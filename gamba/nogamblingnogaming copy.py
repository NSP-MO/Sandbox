import os
import ccxt
import ssl
import requests
import time
import numpy as np
import pandas as pd

# Initialize OKX API
api_key = "4c1029f9-6317-4c87-903f-3923f56de4d1"
api_secret = "B565C60ED402A2EA0DD41167F60E8CD6"
passphrase = "Step463656!"

exchange = ccxt.okx({
    'apiKey': api_key,
    'secret': api_secret,
    'password': passphrase,
})

# Fetch Market Data (Candles)
def fetch_candles(symbol, interval, limit=100):
    url = "https://www.okx.com/api/v5/market/candles"
    params = {"instId": symbol, "bar": interval, "limit": limit}
    try:
        response = requests.get(url, params=params)
        data = response.json()

        if 'data' not in data or not data['data']:
            print("Error: No candle data retrieved")
            print(f"Response: {data}")  # Add this line to see the full response from OKX API
            return pd.DataFrame()

        candles = pd.DataFrame(data['data'], columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume', 'currency', 'timestamp_end', 'market_type'
        ])

        # Convert timestamp to datetime after ensuring it's numeric
        candles['timestamp'] = pd.to_datetime(pd.to_numeric(candles['timestamp']), unit='ms')
        candles[['open', 'high', 'low', 'close']] = candles[['open', 'high', 'low', 'close']].astype(float)

        print(f"Fetched {len(candles)} candles")
        return candles
    except Exception as e:
        print(f"Error fetching candles: {e}")
        return pd.DataFrame()


# Calculate Fisher Transform
def calculate_fisher_transform(candles, period=10):
    try:
        high = candles['high']
        low = candles['low']
        close = candles['close']

        # Normalize prices
        min_low = low.rolling(period).min()
        max_high = high.rolling(period).max()
        value = 2 * ((close - min_low) / (max_high - min_low) - 0.5)
        
        # Clip values to avoid division by zero in log
        value = value.clip(-0.9999, 0.9999)

        # Fisher Transform
        fisher = 0.5 * np.log((1 + value) / (1 - value))
        candles['fisher'] = fisher.rolling(window=1).mean()
        candles['fisher_signal'] = candles['fisher'].shift(1)

        print(f"Calculated Fisher Transform for {len(candles)} candles")
        return candles
    except Exception as e:
        print(f"Error calculating Fisher Transform: {e}")
        return candles


# Calculate Moving Averages
def calculate_moving_averages(candles, short_window, long_window):
    candles['sma_short'] = candles['close'].rolling(window=short_window).mean()
    candles['sma_long'] = candles['close'].rolling(window=long_window).mean()
    print(f"Calculated Moving Averages for {len(candles)} candles")
    return candles


# Calculate Support and Resistance
def calculate_support_resistance(candles, pivot_window=5):
    candles['support'] = candles['low'].rolling(window=pivot_window).min()
    candles['resistance'] = candles['high'].rolling(window=pivot_window).max()
    print(f"Calculated Support and Resistance for {len(candles)} candles")
    return candles


# Determine Signals
def calculate_combined_strategy(candles, fisher_period, short_window, long_window, pivot_window):
    candles = calculate_fisher_transform(candles, fisher_period)
    candles = calculate_moving_averages(candles, short_window, long_window)
    candles = calculate_support_resistance(candles, pivot_window)

    candles['signal'] = 0
    buy_condition = (
        (candles['close'] <= candles['support']) &  # Close near support
        (candles['sma_short'] > candles['sma_long']) &  # Trend is bullish
        (candles['fisher'] > candles['fisher_signal'])  # Fisher is rising
    )
    sell_condition = (
        (candles['close'] >= candles['resistance']) &  # Close near resistance
        (candles['sma_short'] < candles['sma_long']) &  # Trend is bearish
        (candles['fisher'] < candles['fisher_signal'])  # Fisher is falling
    )

    candles.loc[buy_condition, 'signal'] = 1
    candles.loc[sell_condition, 'signal'] = -1

    print(f"Signals generated: {candles['signal'].sum()} trades")
    return candles


# Set Leverage
def set_leverage(symbol, leverage):
    try:
        response = exchange.set_leverage(leverage, symbol, params={"mgnMode": "cross"})
        print(f"Leverage set to {leverage}x for {symbol}")
        return response
    except Exception as e:
        print(f"Error setting leverage: {e}")
        return None


# Place an Order
def place_order(symbol, side, amount):
    try:
        order = exchange.create_order(symbol=symbol, type="market", side=side, amount=amount)
        print(f"Order placed: {side} {amount} {symbol}")
        return order
    except Exception as e:
        print(f"Order Error: {e}")
        return None


# Trading Bot
def trading_bot(symbol, interval, fisher_period, short_window, long_window, pivot_window, trade_amount, leverage):
    set_leverage(symbol, leverage)

    while True:
        try:
            candles = fetch_candles(symbol, interval)
            if candles.empty or len(candles) < max(fisher_period, short_window, long_window):
                print("Insufficient data, waiting for next interval...")
                time.sleep(60)
                continue

            candles = calculate_combined_strategy(candles, fisher_period, short_window, long_window, pivot_window)
            latest_signal = candles.iloc[-1]['signal']
            support = candles.iloc[-1]['support']
            resistance = candles.iloc[-1]['resistance']

            print(f"Latest signal: {latest_signal}")
            if latest_signal == 1:
                print(f"Buy signal detected. Placing buy order...")
                place_order(symbol, 'buy', trade_amount)
            elif latest_signal == -1:
                print(f"Sell signal detected. Placing sell order...")
                place_order(symbol, 'sell', trade_amount)

            time.sleep(60)  # Adjust interval as needed
        except Exception as e:
            print(f"Error in trading loop: {e}")
            time.sleep(60)


if __name__ == "__main__":
    trading_bot(
        symbol="ACE-USDT-SWAP",
        interval="1m",
        fisher_period=10,
        short_window=10,
        long_window=50,
        pivot_window=5,
        trade_amount=10,
        leverage=15
    )
