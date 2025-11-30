import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_hist"] = macd.macd_diff()
    df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    df["EMA50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
    df["EMA200"] = EMAIndicator(df["Close"], window=200).ema_indicator()
    bb = BollingerBands(df["Close"])
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    return df

def get_support_resistance(df: pd.DataFrame):
    recent = df.tail(20)
    support = recent["Low"].min()
    resistance = recent["High"].max()
    pivot = (recent["High"].max() + recent["Low"].min() + df["Close"].iloc[-1]) / 3
    s1 = 2 * pivot - recent["High"].max()
    r1 = 2 * pivot - recent["Low"].min()
    return round(support, 4), round(resistance, 4), round(s1, 4), round(r1, 4)

def generate_signal(row: pd.Series) -> str:
    signals = []
    if row["RSI"] < 30: signals.append("Strong Buy")
    elif row["RSI"] < 40: signals.append("Buy")
    elif row["RSI"] > 70: signals.append("Strong Sell")
    elif row["RSI"] > 60: signals.append("Sell")
    if row["MACD"] > row["MACD_signal"] and row["MACD_hist"] > 0:
        signals.append("MACD Bullish")
    elif row["MACD"] < row["MACD_signal"] and row["MACD_hist"] < 0:
        signals.append("MACD Bearish")
    if row["Close"] > row["EMA20"] > row["EMA50"] > row["EMA200"]:
        signals.append("Strong Uptrend")
    elif row["Close"] < row["EMA20"] < row["EMA50"] < row["EMA200"]:
        signals.append("Strong Downtrend")
    if row["Close"] <= row["BB_lower"]: signals.append("Oversold")
    if row["Close"] >= row["BB_upper"]: signals.append("Overbought")
    if not signals: return "Neutral"
    strong_buy = any("Strong Buy" in s for s in signals)
    strong_sell = any("Strong Sell" in s for s in signals)
    if strong_buy: return "STRONG BUY"
    if strong_sell: return "STRONG SELL"
    if "Buy" in " ".join(signals): return "BUY"
    if "Sell" in " ".join(signals): return "SELL"
    return "HOLD"
