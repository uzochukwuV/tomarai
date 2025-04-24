# client.py

import requests
import time
from datetime import datetime, timedelta
from config import Config

class TMAIClient:
    def __init__(self, api_key):
        self.base_url = Config.TMAI_API_BASE_URL
        self.api_key = api_key
        self.headers = {
            "accept": "application/json",
            "api_key": self.api_key
        }

    def get_ohlcv_data(self, token_id, symbol, token_name, days=3):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        params = {
            'token_id': token_id,
            'symbol': symbol,
            'token_name': token_name,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'limit': min(days, 100),
            'page': 0
        }
        response = requests.get(f"{self.base_url}/daily-ohlcv", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_tokens(self, limit=10):
        params = {'limit': limit, 'sort': 'market_cap', 'order': 'desc'}
        response = requests.get(f"{self.base_url}/tokens", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_top_tokens(self, limit=10,page=0):
        print(f"Limit: {limit}, Page: {page}")
        params = {'top_k': limit, 'page': page}
        response = requests.get(f"{self.base_url}/top-market-cap-tokens", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def ask_ai(self, question):
      
        payload = { "messages": [{ "user": question }] }
        response = requests.post(f"{self.base_url}/tmai", headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def get_trader_indices(self, params=None):
        response = requests.get(f"{self.base_url}/trader-indices", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_market_metrics(self):
        response = requests.get(f"{self.base_url}/market-metrics", headers=self.headers, params={'limit': 10, 'page': 0})
        response.raise_for_status()
        return response.json()

    def get_trading_signals(
            self,
            token_id=None,
            symbol=None,
            start_date=None,
            end_date=None,
            category=None,
            exchange=None,
            marketcap=None,
            volume=None,
            fdv=None,
            signal=None,
            limit=50,
            page=0
        ):
        print(token_id, symbol)
        try:
            params = {
                "token_id": "3375,3306",
                "startDate": (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d'),
                "endDate": datetime.now().strftime('%Y-%m-%d'),
                "symbol": "BTC,ETH",
                "category": "layer-1,nft",
                "exchange": "binance,gate",
                "marketcap": 100000000,
                "volume": 100000000,
                "fdv": 100000000,
                "signal": 1,
                "limit": limit,
                "page": page
            }
            print(params)
            if token_id:
                print(f"Token ID: {token_id}")
                params['token_id'] = token_id
            if symbol:
                print(f"Symbol: {symbol}")
                params['symbol'] = symbol
            if start_date:
                params['startDate'] = start_date
            if end_date:
                params['endDate'] = end_date
            if category:
                params['category'] = category
            if exchange:
                params['exchange'] = exchange
            if marketcap:
                params['marketcap'] = marketcap
            if volume:
                params['volume'] = volume
            if fdv:
                params['fdv'] = fdv
            if signal is not None:
                params['signal'] = signal
            print(f"Params: {params}")
            response = requests.get(f"{self.base_url}/trading-signals", headers=self.headers, params=params)
            print(f"Response: {response}")
            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"Error: {e}")



    def get_sentiment(self, token_id, symbol):
        params = {'limit': "10", 'page': 0}
        response = requests.get(f"{self.base_url}/sentiments", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_resistance_support(self, token_id, symbol):
        params = {'token_id': token_id, 'symbol': symbol}
        response = requests.get(f"{self.base_url}/resistance-support", headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()

    def get_market_metrics(self):
        response = requests.get(f"{self.base_url}/market-metrics", headers=self.headers)
        response.raise_for_status()
        return response.json()

class RateLimitedTMAIClient(TMAIClient):
    def __init__(self, api_key, requests_per_minute=60):
        super().__init__(api_key)
        self.requests_per_minute = requests_per_minute
        self.request_timestamps = []

    def _check_rate_limit(self):
        now = time.time()
        self.request_timestamps = [ts for ts in self.request_timestamps if now - ts < 60]
        if len(self.request_timestamps) >= self.requests_per_minute:
            time.sleep(60 - (now - self.request_timestamps[0]))
        self.request_timestamps.append(time.time())

    def get_ohlcv_data(self, token_id, symbol, token_name, days=30):
        self._check_rate_limit()
        return super().get_ohlcv_data(token_id, symbol, token_name, days)
