import sys
import types
import asyncio
import os
from flask import Flask
from threading import Thread
import discord
import time

# --- 1. TẠO SERVER WEB (FLASK) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Live! Gunicorn is running."

# Hàm này để khởi chạy bot Discord trong một luồng riêng
def run_discord_bot():
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        print("❌ LỖI: Thiếu DISCORD_TOKEN trong Environment Variables!")
        return

    # Vá lỗi Python 3.12+
    if "audioop" not in sys.modules:
        sys.modules["audioop"] = types.ModuleType("audioop")

    client = DonutMonitorV2()
    try:
        client.run(token)
    except Exception as e:
        print(f"❌ Lỗi đăng nhập: {e}")

# --- 2. CẤU HÌNH BOT ---
CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559 
TARGET_MC_NAME = ".binsonub"
CHECK_INTERVAL = 300 

class DonutMonitorV2(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_status = "unknown"

    async def on_ready(self):
        print(f"✅ Đã đăng nhập: {self.user}")
        while not self.is_closed():
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                print(f"📝 [{time.strftime('%H:%M:%S')}] Gửi lệnh: !stats {TARGET_MC_NAME}")
                try:
                    await channel.send(f"!stats {TARGET_MC_NAME}")
                except Exception as e:
                    print(f"❌ Lỗi: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

    async def on_message(self, message):
        if message.author.id == self.user.id: return
        if message.author.id == APPLICATION_ID and message.channel.id == CHANNEL_ID:
            full_data = [message.content or ""]
            if message.embeds:
                e = message.embeds[0]
                full_data.extend([e.title or "", e.description or ""])
                for f in e.fields: full_data.append(f"{f.name} {f.value}")
            
            final_text = " ".join(full_data).lower()
            if any(word in final_text for word in ["offline", "🔴"]):
                if self.last_status == "online":
                    await message.channel.send(f"⚠️ **CẢNH BÁO:** {TARGET_MC_NAME} đã OFFLINE! @everyone")
                self.last_status = "offline"
            elif any(word in final_text for word in ["online", "🟢"]):
                self.last_status = "online"

# --- 3. KHỞI CHẠY BOT TRONG BACKGROUND ---
# Khi Gunicorn chạy app, nó sẽ thực hiện lệnh này một lần
t = Thread(target=run_discord_bot)
t.daemon = True
t.start()
