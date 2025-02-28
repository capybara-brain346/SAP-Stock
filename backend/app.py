import csv
import os
import time
import logging
import yfinance as yf
from flask import Flask, request, jsonify
from flask_cors import CORS
from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException
from sentiment_analysis import SentimentAnalysis
from bot import query_rag
from chromadb import PersistentClient
from bot import query_rag

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

COLLECTION_NAME = "stock_news"

# Load API Key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable not set.")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)


def clean_symbol_for_newsapi(symbol):
    """Removes `.NS` or `.BO` extensions for NewsAPI compatibility."""
    return symbol.rsplit(".", 1)[0] if symbol.upper().endswith((".NS", ".BO")) else symbol

def clean_symbol_for_newsapi(symbol):
    if symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO"):
        return symbol.rsplit(".", 1)[0]  # Remove the extension
    return symbol

@app.route("/query", methods=["POST"])
def query():
    """Handles chatbot queries."""
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    try:
        result = query_rag(question)
        return jsonify({"response": result})
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your query."}), 500

@app.route("/api/stock", methods=["GET"])
def stock():
    """Fetches stock data from Yahoo Finance."""
    symbol = request.args.get("symbol", default="AAPL", type=str).upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol."}), 400

    try:
        ticker = yf.Ticker(symbol)
        quote = ticker.info
        print(quote)

        if "regularMarketOpen" in quote:
            return jsonify({
                "symbol": symbol,
                "currentPrice": quote["regularMarketOpen"],
                "longName": quote.get("longName", "N/A"),
                "error": None,
            }), 200
        else:
            return jsonify(
                {"error": "Stock not found or no current price available"}
            ), 404
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": str(e)}), 500


def delete_chroma_collection():
    try:
        chroma_client = PersistentClient(path="chroma_stock")
        chroma_client.delete_collection(COLLECTION_NAME)
        print(f"Collection {COLLECTION_NAME} deleted successfully.")
    except Exception as e:
        raise Exception(f"Unable to delete collection: {e}")


@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    # Attempt to delete the Chroma database with retry logic
    #  retries = 5
    #   for attempt in range(retries):
    #       try:
    #            delete_chroma_collection()  # Attempt to delete the collection
    #           break  # Exit loop if successful
    #       except Exception as e:
    #           print(f"Attempt {attempt + 1}: {e}")
    #          time.sleep(1)  # Wait before retrying

    # Fetch stock data
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

        if data.empty:
            return jsonify({"error": "No data found for the symbol provided."}), 404

        prices = data["Close"].to_dict()
        labels = list(prices.keys())
        values = list(prices.values())

        return jsonify({"labels": labels, "values": values})
    except Exception as e:
        logging.error(f"Error fetching stock history: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    """Fetches news and performs sentiment analysis."""
    data = request.json
    symbol = data.get("symbol", "").upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol for sentiment analysis."}), 400

    try:
        # Fetch top 3 latest news articles
        latest_articles = newsapi.get_everything(q=symbol, language="en", sort_by="publishedAt", page_size=3)
        latest_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in latest_articles.get("articles", [])
        ]

        # Fetch top 3 most relevant news articles
        relevant_articles = newsapi.get_everything(q=symbol, language="en", sort_by="relevancy", page_size=3)
        relevant_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in relevant_articles.get("articles", [])
        ]

        # Combine and remove duplicates
        combined_news = {article["url"]: article for article in latest_news + relevant_news}.values()
        limited_news = list(combined_news)[:5]  # Limit to top 5 unique articles

        # Extract content for sentiment analysis
        news_texts = [f"{article['title']} {article['description']}" for article in limited_news]

        # Perform sentiment analysis
        sentiment = SentimentAnalysis(news_texts).sentiment_analysis()

        # Extract article URLs
        links = [article["url"] for article in limited_news]

        return jsonify(
            {
                "sentiments": sentiment,  # Sentiment results
                "links": links,  # News links
            }
        )

    except Exception as e:
        logging.error(f"Error in sentiment analysis: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    """Handles chatbot interactions."""
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    try:
        response = query_rag(question)
        return jsonify({"response": response})
    except Exception as e:
        logging.error(f"Error in chatbot response: {e}")
        return jsonify({"error": "An error occurred while processing your request."}), 500


def delete_chroma_collection():
    """Deletes ChromaDB collection if needed."""
    try:
        chroma_client = PersistentClient(path="chroma_stock")
        chroma_client.delete_collection(COLLECTION_NAME)
        logging.info(f"Collection {COLLECTION_NAME} deleted successfully.")
    except Exception as e:
        logging.error(f"Unable to delete collection: {e}")
        raise Exception(f"Unable to delete collection: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
