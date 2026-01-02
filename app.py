import os, sys, types, asyncio, discord, time
from flask import Flask

# --- 1. PHẦN WEB (Dành cho Gunicorn) ---
app = Flask('')
@app.route('/')
def home():
    return "Web server is running!"

# --- 2. PHẦN BOT (Dành cho python app.py) ---
if "audioop" not in sys.modules:
    sys.modules["audioop"] = types.ModuleType("audioop")

TOKEN = os.environ.get("DISCORD_TOKEN")
CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559 
TARGET_MC_NAME = ".binsonub"
CHECK_INTERVAL = 300 

class DonutMonitorV2(discord.Client):
    async def on_ready(self):
        print(f"✅ Bot Online: {self.user}")
        while not self.is_closed():
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                await channel.send(f"!stats {TARGET_MC_NAME}")
            await asyncio.sleep(CHECK_INTERVAL)

# Lệnh này đảm bảo Bot CHỈ chạy khi gọi 'python app.py'
if __name__ == "__main__":
    client = DonutMonitorV2()
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Lỗi: {e}")
