from flask import Blueprint, Flask
from flask_cors import CORS
from config import Config
from flask_socketio import SocketIO, emit
from app.routes.socket import register_market_socket_handlers
from app.routes.client import TMAIClient
import os

socket_bp = Blueprint('socket', __name__)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    socketio = SocketIO(app, cors_allowed_origins="*")
    CORS(app)

    from app.routes.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    from app.routes.market import bp as market_bp
    app.register_blueprint(market_bp)  # Already prefixed with /api

    
    app.register_blueprint(socket_bp, url_prefix='/')
    register_market_socket_handlers(socketio, TMAIClient(os.environ.get("TMAI_API_KEY")))
    return app , socketio
