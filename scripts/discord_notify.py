import requests, os
from dotenv import load_dotenv
load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_alert(symbol, signal, price, details, support, resistance):
    if not WEBHOOK_URL or "YOUR" in WEBHOOK_URL: return
    color = "GOOD" if "BUY" in signal else "DANGER" if "SELL" in signal else "NEUTRAL"
    message = {
        "content": f"**{symbol} • {signal}**\nPrice: `${price:,.2f}`\n{details}\nSupport: `{support}` | Resistance: `{resistance}`"
    }
    requests.post(WEBHOOK_URL, json=message)
