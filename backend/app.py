from flask import Flask, request, jsonify
import yfinance as yf
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app) 

@app.route('/api/stock', methods=['GET'])
def stock():
    symbol = request.args.get('symbol', default='AAPL', type=str).upper()  # Ensure the symbol is uppercase
    ticker = yf.Ticker(symbol)

    try:
        quote = ticker.info
        print(quote)  # Debugging output to check fetched data
        
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
        print("Error fetching data:", e)  # Debugging output for errors
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
