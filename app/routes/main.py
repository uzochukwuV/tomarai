from flask import Blueprint, render_template
import requests
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from config import Config

bp = Blueprint('main', __name__)

class TMAIClient:
    def __init__(self, api_key):
        self.base_url = "https://api.tokenmetrics.com/v2"
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    def get_eth_data(self, days=30):
        """Get ETH historical data"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        params = {
            'token_id': '3306',  # ETH token ID
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'interval': '1d'
        }
        
        response = requests.get(
            f"{self.base_url}/daily-ohlcv",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def get_top_tokens(self, limit=10):
        """Get top tokens by market cap"""
        params = {'limit': limit, 'sort': 'market_cap', 'order': 'desc'}
        response = requests.get(
            f"{self.base_url}tokens",
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

@bp.route('/')
@bp.route('/dashboard')
def dashboard():
    tmai_client = TMAIClient(Config.TMAI_API_KEY)
    
    try:
        # Get real data from TMAI API
        eth_data = process_eth_data(tmai_client.get_eth_data())
        portfolio_data = process_portfolio_data(tmai_client.get_top_tokens())
        
        # Create charts
        eth_chart = create_eth_chart(eth_data)
        portfolio_chart = create_portfolio_chart(portfolio_data)
        
        return render_template('dashboard.html', 
                            eth_chart=eth_chart,
                            portfolio_chart=portfolio_chart)
    
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error=str(e))

def process_eth_data(api_data):
    """Process ETH data from TMAI API"""
    df = pd.DataFrame(api_data['data'])
    df['DATE'] = pd.to_datetime(df['DATE'])
    df['30_day_high'] = df['CLOSE'].rolling(30).max()
    return df.rename(columns={
        'DATE': 'date',
        'CLOSE': 'price'
    })

def process_portfolio_data(api_data):
    """Process portfolio data from TMAI API"""
    tokens = api_data['data'][:5]  # Get top 5 tokens
    total_mcap = sum(float(token['market_cap']) for token in tokens)
    
    portfolio = []
    for token in tokens:
        portfolio.append({
            'token': token['symbol'],
            'weight': float(token['market_cap']) / total_mcap,
            'performance': float(token['price_change_24h'])
        })
    
    return pd.DataFrame(portfolio)

def create_eth_chart(df):
    """Create ETH breakout chart"""
    fig = px.line(df, x='date', y=['price', '30_day_high'],
                 title='ETH Price vs 30-Day High',
                 labels={'value': 'Price (USD)', 'variable': 'Metric'})
    fig.update_layout(legend_title_text='Metric')
    return fig.to_html(full_html=False)

def create_portfolio_chart(df):
    """Create portfolio composition pie chart"""
    fig = px.pie(df, values='weight', names='token',
                title='Market Cap Weighted Portfolio',
                hover_data=['performance'])
    return fig.to_html(full_html=False)