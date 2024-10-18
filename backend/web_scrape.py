import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from langchain_google_genai import GoogleGenerativeAI

# from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class NewsScrapper:
    def __init__(self, site, ticker):
        self.site = site
        self.ticker = ticker
        self.url = self.site + self.ticker

    def scrape_links(self):
        dr = webdriver.Chrome()
        dr.get(self.url)
        # resp = requests.get(self.url)
        # print(resp.text)

        soup = BeautifulSoup(dr.page_source, "html.parser")
        # print(soup.find_all("a", class_="tab-link-news"))
        soup_list = [
            link.get("href") for link in soup.find_all("a", class_="tab-link-news")[0]
        ]
        # print(soup_list)
        return soup_list

    def scrape_website(self, url):
        print("Connecting to Scraping Browser...")

        dr = webdriver.Chrome()
        dr.get(self.url)
        return dr.page_source

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

        # Get text or further process the content
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

    def parse_with_ollama(self, dom_chunks, parse_description):
        template = (
            "You are tasked with extracting specific information from the following text content: {dom_content}. "
            "Please follow these instructions carefully: \n\n"
            "1. **Extract Information:** Only extract the information that you think directly matches the provided description: {parse_description}. "
            "2. **Empty Response:** If no information matches the description, return an empty string ('')."
        )

        # model = OllamaLLM(model="llama3.2:3b")
        model = GoogleGenerativeAI(model="gemini-1.5-flash")
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

        for html in scraped_html:
            body_content = self.extract_body_content(html)
            cleaned_content = self.clean_body_content(body_content)
            split_dom_content = self.split_dom_content(cleaned_content)
            parsed_result = self.parse_with_ollama(
                split_dom_content,
                "Give me any News/Articles/Posts that are contained in this corpus of text",
            )
            results.append(parsed_result)
        return results
        # print(parsed_result)


if __name__ == "__main__":
    n = NewsScrapper("https://finviz.com/quote.ashx?t=", "MSFT")
    print(n.run_scrapper())
