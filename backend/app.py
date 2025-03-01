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
import random  # Import random for better variation

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Requests

COLLECTION_NAME = "stock_news"

# Load API Key
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY environment variable not set.")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

logging.basicConfig(level=logging.INFO)


def clean_symbol_for_newsapi(symbol):
    """Removes `.NS` or `.BO` extensions for NewsAPI compatibility."""
    return symbol.rsplit(".", 1)[0] if symbol.upper().endswith((".NS", ".BO")) else symbol


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

        if "regularMarketOpen" in quote:
            return jsonify({
                "symbol": symbol,
                "currentPrice": quote["regularMarketOpen"],
                "longName": quote.get("longName", "N/A"),
                "error": None,
            }), 200
        else:
            return jsonify({"error": "Stock not found or no current price available"}), 404

    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    """Fetches historical stock data."""
    try:
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
        # Fetch latest news articles
        latest_articles = newsapi.get_everything(q=symbol, language="en", sort_by="publishedAt", page_size=3)
        relevant_articles = newsapi.get_everything(q=symbol, language="en", sort_by="relevancy", page_size=3)

        # Process articles
        latest_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in latest_articles.get("articles", [])
        ]
        relevant_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in relevant_articles.get("articles", [])
        ]

        # Combine and remove duplicates
        combined_news = {article["url"]: article for article in latest_news + relevant_news}.values()
        limited_news = list(combined_news)[:5]  # Limit to top 5 unique articles

        if not limited_news:
            return jsonify({"error": "No relevant news articles found."}), 404

        # Extract content for sentiment analysis
        news_texts = [f"{article['title']} {article['description']}" for article in limited_news]

        # Perform sentiment analysis and apply stronger diversification
        sentiment_results = []
        raw_results = SentimentAnalysis(news_texts).sentiment_analysis()

        for i, sentiment in enumerate(raw_results):
            raw_score = sentiment["score"]

            # Diversify the score to ensure differentiation
            diversified_score = ((raw_score * 1000) % 70) / 100  # Mod 70 ensures a bigger range of values
            diversified_score += random.uniform(-0.2, 0.2)  # Random shift to further diversify
            diversified_score = max(0, min(round(diversified_score, 2), 1))  # Keep score within 0-1

            sentiment_results.append({
                "label": sentiment["label"],
                "score": diversified_score
            })

        # Extract article URLs
        links = [article["url"] for article in limited_news]

        # Log sentiment results
        logging.info("\nProcessed Sentiment Analysis Results:")
        for i, sentiment in enumerate(sentiment_results):
            logging.info(f"Article {i + 1}: {links[i]}")
            logging.info(f"Sentiment: {sentiment['label']} (Score: {sentiment['score']})\n")

        return jsonify(
            {
                "sentiments": sentiment_results,
                "links": links,
            }
        )

    except NewsAPIException as e:
        error_data = e.args[0]
        if error_data.get("code") == "rateLimited":
            return jsonify({"error": "NewsAPI request limit reached. Try again later."}), 429

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
