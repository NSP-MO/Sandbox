import os
import ccxt
import time
import getpass
import numpy as np
import pandas as pd
from typing import Dict, Optional

try:
    import winsound
except ImportError:
    winsound = None

class ExchangeClient:
    """Handles all exchange communications using CCXT"""
    def __init__(self, config: Dict):
        self.exchange = ccxt.okx({
            'apiKey': config['api_key'],
            'secret': config['secret'],
            'password': config['password'],
            'enableRateLimit': True,
            'options': {'defaultType': 'swap'},
        })
        self.symbol = config['symbol']
        self.leverage = config['leverage']
        self._set_leverage()

    def _set_leverage(self):
        try:
            self.exchange.set_leverage(self.leverage, self.symbol)
        except Exception as e:
            print(f"Error setting leverage: {e}")

    def fetch_balance(self) -> float:
        """Get available USDT balance"""
        try:
            balance = self.exchange.fetch_balance({'type': 'swap'})
            return float(balance['USDT']['free'])
        except Exception as e:
            print(f"Balance check failed: {e}")
            return 0.0

    def fetch_ticker(self) -> Optional[float]:
        """Get current market price"""
        try:
            ticker = self.exchange.fetch_ticker(self.symbol)
            return float(ticker['last'])
        except Exception as e:
            print(f"Price check failed: {e}")
            return None

    def fetch_ohlcv(self, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Retrieve historical candle data"""
        try:
            candles = self.exchange.fetch_ohlcv(self.symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(candles, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except Exception as e:
            print(f"Data fetch error: {e}")
            return pd.DataFrame()

    def create_order(self, side: str, amount: float) -> Optional[Dict]:
        """Execute market order"""
        try:
            params = {
                'tdMode': 'cross',
                'posSide': 'long' if side == 'buy' else 'short',
                'clOrdId': self.exchange.uuid()[:32]
            }
            return self.exchange.create_market_order(self.symbol, side, amount, params=params)
        except Exception as e:
            print(f"Order execution failed: {e}")
            return None


class DataHandler:
    """Handles data retrieval and technical indicator calculation"""
    def __init__(self, exchange: ExchangeClient, config: Dict):
        self.exchange = exchange
        self.sr_window = config['sr_window']
        self.lookback_shift = config['lookback_shift']
        self.fast_sma = config['fast_sma']
        self.slow_sma = config['slow_sma']
        self.fisher_period = config['fisher_period']

    def get_processed_data(self, timeframe: str, limit: int = 200) -> pd.DataFrame:
        """Fetch and process market data"""
        df = self.exchange.fetch_ohlcv(timeframe, limit)
        if not df.empty:
            return self._calculate_indicators(df)
        return df

    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        try:
            # Support/Resistance
            df['resistance'] = df['high'].rolling(self.sr_window).max().shift(self.lookback_shift)
            df['support'] = df['low'].rolling(self.sr_window).min().shift(self.lookback_shift)
            
            # Moving Averages
            df['fast_sma'] = df['close'].rolling(self.fast_sma).mean()
            df['slow_sma'] = df['close'].rolling(self.slow_sma).mean()
            
            # Fisher Transform
            high, low = df['high'], df['low']
            max_high = high.rolling(self.fisher_period).max()
            min_low = low.rolling(self.fisher_period).min()
            
            with np.errstate(divide='ignore', invalid='ignore'):
                value = 2 * ((df['close'] - min_low) / (max_high - min_low).replace(0, 1e-5) - 0.5)
                value = value.clip(-0.9999, 0.9999)
                fisher = 0.5 * np.log((1 + value) / (1 - value))
                
            df['fisher'] = fisher.ewm(span=3, adjust=False).mean()
            df['fisher_signal'] = df['fisher'].rolling(5).mean()
            
            return df.dropna()
        except Exception as e:
            print(f"Indicator calculation error: {e}")
            return df


class SignalGenerator:
    """Generates trading signals based on technical indicators"""
    def __init__(self, config: Dict):
        self.buffer_pct = config['buffer_pct']
        self.fast_sma = config['fast_sma']
        self.slow_sma = config['slow_sma']

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals and strategy reasons"""
        df['signal'] = 0
        df['strategy_reason'] = ''
        
        # Buy conditions
        buy_mask = (
            (df['close'] <= df['support'] * (1 + self.buffer_pct)) &
            (df['fast_sma'] > df['slow_sma']) &
            (df['fisher'] > df['fisher_signal'])
        )
        df.loc[buy_mask, 'signal'] = 1
        
        # Sell conditions
        sell_mask = (
            (df['close'] >= df['resistance'] * (1 - self.buffer_pct)) &
            (df['fast_sma'] < df['slow_sma']) &
            (df['fisher'] < df['fisher_signal'])
        )
        df.loc[sell_mask, 'signal'] = -1
        
        # Generate strategy reasons
        df['strategy_reason'] = df.apply(self._get_strategy_description, axis=1)
        return df

    def _get_strategy_description(self, row) -> str:
        """Generate human-readable signal explanation"""
        reasons = []
        if row['signal'] == 1:
            if row['close'] <= row['support'] * (1 + self.buffer_pct):
                reasons.append(f"Price within {self.buffer_pct*100:.1f}% of support ({row['support']:.3f})")
            if row['fast_sma'] > row['slow_sma']:
                reasons.append(f"{self.fast_sma}SMA > {self.slow_sma}SMA")
            if row['fisher'] > row['fisher_signal']:
                reasons.append("Fisher bullish")
                
        elif row['signal'] == -1:
            if row['close'] >= row['resistance'] * (1 - self.buffer_pct):
                reasons.append(f"Price within {self.buffer_pct*100:.1f}% of resistance ({row['resistance']:.3f})")
            if row['fast_sma'] < row['slow_sma']:
                reasons.append(f"{self.fast_sma}SMA < {self.slow_sma}SMA")
            if row['fisher'] < row['fisher_signal']:
                reasons.append("Fisher bearish")
                
        return " | ".join(reasons) if reasons else "No active signals"


class TradeExecutor:
    """Manages position sizing and order execution"""
    def __init__(self, exchange: ExchangeClient, config: Dict):
        self.exchange = exchange
        self.risk_percent = config['risk_percent']
        self.safety_buffer = config['safety_buffer']
        self.leverage = config['leverage']
        self.symbol = config['symbol']

    def calculate_position_size(self, price: float) -> float:
        """Calculate appropriate position size based on risk parameters"""
        balance = self.exchange.fetch_balance()
        if balance <= 0:
            return 0.0
            
        risk_amount = balance * self.risk_percent
        adjusted_amount = risk_amount * (1 - self.safety_buffer)
        return round(adjusted_amount / (price / self.leverage), 3)

    def execute_trade(self, signal: int, price: float, reason: str) -> Optional[Dict]:
        """Execute trade based on signal"""
        position_size = self.calculate_position_size(price)
        if position_size <= 0:
            return None

        action = "BUY" if signal == 1 else "SELL"
        print(f"\n{action} SIGNAL TRIGGERED")
        print(f"Price: {price:.3f}")
        print(f"Reason: {reason}")
        
        return self.exchange.create_order('buy' if signal == 1 else 'sell', position_size)


class TradingBot:
    """Main trading bot class orchestrating all components"""
    def __init__(self, config: Dict):
        self.config = config
        self.exchange = ExchangeClient(config)
        self.data_handler = DataHandler(self.exchange, config)
        self.signal_generator = SignalGenerator(config)
        self.trade_executor = TradeExecutor(self.exchange, config)
        self.alert_enabled = True

    def _print_market_status(self, df: pd.DataFrame):
        """Print current market status"""
        last = df.iloc[-1]
        print("\n" + "="*60)
        print(f"[{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}] Market Update:")
        print(f"Price: {last['close']:.3f}")
        print(f"Support: {last['support']:.3f} | Resistance: {last['resistance']:.3f}")
        print(f"Fast SMA: {last['fast_sma']:.3f} | Slow SMA: {last['slow_sma']:.3f}")
        print(f"Fisher: {last['fisher']:.2f} | Signal: {last['fisher_signal']:.2f}")
        print("="*60)
        print(f"STRATEGY STATUS: {last['strategy_reason']}")
        print("="*60 + "\n")

    def _alert(self):
        """Play alert sound"""
        if winsound:
            winsound.Beep(1000, 1000)
        else:
            print('\a')

    def run(self):
        """Main trading loop"""
        print("Initializing Trading Bot...")
        print(f"Symbol: {self.config['symbol']}")
        print(f"Timeframe: {self.config['timeframe']}")
        print(f"Leverage: {self.config['leverage']}x")
        print("Strategy Parameters:")
        print(f"- {self.config['fast_sma']}/{self.config['slow_sma']} SMA Crossover")
        print(f"- {self.config['sr_window']}-period Support/Resistance")
        print(f"- {self.config['fisher_period']}-period Fisher Transform")
        
        while True:
            try:
                # Fetch and process data
                df = self.data_handler.get_processed_data(self.config['timeframe'])
                if len(df) < (self.config['sr_window'] + self.config['lookback_shift']) * 2:
                    print("Waiting for sufficient data...")
                    time.sleep(10)
                    continue
                
                # Generate signals
                df = self.signal_generator.generate_signals(df)
                current_signal = df['signal'].iloc[-1]
                last_close = df['close'].iloc[-1]
                strategy_reason = df['strategy_reason'].iloc[-1]

                # Print market status
                self._print_market_status(df)

                # Execute trade if signal present
                if current_signal != 0:
                    if self.alert_enabled:
                        self._alert()
                    self.trade_executor.execute_trade(current_signal, last_close, strategy_reason)
                
                time.sleep(5 - time.time() % 5)
                
            except Exception as e:
                print(f"Main loop error: {e}")
                time.sleep(30)


if __name__ == "__main__":
    # Configuration
    config = {
        'api_key': "4c1029f9-6317-4c87-903f-3923f56de4d1",
        'secret': "B565C60ED402A2EA0DD41167F60E8CD6",
        'symbol': "ACE-USDT-SWAP",
        'timeframe': "15m",
        'leverage': 10,
        'risk_percent': 0.02,
        'safety_buffer': 0.15,
        'sr_window': 75,
        'lookback_shift': 10,
        'fast_sma': 5,
        'slow_sma': 15,
        'fisher_period': 7,
        'buffer_pct': 0.005,
    }
    
    config['password'] = getpass.getpass("Enter your OKX exchange password: ")


    # Initialize and run bot
    bot = TradingBot(config)
    bot.run()