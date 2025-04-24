# api.py

from flask import Blueprint, jsonify
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from config import Config
from .client import *
from datetime import datetime
from app.routes.client import *
from app.routes.client import *
from app.routes.utils.ohlcv import *
import os
bp = Blueprint('api', __name__)
from flask import request

# ... Existing routes remain here (ohlcv_data, portfolio)



@bp.route('/trading-signals', methods=['GET'])
def get_trading_signals():
    # Parameters (you can make these dynamic with `request.args.get(...)`)
    url = "https://api.tokenmetrics.com/v2/trading-signals"
    params = {
        "token_id": "3375,3306",
        "startDate": "2023-10-01",
        "endDate": "2023-10-10",
        "symbol": "BTC,ETH",
        "category": "layer-1,nft",
        "exchange": "binance,gate",
        "marketcap": 100000000,
        "volume": 100000000,
        "fdv": 100000000,
        "signal": 1,
        "limit": 10,
        "page": 0
    }

    headers = {
        "accept": "application/json",
        "api_key": os.environ.get("TMAI_API_KEY")
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        if data.get("success"):
            return jsonify(data["data"])
        return jsonify({"error": data.get("message", "Unknown error")}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@bp.route('/token-analysis/<token_id>/<symbol>/<name>')
def token_analysis(token_id, symbol, name):
    tmai_client = TMAIClient(Config.TMAI_API_KEY)

    try:
        with ThreadPoolExecutor(max_workers=4) as executor:
            ohlcv_future = executor.submit(tmai_client.get_ohlcv_data, token_id, symbol, name)
            sentiment_future = executor.submit(tmai_client.get_sentiment, token_id, symbol)
            signals_future = executor.submit(tmai_client.get_trading_signals, token_id, symbol)
            support_resistance_future = executor.submit(tmai_client.get_resistance_support, token_id, symbol)

        ohlcv_response = ohlcv_future.result()
        sentiment_response = sentiment_future.result()
        signals_response = signals_future.result()
        support_resistance_response = support_resistance_future.result()

        ohlcv_data = process_ohlcv_data(ohlcv_response) if ohlcv_response.get('success') else None

        return jsonify({
            'status': 'success',
            'token_id': token_id,
            'symbol': symbol,
            'price_data': ohlcv_data.to_dict('records') if ohlcv_data is not None else None,
            'sentiment': sentiment_response.get('data'),
            'trading_signals': signals_response.get('data'),
            'support_resistance': support_resistance_response.get('data')
        })

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@bp.route('/trader-indices/<days>')
def trader_indices(days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=int(days))
    days = int(days)
    print(f"Start Date: {start_date}, End Date: {end_date}")
    try:
        print(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), min(days, 100))
        # Ensure days is an integer and within a reasonable range
        params ={
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'limit': 100,
            'page': 0
        }
        print(f"Params: {params}")
        tmai_client = TMAIClient(Config.TMAI_API_KEY)
        data = tmai_client.get_trader_indices(params=params)
        return jsonify({'status': 'success', 'data': data.get('data')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@bp.route('/market-metrics')
def market_metrics():
    try:
        tmai_client = TMAIClient(Config.TMAI_API_KEY)
        data = tmai_client.get_market_metrics()
        return jsonify({'status': 'success', 'data': data.get('data')})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@bp.route('/')
def index():
    return "Market API is live"

@bp.route('/market-prediction')
def market_prediction():
    """Aggregate AI predictions and signals into a single perspective"""
    tmai_client = TMAIClient(Config.TMAI_API_KEY)

    # Extract optional query parameters
    start_date = "2023-10-01"
    end_date = "2023-10-10"
    category = "layer-1,nft"
    exchange = "binance,gate"
    marketcap = "100000000"
    volume = "100000000"
    fdv = "100000000"
    signal = "1"
    limit = 1000
    page = 0

    try:
        top_tokens = tmai_client.get_top_tokens(limit=5)

        if not top_tokens.get('success', False):
            return jsonify({
                'status': 'error',
                'message': 'Could not retrieve top tokens'
            }), 400

        tokens = top_tokens['data']
        predictions = []

        for token in tokens:
            token_id = token['TOKEN_ID']
            symbol = token['TOKEN_SYMBOL']

            signals = tmai_client.get_trading_signals(
                token_id=token_id,
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
                category=category,
                exchange=exchange,
                marketcap=marketcap,
                volume=volume,
                fdv=fdv,
                signal=signal,
                limit=limit,
                page=page
            )
            sentiment = tmai_client.get_sentiment(token_id, symbol)

            if signals.get('success', False) and sentiment.get('success', False):
                predictions.append({
                    'token_id': token_id,
                    'symbol': symbol,
                    'name': token['TOKEN_NAME'],
                    'signals': signals['data'],
                    'sentiment': sentiment['data'],
                    'combined_score': calculate_prediction_score(signals['data'], sentiment['data'])
                })

        return jsonify({
            'status': 'success',
            'market_prediction': {
                'timestamp': datetime.now().isoformat(),
                'tokens': predictions,
                'market_direction': determine_market_direction(predictions)
            }
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500



@bp.route('/ask-tmai', methods=['GET'])
def ask_tmai():
    """Ask a question to Token Metrics AI"""
    q= request.args.get('q', 'What is the price of Bitcoin?')
    print(q)
    tmai_client = TMAIClient(Config.TMAI_API_KEY)
    

    try:
        data = tmai_client.ask_ai(q)
        return data

    except requests.exceptions.RequestException as e:
        return jsonify({
            "status": "error",
            "message": "Failed to communicate with Token Metrics AI",
            "details": str(e)
        }), 500


def calculate_prediction_score(signals, sentiment):
    """Calculate a combined prediction score based on signals and sentiment"""
    # Placeholder - implement logic based on signal/sentiment structure
    return 0.5


def determine_market_direction(predictions):
    """Determine overall market direction based on token predictions"""
    if not predictions:
        return "neutral"

    avg_score = sum(p['combined_score'] for p in predictions) / len(predictions)

    if avg_score > 0.3:
        return "bullish"
    elif avg_score < -0.3:
        return "bearish"
    else:
        return "neutral"
