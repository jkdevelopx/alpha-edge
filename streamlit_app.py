import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from scripts.signals import add_indicators, generate_signal
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Page config
st.set_page_config(page_title="Alpha Edge", layout="wide", page_icon="Chart Increasing")

# Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Title
st.markdown("# Alpha Edge")
st.markdown("**Quantitative Trading Dashboard** • Real-time Signals • Backtested Strategy")

# Sidebar - Asset selector
@st.cache_data(ttl=3600)
def get_symbols():
    data = supabase.table("daily_prices").select("symbol").execute()
    return sorted({row["symbol"] for row in data.data})

symbols = get_symbols()
symbol = st.sidebar.selectbox("Select Asset", symbols, index=symbols.index("BTC") if "BTC" in symbols else 0)

# Get data
@st.cache_data(ttl=600)
def get_data(sym):
    resp = supabase.table("daily_prices").select("*").eq("symbol", sym).order("date").execute()
    df = pd.DataFrame(resp.data)
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    return df

df = get_data(symbol)
df = add_indicators(df)

# Latest signal
latest = df.iloc[-1]
signal = generate_signal(latest)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Price", f"${latest.Close:,.2f}")
with col2:
    st.metric("RSI", f"{latest.RSI:.1f}")
with col3:
    st.metric("MACD", f"{latest.MACD:.4f}")
with col4:
    color = "green" if "Buy" in signal else "red" if "Sell" in signal else "gray"
    st.markdown(f"**Signal**  \n<span style='color:{color};font-size:1.5em'>{signal}</span>", unsafe_allow_html=True)

# Chart
fig = go.Figure()

# Candlestick
fig.add_trace(go.Candlestick(
    x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close,
    name="Price"
))

# Bollinger Bands
fig.add_trace(go.Scatter(x=df.index, y=df.BB_upper, name="BB Upper", line=dict(dash="dot")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_lower, name="BB Lower", line=dict(dash="dot")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_mid, name="BB Mid", line=dict(color="orange")))

# EMAs
fig.add_trace(go.Scatter(x=df.index, y=df.EMA20, name="EMA20", line=dict(color="blue")))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA50, name="EMA50", line=dict(color="purple")))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA200, name="EMA200", line=dict(color="red")))

fig.update_layout(height=600, xaxis_rangeslider_visible=False, template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# Recent data
st.subheader("Recent Prices & Indicators")
st.dataframe(df.tail(10)[["Close", "RSI", "MACD", "MACD_signal", "EMA20", "EMA50"]].round(2))

st.caption(f"Last updated: {datetime.now().strftime('%d %B %Y • %H:%M UTC')} • Data from Supabase")
