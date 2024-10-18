import requests
from bs4 import BeautifulSoup
import time


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

    def get_finviz(self):
        URL = pass
if __name__ == "__main__":
    n = NewsScrapper("https://finance.yahoo.com/quote/", "MSFT", "bruh")
    n.get_yahoo()
