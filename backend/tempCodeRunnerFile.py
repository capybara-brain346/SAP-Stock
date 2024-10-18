<<<<<<< HEAD
query_rag
=======
from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/stock', methods=['GET'])
def get_stock_price():
    symbol = request.args.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol is required'}), 400

    try:
        stock = yf.Ticker(symbol)
        stock_info = stock.info

        # Fetching the regular market price
        if 'regularMarketPrice' in stock_info:
            current_price = stock_info['regularMarketPrice']
            return jsonify({'symbol': symbol, 'price': current_price}), 200
        else:
            return jsonify({'error': 'Stock not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> d7c742f (Fetched prices successfully)
