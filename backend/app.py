from flask import Flask, request, jsonify, render_template
import yfinance as yf
from flask_cors import CORS
from sentiment_analysis import SentimentAnalysis
from web_scrape import NewsScrapper
import json
from bot import query_rag
import logging

app = Flask(__name__)
CORS(app)


app = Flask(__name__)
CORS(app)


@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question")

    try:
        # Call your query_rag function and get the result
        result = query_rag(question)

        # Return the result as JSON
        return jsonify({"response": result})  # Wrap result in a response object
    except Exception as e:
        # Log the error (you can configure logging as needed)
        logging.error(f"Error processing query: {e}")
        return jsonify({"error": "An error occurred while processing your query."}), 500


@app.route("/api/stock", methods=["GET"])
def stock():
    symbol = request.args.get("symbol", default="AAPL", type=str).upper()
    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        print(quote)  # Debugging output to check fetched data

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
        print("Error fetching data:", e)  # Debugging output for errors
        return jsonify({"error": str(e)}), 500


@app.route("/stock_data/<symbol>")
def stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")  # Get the last 1 month of stock data

    if data.empty:
        return jsonify({"error": "No data found for the symbol provided."})

    prices = data["Close"].to_dict()
    labels = list(prices.keys())
    values = list(prices.values())

    return jsonify({"labels": labels, "values": values})


@app.route("/api/sentiments", methods=["POST"])
def sentiment():
    ticker = request.form.get("ticker")
    news = NewsScrapper(
        "https://finviz.com/quote.ashx?t=", ticker=ticker
    ).run_scrapper()
    with open(r"backend/data/scraped_results.json", "r") as file:
        news = json.load(file)

    all_parsed_results = [item["parsed_result"] for item in news]

    if not all_parsed_results:
        return jsonify({"error": "No data found for sentiment analysis"}), 404

    sentiment = SentimentAnalysis(all_parsed_results).sentiment_analysis()
    print(sentiment)
    return jsonify(sentiment)


@app.route("/api/chatbot", methods=["POST"])
def chatbot():
    data = request.json
    question = data.get("question")

    # Validate input
    if not question:
        return jsonify({"error": "Please provide a question."}), 400

    # Call the query_rag function
    response = query_rag(question)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True)
