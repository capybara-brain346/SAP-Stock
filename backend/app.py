from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS
from sentiment_analysis import SentimentAnalysis
from web_scrape import NewsScrapper
import json
from bot import query_rag
import logging

app = Flask(__name__)
CORS(app)


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
    symbol = request.args.get("symbol", default="AAPL", type=str).upper()
    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        print(quote)

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
            return jsonify(
                {"error": "Stock not found or no current price available"}
            ), 404
    except Exception as e:
        print("Error fetching data:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")

    if data.empty:
        return jsonify({"error": "No data found for the symbol provided."})

    prices = data["Close"].to_dict()
    labels = list(prices.keys())
    values = list(prices.values())

    NewsScrapper(site="https://finviz.com/quote.ashx?t=", ticker=symbol).run_scrapper()

    return jsonify({"labels": labels, "values": values})


@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    try:
        with open(r"backend/data/scraped_results.json", "r") as file:
            news = json.load(file)

        all_parsed_results = [item["parsed_result"] for item in news]

        if not all_parsed_results:
            return jsonify({"error": "No data found for sentiment analysis"}), 404

        sentiment = SentimentAnalysis(all_parsed_results).sentiment_analysis()
        print(sentiment)

        links = [item["link"] for item in news if "link" in item]

        return jsonify(
            {
                "sentiments": sentiment,
                "links": links,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    question = data.get("question")

    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    response = query_rag(question)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
