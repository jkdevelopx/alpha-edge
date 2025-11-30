import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from scripts.signals import add_indicators, generate_signal
from scripts.backtest import backtest_strategy
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

st.set_page_config(page_title="Alpha Edge", layout="wide", page_icon="Chart Increasing")
st.markdown("# Alpha Edge")
st.markdown("**Quantitative Trading Dashboard** • Live Signals • Backtested Strategy")

# Sidebar
@st.cache_data(ttl=3600)
def get_symbols():
    try:
        data = supabase.table("daily_prices").select("symbol").execute()
        return sorted({row["symbol"] for row in data.data})
    except:
        return ["BTC", "AAPL", "ETH"]

symbols = get_symbols()
symbol = st.sidebar.selectbox("Select Asset", symbols, index=symbols.index("BTC") if "BTC" in symbols else 0)

# ดึงข้อมูล
@st.cache_data(ttl=600)
def get_data(sym):
    resp = supabase.table("daily_prices").select("*").eq("symbol", sym).order("date").execute()
    df = pd.DataFrame(resp.data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    return df

df = get_data(symbol)
df = add_indicators(df)

latest = df.iloc[-1]
signal = generate_signal(latest)

# Header metrics
col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Price", f"${latest.Close:,.2f}")
with col2: st.metric("RSI", f"{latest.RSI:.1f}")
with col3: st.metric("MACD", f"{latest.MACD:+.4f}")
with col4:
    color = "lime" if "BUY" in signal else "red" if "SELL" in signal else "gray"
    st.markdown(f"**Live Signal**  \n<span style='font-size:2.2em;color:{color}'>{signal}</span>", unsafe_allow_html=True)

# กราฟราคา + indicator
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA20, name="EMA20", line=dict(color="#00ff88", width=2)))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA50, name="EMA50", line=dict(color="#ff00ff")))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA200, name="EMA200", line=dict(color="#ff4444")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_upper, name="BB Upper", line=dict(dash="dot", color="gray")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_lower, name="BB Lower", line=dict(dash="dot", color="gray")))
fig.update_layout(height=600, template="plotly_dark", xaxis_rangeslider_visible=False, title=f"{symbol} • Live Chart")
st.plotly_chart(fig, use_container_width=True)

# Backtest
st.markdown("---")
st.subheader("Strategy Backtest (RSI + MACD + EMA Trend)")
result = backtest_strategy(df.copy())

col1, col2, col3, col4, col5 = st.columns(5)
with col1: st.metric("Total Return", f"{result['total_return']:.1%}")
with col2: st.metric("CAGR", f"{result['cagr']:.1%}")
with col3: st.metric("Sharpe Ratio", f"{result['sharpe']:.2f}")
with col4: st.metric("Max Drawdown", f"{result['max_drawdown']:.1%}")
with col5: st.metric("Win Rate", f"{result['win_rate']:.1%}")

# Equity curve
fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=result['df'].index, y=result['df']['cum_market'], name="Buy & Hold", line=dict(color="gray")))
fig2.add_trace(go.Scatter(x=result['df'].index, y=result['df']['cum_strategy'], name="Strategy", line=dict(color="#00ff88", width=3)))
fig2.update_layout(template="plotly_dark", height=500, title="Equity Curve")
st.plotly_chart(fig2, use_container_width=True)

st.caption(f"Data updated daily • Built by jkdevelopx • November 2025")
