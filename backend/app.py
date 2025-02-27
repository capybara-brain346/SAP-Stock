import csv
import os
from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS
from sentiment_analysis import SentimentAnalysis
from newsapi import NewsApiClient  # Import News API Client
import logging
from bot import query_rag
from chromadb import PersistentClient
import time

app = Flask(__name__)
CORS(app)

COLLECTION_NAME = "stock_news"

newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def clean_symbol_for_newsapi(symbol):
    if symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO"):
        return symbol.rsplit(".", 1)[0]  # Remove the extension
    return symbol

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question")

    try:
        result = query_rag(question)
        return jsonify({"response": result})
    except Exception as e:
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your query."}), 500

@app.route("/api/stock", methods=["GET"])
def stock():
    symbol = request.args.get("symbol", default="AAPL", type=str).upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol."}), 400

    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        if "regularMarketOpen" in quote:
            current_price = quote["regularMarketOpen"]
            return jsonify(
                {
                    "symbol": symbol,
                    "currentPrice": current_price,
                    "longName": quote.get("longName", "N/A"),
                    "error": None,
                }
            ), 200
        else:
            return jsonify({"error": "Stock not found or no current price available"}), 404
    except Exception as e:
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
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

    if data.empty:
        return jsonify({"error": "No data found for the symbol provided."})

    prices = data["Close"].to_dict()
    labels = list(prices.keys())
    values = list(prices.values())

    return jsonify({"labels": labels, "values": values})

@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    data = request.json
    symbol = data.get("symbol", "").upper().strip()

    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol for sentiment analysis."}), 400

    newsapi_symbol = clean_symbol_for_newsapi(symbol)  # Remove .NS or .BO for NewsAPI

    try:
        latest_articles = newsapi.get_everything(q=newsapi_symbol, language="en", sort_by="publishedAt", page_size=3)
        latest_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in latest_articles.get("articles", [])
        ]

        relevant_articles = newsapi.get_everything(q=newsapi_symbol, language="en", sort_by="relevancy", page_size=3)
        relevant_news = [
            {"title": article["title"], "description": article.get("description", ""), "url": article["url"]}
            for article in relevant_articles.get("articles", [])
        ]

        combined_news = {article["url"]: article for article in latest_news + relevant_news}.values()
        limited_news = list(combined_news)[:5]

        news_texts = [f"{article['title']} {article['description']}" for article in limited_news]

        sentiment = SentimentAnalysis(news_texts).sentiment_analysis()

        links = [article["url"] for article in limited_news]

        return jsonify(
            {
                "sentiments": sentiment,
                "links": links,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
