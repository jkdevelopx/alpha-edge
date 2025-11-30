import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands

def add_indicators(df):
    df = df.copy()
    
    # RSI
    df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
    
    # MACD
    macd = MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_signal'] = macd.macd_signal()
    df['MACD_hist'] = macd.macd_diff()
    
    # EMA
    df['EMA20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
    df['EMA50'] = EMAIndicator(df['Close'], window=50).ema_indicator()
    df['EMA200'] = EMAIndicator(df['Close'], window=200).ema_indicator()
    
    # Bollinger Bands
    bb = BollingerBands(df['Close'])
    df['BB_upper'] = bb.bollinger_hband()
    df['BB_lower'] = bb.bollinger_lband()
    df['BB_mid'] = bb.bollinger_mavg()
    
    return df

def generate_signal(row):
    signals = []
    
    # RSI
    if row['RSI'] < 30:
        signals.append("Strong Buy")
    elif row['RSI'] < 40:
        signals.append("Buy")
    elif row['RSI'] > 70:
        signals.append("Strong Sell")
    elif row['RSI'] > 60:
        signals.append("Sell")
    
    # MACD
    if row['MACD'] > row['MACD_signal'] and row['MACD_hist'] > 0:
        signals.append("MACD Bullish")
    elif row['MACD'] < row['MACD_signal'] and row['MACD_hist'] < 0:
        signals.append("MACD Bearish")
    
    # EMA Trend
    if row['Close'] > row['EMA20'] > row['EMA50'] > row['EMA200']:
        signals.append("Strong Uptrend")
    elif row['Close'] < row['EMA20'] < row['EMA50'] < row['EMA200']:
        signals.append("Strong Downtrend")
    
    # Bollinger Squeeze / Breakout
    if row['Close'] <= row['BB_lower']:
        signals.append("Oversold (BB)")
    elif row['Close'] >= row['BB_upper']:
        signals.append("Overbought (BB)")
    
    return ", ".join(signals) if signals else "Hold"
