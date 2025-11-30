# scripts/signals.py
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, EMAIndicator
from ta.volatility import BollingerBands


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add technical indicators to the price DataFrame
    """
    df = df.copy()

    # RSI (14)
    df["RSI"] = RSIIndicator(df["Close"], window=14).rsi()

    # MACD
    macd = MACD(df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["MACD_hist"] = macd.macd_diff()

    # EMA 20, 50, 200
    df["EMA20"] = EMAIndicator(df["Close"], window=20).ema_indicator()
    df["EMA50"] = EMAIndicator(df["Close"], window=50).ema_indicator()
    df["EMA200"] = EMAIndicator(df["Close"], window=200).ema_indicator()

    # Bollinger Bands
    bb = BollingerBands(df["Close"], window=20, window_dev=2)
    df["BB_upper"] = bb.bollinger_hband()
    df["BB_lower"] = bb.bollinger_lband()
    df["BB_mid"] = bb.bollinger_mavg()

    return df


def generate_signal(row: pd.Series) -> str:
    """
    Generate trading signal based on latest row
    """
    signals = []

    # RSI logic
    if row["RSI"] < 30:
        signals.append("Strong Buy (RSI)")
    elif row["RSI"] < 40:
        signals.append("Buy (RSI)")
    elif row["RSI"] > 70:
        signals.append("Strong Sell (RSI)")
    elif row["RSI"] > 60:
        signals.append("Sell (RSI)")

    # MACD crossover
    if row["MACD"] > row["MACD_signal"] and row["MACD_hist"] > 0:
        signals.append("MACD Bullish")
    elif row["MACD"] < row["MACD_signal"] and row["MACD_hist"] < 0:
        signals.append("MACD Bearish")

    # EMA trend
    if row["Close"] > row["EMA20"] > row["EMA50"] > row["EMA200"]:
        signals.append("Strong Uptrend")
    elif row["Close"] < row["EMA20"] < row["EMA50"] < row["EMA200"]:
        signals.append("Strong Downtrend")

    # Bollinger Bands
    if row["Close"] <= row["BB_lower"]:
        signals.append("Oversold (BB)")
    elif row["Close"] >= row["BB_upper"]:
        signals.append("Overbought (BB)")

    # Final decision
    if not signals:
        return "Hold / Neutral"

    # Priority: Strong > Regular
    strong_buy = any("Strong Buy" in s for s in signals)
    strong_sell = any("Strong Sell" in s for s in signals)

    if strong_buy and not strong_sell:
        return "STRONG BUY"
    if strong_sell and not strong_buy:
        return "STRONG SELL"
    if any("Buy" in s for s in signals) and not strong_sell:
        return "BUY"
    if any("Sell" in s for s in signals) and not strong_buy:
        return "SELL"

    return ", ".join(signals)  # Multiple conditions