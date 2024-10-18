import requests
from bs4 import BeautifulSoup
import time
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from langchain_google_genai import GoogleGenerativeAI

# from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()


class NewsScrapper:
    def __init__(self, url, stock, source):
        self.url = url
        self.source = source
        self.stock = stock

    def get_yahoo(self):
        URL = self.url + self.stock

        print(f"Fetching data from: {URL}")

        # Fetch the page with stock data
        resp_links = requests.get(url=URL)
        if resp_links.status_code != 200:
            print(f"Failed to fetch data from {URL}")
            return

        soup_links = BeautifulSoup(resp_links.text, "html.parser")

        # Make sure to adjust the class to reflect the actual HTML structure
        links = [
            i.get("href")
            for i in soup_links.find_all(
                "a", class_="subtle-link fin-size-small titles noUnderline yf-1e4diqp"
            )
        ]

        # Validate if any links were found
        if not links:
            print("No news links found")
            return

        # Handle relative links
        base_url = "https://finance.yahoo.com"
        links = [link if link.startswith("http") else base_url + link for link in links]

        print(f"Found {len(links)} news articles")

        # Fetch news articles from links
        for news in links:
            time.sleep(0.5)
            # try:
            resp_articles = requests.get(news)
            print(resp_articles.text)
            #     if resp_articles.status_code != 200:
            #         print(f"Failed to fetch article: {news}")
            #         continue

            #     soup_articles_parent = BeautifulSoup(resp_articles.text, "html.parser")
            #     soup_news = soup_articles_parent.find(
            #         "div", class_="body-wrap yf-i23rhs"
            #     )

            #     if soup_news is not None:
            #         article_text = [i.text for i in soup_news.find_all("p")]
            #         print(article_text)
            #     else:
            #         print(f"No article content found for: {news}")

            # except Exception as e:
            #     print(f"Error fetching article {news}: {str(e)}")

    def scrape_website(self, website):
        print("Connecting to Scraping Browser...")
        # SBR_WEBDRIVER = r"backend\chromedriver.exe"

        # sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, "goog", "chrome")
        # with Remote(sbr_connection, options=ChromeOptions()) as driver:
        #     driver.get(website)
        #     print("Waiting captcha to solve...")
        #     solve_res = driver.execute(
        #         "executeCdpCommand",
        #         {
        #             "cmd": "Captcha.waitForSolve",
        #             "params": {"detectTimeout": 10000},
        #         },
        #     )
        #     print("Captcha solve status:", solve_res["value"]["status"])
        #     print("Navigated! Scraping page content...")
        #     html = driver.page_source
        html = requests.get(website)
        return html.text

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
        dom_content = self.scrape_website(self.url)
        body_content = self.extract_body_content(dom_content)
        cleaned_content = self.clean_body_content(body_content)
        split_dom_content = self.split_dom_content(cleaned_content)
        parsed_result = self.parse_with_ollama(
            split_dom_content,
            "Give me any News/Articles/Posts that are contained in this corpus of text",
        )
        print(parsed_result)


if __name__ == "__main__":
    n = NewsScrapper(
        "https://www.moneycontrol.com/news/business/markets/tata-groups-stellar-market-cap-growth-under-ratan-tatas-leadership-from-legacy-to-global-powerhouse-12839268.html",
        "MSFT",
        "bruh",
    )
    n.run_scrapper()
