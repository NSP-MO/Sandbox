import os
import ccxt
import time
import numpy as np
import pandas as pd

try:
    import winsound
except ImportError:
    winsound = None

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
SR_WINDOW = 75
BUFFER_PCT = 0.005
LOOKBACK_SHIFT = 10


# API Configuration
EXCHANGE = ccxt.okx({
    'apiKey': "4c1029f9-6317-4c87-903f-3923f56de4d1",
    'secret': "B565C60ED402A2EA0DD41167F60E8CD6",
    'password': "Step463656!",
    'enableRateLimit': True,
    'options': {'defaultType': 'swap'},
})

# ==========================================
#               CORE FUNCTIONS
# ==========================================

def get_strategy_description(row):
    """Generate human-readable strategy explanation for signals"""
    reasons = []
    
    if row['signal'] == 1:
        if row['close'] <= row['support'] * (1 + BUFFER_PCT):
            reasons.append(f"Price within {BUFFER_PCT*100:.1f}% of 75-period support ({row['support']:.3f})")
        if row['fast_sma'] > row['slow_sma']:
            reasons.append(f"{FAST_SMA}SMA > {SLOW_SMA}SMA ({row['fast_sma']:.3f} vs {row['slow_sma']:.3f})")
        if row['fisher'] > row['fisher_signal']:
            reasons.append(f"Fisher bullish divergence ({row['fisher']:.2f} > {row['fisher_signal']:.2f})")
            
    elif row['signal'] == -1:
        if row['close'] >= row['resistance'] * (1 - BUFFER_PCT):
            reasons.append(f"Price within {BUFFER_PCT*100:.1f}% of 75-period resistance ({row['resistance']:.3f})")
        if row['fast_sma'] < row['slow_sma']:
            reasons.append(f"{FAST_SMA}SMA < {SLOW_SMA}SMA ({row['fast_sma']:.3f} vs {row['slow_sma']:.3f})")
        if row['fisher'] < row['fisher_signal']:
            reasons.append(f"Fisher bearish divergence ({row['fisher']:.2f} < {row['fisher_signal']:.2f})")
    
    return " | ".join(reasons) if reasons else "No active signals"

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
        df['resistance'] = df['high'].rolling(SR_WINDOW).max().shift(LOOKBACK_SHIFT)
        df['support'] = df['low'].rolling(SR_WINDOW).min().shift(LOOKBACK_SHIFT)
        
        df['fast_sma'] = df['close'].rolling(FAST_SMA).mean()
        df['slow_sma'] = df['close'].rolling(SLOW_SMA).mean()
        df['ema_34'] = df['close'].ewm(span=34, adjust=False).mean()
        
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
    
    buy_condition = (
        (df['close'] <= df['support'] * (1 + BUFFER_PCT)) &
        (df['fast_sma'] > df['slow_sma']) &
        (df['fisher'] > df['fisher_signal'])
    )
    
    sell_condition = (
        (df['close'] >= df['resistance'] * (1 - BUFFER_PCT)) &
        (df['fast_sma'] < df['slow_sma']) &
        (df['fisher'] < df['fisher_signal'])
    )
    
    df.loc[buy_condition, 'signal'] = 1
    df.loc[sell_condition, 'signal'] = -1
    
    # Add strategy description for each signal
    df['strategy_reason'] = df.apply(get_strategy_description, axis=1)
    
    return df

# ==========================================
#           TRADING EXECUTION
# ==========================================

def execute_trade(signal, last_price, strategy_reason):
    try:
        position_size = calculate_position_size()
        if position_size <= 0:
            return None

        params = {
            'tdMode': 'cross',
            'posSide': 'long' if signal == 1 else 'short',
            'clOrdId': EXCHANGE.uuid()[:32]
        }

        action = "BUY" if signal == 1 else "SELL"
        print(f"\n{action} SIGNAL DETAILS:")
        print(f"- Price: {last_price:.3f}")
        print(f"- Strategy Reasons: {strategy_reason}")
        
        if signal == 1:
            order = EXCHANGE.create_market_buy_order(SYMBOL, position_size, params=params)
            print(f"Executed BUY @ {last_price:.3f}")
        else:
            order = EXCHANGE.create_market_sell_order(SYMBOL, position_size, params=params)
            print(f"Executed SELL @ {last_price:.3f}")
            
        return order
        
    except Exception as e:
        print(f"Trade execution failed: {str(e)}")
        return None

# ==========================================
#               MAIN BOT LOOP
# ==========================================

def run_bot():
    EXCHANGE.set_leverage(LEVERAGE, SYMBOL)
    print(f"Bot started - 75-period S/R Strategy with Momentum Confirmation")
    print("Strategy Logic:")
    print(f"- Buy when price is within {BUFFER_PCT*100:.1f}% of 75-period support")
    print(f"- Sell when price is within {BUFFER_PCT*100:.1f}% of 75-period resistance")
    print(f"- Confirm with {FAST_SMA}/{SLOW_SMA} SMA crossover and Fisher Transform")
    
    while True:
        try:
            df = fetch_candles(SYMBOL, TIMEFRAME)
            if len(df) < (SR_WINDOW + LOOKBACK_SHIFT) * 2:
                print(f"Collecting data ({len(df)}/{(SR_WINDOW + LOOKBACK_SHIFT)*2})...")
                time.sleep(10)
                continue
                
            df = calculate_indicators(df)
            df = generate_signals(df)
            
            current_signal = df['signal'].iloc[-1]
            last_close = df['close'].iloc[-1]
            strategy_reason = df['strategy_reason'].iloc[-1]
            
            print("\n" + "="*60)
            print(f"[{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}] Market Update:")
            print(f"Price: {last_close:.3f}")
            print(f"Support: {df['support'].iloc[-1]:.3f} | Resistance: {df['resistance'].iloc[-1]:.3f}")
            print(f"Fast SMA: {df['fast_sma'].iloc[-1]:.3f} | Slow SMA: {df['slow_sma'].iloc[-1]:.3f}")
            print(f"Fisher: {df['fisher'].iloc[-1]:.2f} | Signal: {df['fisher_signal'].iloc[-1]:.2f}")
            print("="*60)
            print(f"STRATEGY STATUS: {strategy_reason}")
            print("="*60 + "\n")
            
            if current_signal != 0:
                if winsound:
                    winsound.Beep(1000, 1000)
                else:
                    print('\a')
                execute_trade(current_signal, last_close, strategy_reason)
                
            time.sleep(5 - time.time() % 5)
            
        except Exception as e:
            print(f"Main loop error: {e}")
            time.sleep(30)

if __name__ == "__main__":
    run_bot()