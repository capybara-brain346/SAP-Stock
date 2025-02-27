import os
import csv
import logging
from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS
from sentiment_analysis import SentimentAnalysis  # Ensure this module correctly processes text
from newsapi import NewsApiClient  # News API for fetching stock-related news

app = Flask(__name__)
CORS(app)

# Load NewsAPI Key
newsapi = NewsApiClient(api_key=os.getenv("NEWS_API_KEY"))

def clean_symbol_for_newsapi(symbol):
    if symbol.upper().endswith(".NS") or symbol.upper().endswith(".BO"):
        return symbol.rsplit(".", 1)[0]  # Remove the extension
    return symbol

# ✅ Route: Get Stock Price
@app.route("/api/stock", methods=["GET"])
def stock():
    symbol = request.args.get("symbol", default="AAPL", type=str).upper().strip()
    
    if not symbol:
        return jsonify({"error": "Please provide a valid stock symbol."}), 400

    try:
        ticker = yf.Ticker(symbol)
        quote = ticker.info

        if "regularMarketPrice" in quote:
            return jsonify({
                "symbol": symbol,
                "currentPrice": quote["regularMarketPrice"],
                "longName": quote.get("longName", "N/A"),
            }), 200
        else:
            return jsonify({"error": "Stock not found"}), 404
    except Exception as e:
        logging.error(f"Error fetching stock data: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ Route: Get Historical Stock Data
@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

    if data.empty:
        return jsonify({"error": "No data found for the symbol provided."})

    prices = data["Close"].to_dict()
    return jsonify({"values": list(prices.values())})

# ✅ Route: Sentiment Analysis for Multiple Stocks
@app.route("/api/sentiment_comparison", methods=["POST"])
def sentiment_comparison():
    data = request.json
    symbols = data.get("symbols", [])

    if not symbols:
        return jsonify({"error": "Please provide at least two stock symbols for comparison."}), 400

    sentiment_results = {}

    for symbol in symbols:
        try:
            newsapi_symbol = clean_symbol_for_newsapi(symbol)  # Remove .NS or .BO for NewsAPI
            
            # Fetch news articles
            articles = newsapi.get_everything(q=newsapi_symbol, language="en", sort_by="relevancy")

            parsed_results = [f"{article['title']} {article['description']}" for article in articles["articles"]]
            links = [article["url"] for article in articles["articles"]]

            # Perform sentiment analysis
            sentiment = SentimentAnalysis(parsed_results).sentiment_analysis()
            print(f"DEBUG: Sentiment Data for {symbol} ->", sentiment)  # 🛠 Debug log

            # Ensure counts are initialized correctly
            sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}

            # ✅ Fix: Properly count sentiment labels
            for s in sentiment:
                label = s.get("label", "").lower()  # Ensure lowercase match
                if label == "positive":
                    sentiment_counts["positive"] += 1
                elif label == "neutral":
                    sentiment_counts["neutral"] += 1
                elif label == "negative":
                    sentiment_counts["negative"] += 1

            sentiment_results[symbol] = {"sentiment_counts": sentiment_counts, "links": links[:5]}

        except Exception as e:
            sentiment_results[symbol] = {"error": str(e)}

    print("DEBUG: Final Sentiment Results ->", sentiment_results)  # 🛠 Debug log
    return jsonify(sentiment_results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)