
# routes/market.py

from flask import Blueprint, jsonify
from config import Config
from datetime import datetime
from app.routes.client import TMAIClient

bp = Blueprint('market', __name__)



@bp.route('/')
def index():
    return "Market API is live"

@bp.route('/market-prediction')
def market_prediction():
    """Aggregate AI predictions and signals into a single perspective"""
    tmai_client = TMAIClient(Config.TMAI_API_KEY)

    try:
        top_tokens = tmai_client.get_top_token(limit=5)

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

            signals = tmai_client.get_trading_signals(token_id, symbol)
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
