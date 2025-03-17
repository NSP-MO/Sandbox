import ccxt
import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime

# Initialize OKX API with environment variables
api_key = "4c1029f9-6317-4c87-903f-3923f56de4d1"
api_secret = "B565C60ED402A2EA0DD41167F60E8CD6"
passphrase = input("Please enter your OKX API passphrase: ")

exchange = ccxt.okx({
    'apiKey': api_key,
    'secret': api_secret,
    'password': passphrase,
})

# Fetch Market Data (Candles)
def fetch_candles(symbol, interval, limit=300):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": symbol, "bar": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        data = response.json()

        if 'data' not in data or not data['data']:
            print(f"Error: No candle data retrieved for {symbol}")
            return pd.DataFrame()

        candles = pd.DataFrame(data['data'], columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'currency', 'timestamp_end', 'market_type'
        ])
        
        candles['timestamp'] = pd.to_datetime(pd.to_numeric(candles['timestamp']), unit='ms')
        candles[['open', 'high', 'low', 'close']] = candles[['open', 'high', 'low', 'close']].astype(float)


        
        
        