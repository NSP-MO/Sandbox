import os
import ccxt
import requests
import time
import numpy as np
import pandas as pd
from datetime import datetime

# Initialize OKX API with environment variables
api_key = "4c1029f9-6317-4c87-903f-3923f56de4d1"
api_secret = "B565C60ED402A2EA0DD41167F60E8CD6"
passphrase = "Step463656!"

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

        # Convert timestamp to datetime after ensuring it's numeric
        candles['timestamp'] = pd.to_datetime(pd.to_numeric(candles['timestamp']), unit='ms')
        candles[['open', 'high', 'low', 'close']] = candles[['open', 'high', 'low', 'close']].astype(float)

        print(f"Fetched {len(candles)} candles for {symbol}")
        return candles
    except Exception as e:
        print(f"Error fetching candles for {symbol}: {e}")
        return pd.DataFrame()

# Calculate Moving Averages
def calculate_moving_averages(candles, ma_period=125):  
    candles['sma_125'] = candles['close'].rolling(window=ma_period).mean()
    print(f"Calculated 125-period Moving Average for {len(candles)} candles")
    return candles

# Calculate Support and Resistance based on rolling highs/lows
def calculate_support_resistance(candles, window=20):  
    candles['support'] = candles['low'].rolling(window=window).min()
    candles['resistance'] = candles['high'].rolling(window=window).max()
    print(f"Calculated Support and Resistance for {len(candles)} candles")
    return candles

# Determine Slope of the 125-period MA
def calculate_ma_slope(candles, ma_period=125):
    # Calculate the slope as the difference between the current MA and the MA 125 periods ago
    candles['sma_125_slope'] = candles['sma_125'].diff(periods=1)
    return candles

# Determine Signals based on MA slope
def calculate_combined_strategy(candles, ma_period, sr_window):
    candles = calculate_moving_averages(candles, ma_period)
    candles = calculate_support_resistance(candles, sr_window)
    candles = calculate_ma_slope(candles, ma_period)

    candles['signal'] = 0
    buy_condition = (
        (candles['close'] <= candles['support']) &  # Close near support
        (candles['sma_125_slope'] > 0)  # 125 MA slope is positive (uptrend)
    )
    sell_condition = (
        (candles['close'] >= candles['resistance']) &  # Close near resistance
        (candles['sma_125_slope'] < 0)  # 125 MA slope is negative (downtrend)
    )

    candles.loc[buy_condition, 'signal'] = 1
    candles.loc[sell_condition, 'signal'] = -1

    print(f"Signals generated for {len(candles)} candles: {candles['signal'].sum()} trades")
    return candles

# Set Leverage
def set_leverage(symbol, leverage):
    try:
        response = exchange.set_leverage(leverage, symbol, params={"mgnMode": "cross"})
        print(f"Leverage set to {leverage}x for {symbol}")
        return response
    except Exception as e:
        print(f"Error setting leverage for {symbol}: {e}")
        return None

# Place an Order
def place_order(symbol, side, amount):
    try:
        order = exchange.create_order(symbol=symbol, type="market", side=side, amount=amount)
        print(f"Order placed: {side} {amount} {symbol}")
        return order
    except Exception as e:
        print(f"Order Error for {symbol}: {e}")
        return None

# Trading Bot for Multiple Symbols
def trading_bot(symbols, interval, ma_period, sr_window, trade_amount, leverage):
    # Loop through all symbols and set leverage
    for symbol in symbols:
        set_leverage(symbol, leverage)

    # Initialize counters for total signals
    total_buy_signals = 0
    total_sell_signals = 0

    while True:
        try:
            for symbol in symbols:
                candles = fetch_candles(symbol, interval)
                if candles.empty or len(candles) < max(ma_period, sr_window):
                    print(f"Insufficient data for {symbol}, waiting for next interval...")
                    continue

                candles = calculate_combined_strategy(candles, ma_period, sr_window)
                latest_signal = candles.iloc[-1]['signal']
                support = candles.iloc[-1]['support']
                resistance = candles.iloc[-1]['resistance']
                sma_125_slope = candles.iloc[-1]['sma_125_slope']

                # Get the current timestamp
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Log the latest signal and support/resistance levels for debugging
                print(f"Timestamp: {current_time}")
                print(f"Latest signal for {symbol}: {latest_signal}")
                print(f"Support: {support}, Resistance: {resistance}, MA Slope: {sma_125_slope}")

                # Count the total signals
                if latest_signal == 1:
                    print(f"Buy signal detected for {symbol}. Placing buy order...")
                    place_order(symbol, 'buy', trade_amount)
                    total_buy_signals += 1
                    print(f"Total Buy Signals: {total_buy_signals}, Total Sell Signals: {total_sell_signals} at {current_time}")
                elif latest_signal == -1:
                    print(f"Sell signal detected for {symbol}. Placing sell order...")
                    place_order(symbol, 'sell', trade_amount)
                    total_sell_signals += 1
                    print(f"Total Buy Signals: {total_buy_signals}, Total Sell Signals: {total_sell_signals} at {current_time}")

            # Output total signals after each iteration
            print(f"Total Buy Signals: {total_buy_signals}, Total Sell Signals: {total_sell_signals}")

            time.sleep(10)  # Adjust interval as needed
        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(10)

if __name__ == "__main__":
    symbols = ["SOL-USDT-SWAP", "BTC-USDT-SWAP", "ETH-USDT-SWAP", "DOGE-USDT-SWAP", "ACE-USDT-SWAP"]  # List of symbols to trade
    trading_bot(
        symbols=symbols,
        interval="5m",  # Try a longer interval for better trend data
        ma_period=90,  
        sr_window=20,  
        trade_amount=0.5,
        leverage=15
    )
