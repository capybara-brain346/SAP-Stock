from flask import Flask, request, jsonify, render_template
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stock', methods=['GET'])
def stock():
    symbol = request.args.get('symbol', default='AAPL', type=str).upper()
    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        if 'regularMarketOpen' in quote:
            current_price = quote['regularMarketOpen']
            return jsonify({
                'symbol': symbol,
                'currentPrice': current_price,
                'longName': quote.get('longName', 'N/A'),
                'error': None
            }), 200
        else:
            return jsonify({'error': 'Stock not found or no current price available'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stock_data/<symbol>')
def stock_data(symbol):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1mo")  # Get the last 1 month of stock data

    if data.empty:
        return jsonify({'error': 'No data found for the symbol provided.'})

    prices = data['Close'].to_dict()
    labels = list(prices.keys())
    values = list(prices.values())

    return jsonify({'labels': labels, 'values': values})

if __name__ == '__main__':
    app.run(debug=True)
