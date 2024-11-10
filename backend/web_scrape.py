import csv
import os
import queue
from bs4 import BeautifulSoup
from selenium import webdriver
import json
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
# from langchain_google_genai import GoogleGenerativeAI

load_dotenv()

# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class NewsScrapper:
    def __init__(self, site, ticker) -> None:
        self.site = site
        self.ticker = ticker
        self.url = self.site + self.ticker
        self.queue = queue.Queue(maxsize=5)
        self.driver = webdriver.Chrome()

    def scrape_links(self) -> None:
        self.driver.get(self.url)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")

        links = soup.find_all("a", class_="WwrzSb")

        for link in links:
            self.queue.put(link.get("href"))
        print("Scraped Links: ", self.queue)

    def scrape_website(self, url):
        print("Connecting to Scraping Browser...")
        print("Scraping for: ", url)
        self.driver.get(url)
        return self.driver.page_source

    def extract_body_content(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        body_content = soup.body
        if body_content:
            return str(body_content)
        return ""

    def clean_body_content(self, body_content):
        soup = BeautifulSoup(body_content, "html.parser")

        for script_or_style in soup(["script", "style"]):
            script_or_style.extract()

        cleaned_content = soup.get_text(separator="\n")
        cleaned_content = "\n".join(
            line.strip() for line in cleaned_content.splitlines() if line.strip()
        )

        return cleaned_content

    def split_dom_content(self, dom_content, max_length=6000):
        return [
            dom_content[i : i + max_length]
            for i in range(0, len(dom_content), max_length)
        ]

    def parse_with_model(self, dom_chunks, parse_description):
        template = (
            "You are tasked with extracting specific information from the following text content: {dom_content}. "
            "Please follow these instructions carefully: \n\n"
            "1. **Extract Information:** Only extract the information that you think directly matches the provided description: {parse_description}. "
            "2. **Empty Response:** If no information matches the description, return an empty string ('')."
        )

        print("Using Gemini API for parsing...")

        # model = GoogleGenerativeAI(model="gemini-1.5-flash", api_key=GEMINI_API_KEY)
        model = OllamaLLM(model="llama3.2:3b")
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
        self.scrape_links()

        with open("scraped_text.csv", "w") as file:
            writer = csv.writer(file, delimiter="|.|")
            while not self.queue.empty():
                link = self.queue.get()
                dom_content = self.scrape_website(link)
                writer.writerow(link, dom_content)


        for i, html in enumerate(scraped_html):
            body_content = self.extract_body_content(html)
            cleaned_content = self.clean_body_content(body_content)
            split_dom_content = self.split_dom_content(cleaned_content)
            parsed_result = self.parse_with_model(
                split_dom_content,
                "Give me any News/Articles/Posts that are contained in this corpus of text",
            )
            results.append({"link": links[i], "parsed_result": parsed_result})

        with open(r"backend\data\scraped_results.json", "w") as json_file:
            json.dump(results, json_file, indent=4)

        self.driver.close()

        return results


if __name__ == "__main__":
    n = NewsScrapper("https://finviz.com/quote.ashx?t=", "AAPL")
    print(n.run_scrapper())
