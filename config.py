import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key'
    TMAI_API_KEY = os.environ.get('TMAI_API_KEY') or 'your-tmai-api-key'
    TMAI_API_BASE_URL = os.environ.get('TMAI_API_BASE_URL') or "https://api.tokenmetrics.com/v1"