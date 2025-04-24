# market_socket.py
from flask_socketio import SocketIO, emit, disconnect
from threading import Thread
from flask import request
import uuid

import random
import datetime
import json
from typing import Dict, List, Any, Union

# Dictionary to store ongoing tasks
ongoing_tasks = {}

def register_market_socket_handlers(socketio: SocketIO, tmai_client):
    @socketio.on('connect')
    def handle_connect():
        print('Client connected')
        # Don't emit a 'connect' event as Socket.IO already handles this
        emit('connection_established', {'message': 'Connected to WebSocket'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print('Client disconnected')

    @socketio.on('error')
    def handle_error(error):
        print('Socket error:', error)
    

    # hello


    # @socketio.on('get_market_prediction')
    # def handle_market_prediction():
    #     print('Starting market prediction process')
    #     try:
    #         # Generate a unique task ID (you might want to use user session ID)
    #         task_id = str(uuid.uuid4())
            
    #         # Start background task
    #         print(request.namespace.socket.sessid)
    #         thread = Thread(target=process_market_data, args=(task_id, request.namespace.socket.sessid))
    #         thread.daemon = True
    #         thread.start()
            
    #         # Send acknowledgment with task ID
    #         emit('market_prediction_started', {"task_id": task_id})
            
    #     except Exception as e:
    #         emit('error', {'message': 'Failed to start market prediction', 'error': str(e)})

    # def process_market_data(task_id, sid):
    #     try:
    #         print('Fetching top tokens')
    #         top_tokens = tmai_client.get_top_tokens(limit=5)
            
    #         if not top_tokens.get("success", False):
    #             socketio.emit('error', {'message': 'Could not retrieve top tokens'}, room=sid)
    #             return
                
    #         tokens = top_tokens.get("data", [])
    #         prediction_data = []
            
    #         # Process each token
    #         for i, token in enumerate(tokens):
    #             token_id = token['TOKEN_ID']
    #             symbol = token['TOKEN_SYMBOL']
    #             signals = tmai_client.get_trading_signals(token_id, symbol)
                
    #             token_data = {
    #                 'token_id': token_id,
    #                 'symbol': symbol,
    #                 'signals': signals
    #             }
    #             prediction_data.append(token_data)
                
    #             # Send progress update
    #             socketio.emit('market_prediction_progress', {
    #                 "task_id": task_id,
    #                 "progress": i + 1,
    #                 "total": len(tokens),
    #                 "current_token": symbol
    #             }, room=sid)
            
    #         # Send complete data
    #         socketio.emit('market_prediction', {"data": prediction_data}, room=sid)
        
    #     except Exception as e:
    #         socketio.emit('error', {'message': 'Failed during processing', 'error': str(e)}, room=sid)
    #     # hello

    @socketio.on('get_market_prediction')
    def handle_market_prediction():
        print('Fetching market prediction')
        try:
            print('Fetching top tokens')
            top_tokens = tmai_client.get_top_tokens(limit=5)
            print('Top tokens fetched')
            if not top_tokens.get("success", False):
                emit('error', {'message': 'Could not retrieve top tokens'})
                return
           
            tokens = top_tokens.get("data", [])
            
            prediction_data = []
            
            token= tokens[0]
            token_ids = []
            symbols = []
            
            for token in tokens:
                token_ids.append(str(token['TOKEN_ID']))
                symbols.append(str(token['TOKEN_SYMBOL']))
        
            # Use join instead of string concatenation
            token_id_str = ",".join(token_ids)
            symbol_str = ",".join(symbols)
                
         
            # Remove the first character (comma) from symbol string
            
           
            signals = tmai_client.get_trading_signals(token_id_str, symbol_str)
                    
            prediction_data.append({
                        'token_id': token_ids,
                        'symbol': symbols,
                        'signals': signals
                    })
            emit('market_prediction', {"data": analyze_crypto_signals(prediction_data)})
            
            
        except Exception as e:
            emit('error', {'message': 'Failed to fetch market prediction', 'error': str(e)})

    @socketio.on('get_trading_signals')
    def handle_trading_signals(data):
        print('Fetching trading signals')
        print(data, "  ",data["token_id"])
        try:
            print(data["token_id"])
            token_id = data.get('token_id')
            symbol = data.get('symbol')
            print(token_id, symbol)
            signals = tmai_client.get_trading_signals()
            print('Signals:')
            emit('trading_signals', signals)
        except Exception as e:
            emit('error', {'message': 'Failed to fetch trading signals', 'error': str(e)})

    @socketio.on('get_market_metrics')
    def handle_market_metrics():
        print('Fetching market metrics')
         # Assuming you have a method to get market metrics in your TMAIClient
         # If not, you need to implement it in the TMAIClient class


        try:
            metrics = tmai_client.get_market_metrics()  # Make sure this exists
            print("metrics")
            emit('market_metrics', metrics)
        except Exception as e:
            emit('error', {'message': 'Failed to fetch market metrics', 'error': str(e)})



def analyze_crypto_signals(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyzes cryptocurrency trading signals and returns structured analysis data.
    
    Args:
        data: A dictionary containing cryptocurrency signals data
        
    Returns:
        Dictionary with market direction, timestamp, and token analysis
    """
    # Extract signals data from the input structure
    try:
        signals = data[0]['signals']['data']
    except (KeyError, IndexError, TypeError):
        return {"error": "Invalid data structure"}
    
    # Count bullish vs bearish signals to determine market direction
    bullish_count = sum(1 for signal in signals if signal.get('TRADING_SIGNAL') == 1)
    bearish_count = len(signals) - bullish_count
    
    # Determine overall market direction
    market_direction = 'bullish' if bullish_count > bearish_count else 'bearish'
    
    # Get current timestamp
    timestamp = datetime.datetime.now().isoformat()
    
    # Select top 5 tokens based on some criteria (here we'll use recency)
    # Sort signals by date, most recent first
    sorted_signals = sorted(signals, key=lambda x: x.get('DATE', ''), reverse=True)
    top_tokens = sorted_signals[:5]  # Take top 5
    
    # Generate token analysis data
    tokens = []
    for token in top_tokens:
        token_data = {
            'combined_score': round(random.random(), 3),  # Random score between 0-1
            'symbol': token.get('TOKEN_SYMBOL', ''),
            'token_id': token.get('TOKEN_ID', 0),
            'token_trend': 1 if token.get('TRADING_SIGNAL') == 1 else -1,
            'confidence': random.randint(50, 95)  # Random confidence between 50-95
        }
        tokens.append(token_data)
    
    # Construct the final result
    result = {
        'market_direction': market_direction,
        'timestamp': timestamp,
        'tokens': tokens
    }
    
    return result

