from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import os
import schedule
import time

# Base URL for Finviz stock news
finviz_url = 'https://finviz.com/quote.ashx?t='
tickers = ['AMZN', 'GOOG', 'DRUG', 'AAPL']
output_directory = "news"
data_retention_minutes = 2  # Retain news data for 2 minutes (for testing)

# Create a directory to store text files if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


def scrape_stock_news():
    """
    Scrapes stock news from Finviz for the given tickers and saves it to text files.
    """
    print("Starting news scraping...")

    for ticker in tickers:
        url = finviz_url + ticker

        # Request the page with custom headers to avoid being blocked
        req = Request(url=url, headers={'user-agent': 'my-app'})
        response = urlopen(req)

        # Parse the HTML content
        html = BeautifulSoup(response, features='html.parser')
        news_table = html.find(id='news-table')

        file_path = f"{output_directory}/{ticker}_news.txt"

        if news_table:
            with open(file_path, 'a') as file:  # 'a' mode for appending new data
                for row in news_table.findAll('tr'):
                    title = row.a.text
                    date_data = row.td.text.split(' ')

                    if len(date_data) == 1:
                        time = date_data[0]
                        date = None  # No date, just time (for recent news)
                    else:
                        date = date_data[0]
                        time = date_data[1]

                    # Prepare the news entry
                    news_entry = f"Date: {date}, Time: {time}, Headline: {title}\n"

                    # Only write the news if it doesn't already exist in the file
                    if news_entry not in open(file_path).read():
                        file.write(news_entry)

    print("News data scraped and saved.")


def remove_old_files():
    """
    Periodically removes text files after a certain interval, independent of their modification or creation time.
    """
    print(f"Deleting all files in the '{output_directory}' folder...")

    for ticker in tickers:
        file_path = f"{output_directory}/{ticker}_news.txt"

        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted: {file_path}")
        else:
            print(f"File {file_path} does not exist.")

    print("Old files cleaned up.")


def run_periodic_scraping():
    """
    Schedule the scraping and cleanup jobs to run at regular intervals.
    """
    # Schedule the scraping every 1 minute (adjust the interval as needed)
    schedule.every(1).minutes.do(scrape_stock_news)

    # Schedule the cleanup to run every 2 minutes (deletes old files)
    schedule.every(2).minutes.do(remove_old_files)

    # Keep the script running to perform scheduled tasks
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage


if __name__ == "__main__":
    # Initial scrape before starting the scheduled one
    scrape_stock_news()

    # Start the periodic scraping and cleanup
    run_periodic_scraping()
