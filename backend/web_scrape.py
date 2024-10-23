import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class NewsScrapper:
    def __init__(self, site, ticker):
        self.site = site
        self.ticker = ticker
        self.url = self.site + self.ticker
        chrome_options = Options()
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument("--allow-insecure-localhost")
        self.driver = webdriver.Chrome()

    def scrape_links(self):
        self.driver.get(self.url)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        links = soup.find_all("a", class_="tab-link-news")

        soup_list = [link.get("href") for link in links]
        # print(soup_list)

        return soup_list[0:2]

    def scrape_website(self, url):
        print("Connecting to Scraping Browser...")
        print("Scraping for: ", url)
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "div"))
            )
        except Exception as e:
            print(f"Error waiting for content: {e}")
        finally:
            html = self.driver.page_source

            soup = BeautifulSoup(html, "html.parser")
            body_content = soup.body
            if body_content:
                return " ".join([p.get_text() for p in body_content.find_all("p")])
            return ""

    # def extract_body_content(self, html_content):
    #     soup = BeautifulSoup(html_content, "html.parser")
    #     body_content = soup.body
    #     if body_content:
    #         return " ".join([p.get_text() for p in body_content.find_all("p")])
    #     return ""

    def clean_body_content(self, body_content):
        print(body_content)
        soup = BeautifulSoup(body_content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = " ".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content

    def split_dom_content(self, dom_content, max_length=6000):
        return [
            dom_content[i : i + max_length]
            for i in range(0, len(dom_content), max_length)
        ]

    def parse_with_ollama(self, dom_chunks, parse_description):
        template = (
            "You are assigned to extract specific information from the provided text content: {dom_content}. "
            "Please adhere to the following instructions: \n\n"
            "1. **Extract Relevant Information:** Identify and extract only the information that directly corresponds to the description given: {parse_description}. "
            "2. **Return an Empty Response if No Matches:** If no information aligns with the provided description, respond with an empty string ('').\n\n"
            "Please ensure that your extraction is accurate and concise, focusing solely on the relevant details."
        )

        model = OllamaLLM(model="llama3.2:3b")
        # model = GoogleGenerativeAI(model="gemini-1.5-flash")
        prompt = ChatPromptTemplate.from_template(template)
        chain = prompt | model

        parsed_results = []

        for i, chunk in enumerate(dom_chunks, start=1):
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            print(f"Parsed batch: {i} of {len(dom_chunks)}")
            parsed_results.append(response)

        return " ".join(parsed_results)

    def run_scrapper(self):
        results = []

        scraped_html = []
        links = self.scrape_links()

        for link in links:
            dom_content = self.scrape_website(link)
            scraped_html.append(dom_content)

        for i, html in enumerate(scraped_html):
            # body_content = self.extract_body_content(html)
            cleaned_content = self.clean_body_content(html)
            split_dom_content = self.split_dom_content(cleaned_content)
            parsed_result = self.parse_with_ollama(
                split_dom_content,
                "Give me any News/Articles/Posts that are contained in this corpus of text",
            )
            results.append({"link": links[i], "parsed_result": parsed_result})

        with open(r"backend\data\scraped_results.json", "w") as json_file:
            json.dump(results, json_file, indent=4)

        self.driver.close()

        return results


if __name__ == "__main__":
    n = NewsScrapper("https://finviz.com/quote.ashx?t=", "MSFT")
    print(n.run_scrapper())
