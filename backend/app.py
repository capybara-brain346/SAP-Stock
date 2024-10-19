from flask import Flask, request, jsonify, render_template
import yfinance as yf
from flask_cors import CORS  # Import CORS
from sentiment_analysis import SentimentAnalysis
from web_scrape import NewsScrapper
import json

app = Flask(__name__)
CORS(app)


@app.route("/api/stock", methods=["GET"])
def stock():
    symbol = request.args.get(
        "symbol", default="AAPL", type=str
    ).upper()  # Ensure the symbol is uppercase
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
    with open(r"backend/data/scraped_results.json", "r") as file:
        news = json.load(file)

    all_parsed_results = [item["parsed_result"] for item in news]

    if not all_parsed_results:
        return jsonify({"error": "No data found for sentiment analysis"}), 404

    sentiment = SentimentAnalysis(all_parsed_results).sentiment_analysis()
    print(sentiment)
    return jsonify(sentiment)


if __name__ == "__main__":
    app.run(debug=True)
