import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def send_alert(symbol, signal, price):
    if not WEBHOOK_URL or WEBHOOK_URL == "https://discord.com/api/webhooks/1444548741439815741/2FLPVF2W0XJiznw81vRHHTWfQeaH85MXdM92G0uuCjwYBL0OD3KP3gQYwLm5Hl1JNryG":
        return
    
    color = 0x00ff00 if "Buy" in signal else 0xff0000 if "Sell" in signal else 0x808080
    data = {
        "embeds": [{
            "title": f"{symbol} • {signal}",
            "description": f"Price: ${price:,.2f}",
            "color": color,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }]
    }
    requests.post(WEBHOOK_URL, json=data)
