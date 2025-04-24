# utils/market.py

import pandas as pd

def aggregate_market_metrics(api_response): 
    """Process and aggregate market metrics data"""
    df = pd.DataFrame(api_response['data'])

    df['date'] = pd.to_datetime(df['DATE'])
    df.set_index('date', inplace=True)

    df['7d_avg'] = df['VALUE'].rolling(7).mean()
    df['30d_avg'] = df['VALUE'].rolling(30).mean()
    df['momentum'] = df['VALUE'].pct_change(7) * 100
    df['rolling_max'] = df['VALUE'].rolling(14).max()
    df['rolling_min'] = df['VALUE'].rolling(14).min()

    return df.reset_index()