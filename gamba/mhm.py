import os
import ccxt
import requests
import time
import numpy as np
import pandas as pd

# ==========================================
#           CONFIGURATION SETTINGS
# ==========================================
SYMBOL = "ACE-USDT-SWAP"
TIMEFRAME = "15m"
LEVERAGE = 10
RISK_PERCENT = 0.02
SAFETY_BUFFER = 0.15

# Technical Parameters
FAST_SMA = 5
SLOW_SMA = 15
FISHER_PERIOD = 7
SR_WINDOW = 75  # 75-period lookback
BUFFER_PCT = 0.005  # Tight 0.5% buffer

# API Configuration
EXCHANGE = ccxt.okx({
    'apiKey': "4c1029f9-6317-4c87-903f-3923f56de4d1",
    'secret': "B565C60ED402A2EA0DD41167F60E8CD6",
    'password': "Step463656!",
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'}
})

# ==========================================
#               CORE FUNCTIONS
# ==========================================

def get_account_balance():
    try:
        balance = EXCHANGE.fetch_balance({'type':'swap'})
        return float(balance['USDT']['free'])
    except Exception as e:
        print(f"Balance check failed: {e}")
        return 0

def calculate_position_size():
    try:
        balance = get_account_balance()
        if balance <= 0:
            return 0
            
        ticker = EXCHANGE.fetch_ticker(SYMBOL)
        price = float(ticker['last'])
        max_risk_amount = balance * RISK_PERCENT
        contract_size = (max_risk_amount * (1 - SAFETY_BUFFER)) / (price / LEVERAGE)
        return round(max(contract_size, 0.001), 3)
    except Exception as e:
        print(f"Position calculation error: {e}")
        return 0

def fetch_candles(symbol, interval, limit=200):
    try:
        candles = EXCHANGE.fetch_ohlcv(symbol, timeframe=interval, limit=limit)
        df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df[-limit:]
    except Exception as e:
        print(f"Data fetch error: {e}")
        return pd.DataFrame()

def calculate_indicators(df):
    try:
        # Corrected: Removed .shift(1) to use current window
        df['resistance'] = df['high'].rolling(SR_WINDOW).max()
        df['support'] = df['low'].rolling(SR_WINDOW).min()
        
        # Momentum Indicators
        df['fast_sma'] = df['close'].rolling(FAST_SMA).mean()
        df['slow_sma'] = df['close'].rolling(SLOW_SMA).mean()
        df['ema_34'] = df['close'].ewm(span=34, adjust=False).mean()
        
        # Fisher Transform
        high, low = df['high'], df['low']
        max_high = high.rolling(FISHER_PERIOD).max()
        min_low = low.rolling(FISHER_PERIOD).min()
        
        with np.errstate(divide='ignore', invalid='ignore'):
            value = 2 * ((df['close'] - min_low) / (max_high - min_low).replace(0, 1e-5) - 0.5)
            value = value.clip(-0.9999, 0.9999)
            fisher = 0.5 * np.log((1 + value) / (1 - value))
            
        df['fisher'] = fisher.ewm(span=3, adjust=False).mean()
        df['fisher_signal'] = df['fisher'].rolling(5).mean()
        
        return df.dropna()
    except Exception as e:
        print(f"Indicator error: {e}")
        return df

def generate_signals(df):
    df['signal'] = 0
    
    # Buy at 75-period low with confirmation
    buy_condition = (
        (df['close'] <= df['support'] * (1 + BUFFER_PCT)) &  # Price near current 75-period low
        (df['fast_sma'] > df['slow_sma']) &                   # Upward momentum
        (df['fisher'] > df['fisher_signal'])                  # Bullish divergence
    )
    
    # Sell at 75-period high with confirmation
    sell_condition = (
        (df['close'] >= df['resistance'] * (1 - BUFFER_PCT)) &  # Price near current 75-period high
        (df['fast_sma'] < df['slow_sma']) &                     # Downward momentum
        (df['fisher'] < df['fisher_signal'])                    # Bearish divergence
    )
    
    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1
    
    return df

# ==========================================
#           TRADING EXECUTION
# ==========================================

def execute_trade(signal, last_price):
    try:
        position_size = calculate_position_size()
        if position_size <= 0:
            return None

        params = {
            'tdMode': 'cross',
            'posSide': 'long' if signal == 1 else 'short',
            'clOrdId': EXCHANGE.uuid()[:32]
        }

        if signal == 1:
            order = EXCHANGE.create_market_buy_order(SYMBOL, position_size, params=params)
            print(f"BUY @ {last_price} - 75-period low area")
        else:
            order = EXCHANGE.create_market_sell_order(SYMBOL, position_size, params=params)
            print(f"SELL @ {last_price} - 75-period high area")
            
        return order
        
    except Exception as e:
        print(f"Trade execution failed: {str(e)}")
        return None

# ==========================================
#               MAIN BOT LOOP
# ==========================================

def run_bot():
    EXCHANGE.set_leverage(LEVERAGE, SYMBOL)
    print(f"Bot started - Trading {SYMBOL} using 75-period highs/lows")
    
    while True:
        try:
            df = fetch_candles(SYMBOL, TIMEFRAME)
            if len(df) < SR_WINDOW * 2:
                print(f"Collecting data ({len(df)}/{SR_WINDOW*2})...")
                time.sleep(10)
                continue
                
            df = calculate_indicators(df)
            df = generate_signals(df)
            current_signal = df['signal'].iloc[-1]
            last_close = df['close'].iloc[-1]
            
            print("\n" + "="*40)
            print(f"Price: {last_close:.2f}")
            print(f"75-period Low: {df['support'].iloc[-1]:.3f}")
            print(f"75-period High: {df['resistance'].iloc[-1]:.3f}")
            print(f"Signal: {'BUY' if current_signal == 1 else 'SELL' if current_signal == -1 else 'NEUTRAL'}")
            print("="*40 + "\n")
            
            if current_signal != 0:
                execute_trade(current_signal, last_close)
                
            time.sleep(60 - time.time() % 60)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()