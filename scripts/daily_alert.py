import os
from supabase import create_client
from scripts.signals import add_indicators, generate_signal, get_support_resistance
from scripts.discord_notify import send_alert
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def run_daily_alert():
    symbols = ["AAPL","MSFT","NVDA","TSLA","GOOGL","BTC","ETH","SOL","ADA","DOGE"]
    strong_signals = []

    for sym in symbols:
        try:
            resp = supabase.table("daily_prices").select("*").eq("symbol", sym).order("date").limit(200).execute()
            df = pd.DataFrame(resp.data)
            df["date"] = pd.to_datetime(df["date"])
            df = df.set_index("date")
            df = add_indicators(df)
            latest = df.iloc[-1]
            signal = generate_signal(latest)
            support, resistance, s1, r1 = get_support_resistance(df)

            if "STRONG" in signal or signal in ["BUY", "SELL"]:
                details = f"RSI {latest.RSI:.1f}"
                if latest.MACD > latest.MACD_signal: details += " • MACD Bullish"
                if latest.MACD < latest.MACD_signal: details += " • MACD Bearish"
                strong_signals.append((sym, signal, latest.Close, details, support, resistance))
        except: pass

    # ส่ง Discord
    if strong_signals:
        message = "Alpha Edge — Daily Signal Alert\n" + "\n".join([
            f"**{sym}-USD • {sig}**\nPrice: `${price:,.2f}`\n{det}\nSupport: `{sup}` | Resistance: `{res}`"
            for sym,sig,price,det,sup,res in strong_signals
        ]) + "\n\nLive Dashboard → https://jkdevelopx-alpha-edge.streamlit.app"
        import requests
        requests.post(os.getenv("DISCORD_WEBHOOK_URL"), json={"content": message})
    else:
        requests.post(os.getenv("DISCORD_WEBHOOK_URL"), json={"content": "Alpha Edge — Daily Alert\nNo strong signals today. Market is calm."})

if __name__ == "__main__":
    run_daily_alert()
