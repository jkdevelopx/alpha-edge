from scripts.discord_notify import send_alert
from scripts.signals import add_indicators, generate_signal
import pandas as pd
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# ดึง BTC ล่าสุด
data = supabase.table("daily_prices").select("*").eq("symbol", "BTC").order("date", desc=True).limit(200).execute()
df = pd.DataFrame(data.data)
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()
df = add_indicators(df)
latest = df.iloc[-1]
signal = generate_signal(latest)

# ส่งเข้า Discord ทันที!
send_alert("BTC-USD", signal, latest.Close)
print(f"ส่งแล้ว! → {signal} at ${latest.Close:,.2f}")
