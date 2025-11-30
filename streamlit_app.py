import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from supabase import create_client
from scripts.signals import add_indicators, generate_signal
from datetime import datetime
import os
from dotenv import load_dotenv

# โหลด .env ก่อนเสมอ
load_dotenv()

# ดึงค่าจาก .env
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Missing Supabase credentials. Check your .env file.")
    st.stop()

# เชื่อมต่อ Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Page config
st.set_page_config(page_title="Alpha Edge", layout="wide", page_icon="Chart Increasing")

st.markdown("# Alpha Edge")
st.markdown("**Quantitative Trading Dashboard** • Real-time Signals • Strategy Analysis")

# Sidebar
@st.cache_data(ttl=3600)
def get_symbols():
    try:
        data = supabase.table("daily_prices").select("symbol").execute()
        return sorted({row["symbol"] for row in data.data})
    except Exception as e:
        st.error(f"Cannot connect to database: {e}")
        return ["BTC"]

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

# สัญญาณล่าสุด
latest = df.iloc[-1]
signal = generate_signal(latest)

# Metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Price", f"${latest.Close:,.2f}")
with col2:
    st.metric("RSI (14)", f"{latest.RSI:.1f}")
with col3:
    st.metric("MACD", f"{latest.MACD:.4f}")
with col4:
    color = "green" if "BUY" in signal else "red" if "SELL" in signal else "gray"
    st.markdown(f"**Signal**  \n<span style='font-size:2em;color:{color}'>{signal}</span>", unsafe_allow_html=True)

# Chart
fig = go.Figure()
fig.add_trace(go.Candlestick(x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close, name="Price"))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA20, name="EMA20", line=dict(color="#00ff88")))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA50, name="EMA50", line=dict(color="#ff00ff")))
fig.add_trace(go.Scatter(x=df.index, y=df.EMA200, name="EMA200", line=dict(color="#ff0066")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_upper, name="BB Upper", line=dict(dash="dot", color="gray")))
fig.add_trace(go.Scatter(x=df.index, y=df.BB_lower, name="BB Lower", line=dict(dash="dot", color="gray")))

fig.update_layout(height=650, template="plotly_dark", xaxis_rangeslider_visible=False)
st.plotly_chart(fig, use_container_width=True)

# ตาราง
st.subheader("Recent Data & Indicators")
st.dataframe(df.tail(10)[["Close","RSI","MACD","MACD_signal","EMA20","EMA50","BB_upper","BB_lower"]].round(3))

st.caption(f"Last updated: {datetime.now().strftime('%d %B %Y • %H:%M UTC')} • Powered by Supabase + yfinance")
