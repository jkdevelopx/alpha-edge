import pandas as pd
import numpy as np
from scripts.signals import add_indicators, generate_signal

def backtest_strategy(df: pd.DataFrame) -> dict:
    df = add_indicators(df).copy()
    df = df.dropna()

    # สร้าง signal ทุกวัน
    df['signal_text'] = df.apply(lambda row: generate_signal(row), axis=1)

    # แปลงเป็น position: 1 = long, 0 = flat
    df['position'] = df['signal_text'].apply(lambda x: 1 if 'BUY' in x else 0)

    # Daily return
    df['market_return'] = df['Close'].pct_change()
    df['strategy_return'] = df['market_return'] * df['position'].shift(1)

    # Cumulative returns
    df['cum_market'] = (1 + df['market_return']).cumprod()
    df['cum_strategy'] = (1 + df['strategy_return']).cumprod()

    # Stats
    total_return = df['cum_strategy'].iloc[-1] - 1
    cagr = (df['cum_strategy'].iloc[-1]) ** (365/len(df)) - 1
    sharpe = np.sqrt(252) * df['strategy_return'].mean() / df['strategy_return'].std() if df['strategy_return'].std() != 0 else 0
    max_dd = (df['cum_strategy'].cummax() - df['cum_strategy']).max()

    return {
        'df': df,
        'total_return': total_return,
        'cagr': cagr,
        'sharpe': sharpe,
        'max_drawdown': max_dd,
        'win_rate': (df['strategy_return'] > 0).mean() if len(df) > 0 else 0
    }
