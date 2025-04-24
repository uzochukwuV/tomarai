# utils/ohlcv.py

import pandas as pd

def process_ohlcv_data(api_response):
    """Process OHLCV data and calculate indicators like moving averages and volatility"""
    df = pd.DataFrame(api_response['data'])

    # Rename for consistency if needed
    df.rename(columns={
        'timestamp': 'date',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'volume': 'volume'
    }, inplace=True)

    # Convert date to datetime format and set as index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Moving averages
    df['ma_7'] = df['close'].rolling(window=7).mean()
    df['ma_30'] = df['close'].rolling(window=30).mean()

    # Volatility (Standard deviation over 14 days)
    df['volatility'] = df['close'].rolling(window=14).std()

    # Price momentum (7-day % change)
    df['momentum'] = df['close'].pct_change(periods=7) * 100

    return df.reset_index()
