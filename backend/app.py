from flask import Flask, request, jsonify, render_template
import yfinance as yf
from flask_cors import CORS  # Import CORS
from sentiment_analysis import SentimentAnalysis
from web_scrape import NewsScrapper

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
    ticker = request.form.get("ticker")
    news = NewsScrapper(
        "https://finviz.com/quote.ashx?t=", ticker=ticker
    ).run_scrapper()
    sentiment = SentimentAnalysis(news).sentiment_analysis()
    return jsonify(sentiment)


if __name__ == "__main__":
    app.run(debug=True)
