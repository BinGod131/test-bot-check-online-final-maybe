import sys
import types
import asyncio
import os
from flask import Flask
from threading import Thread

# --- 1. TẠO SERVER WEB ĐỂ GIỮ BOT LUÔN THỨC (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy 24/7! Đừng lo, Render sẽ không cho tôi ngủ đâu."

def run():
    # Render yêu cầu chạy trên port 8080 hoặc port được chỉ định
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True # Đảm bảo thread này tắt khi chương trình chính tắt
    t.start()

# --- 2. VÁ LỖI MÔI TRƯỜNG (CHO PYTHON 3.12+) ---
if "audioop" not in sys.modules:
    sys.modules["audioop"] = types.ModuleType("audioop")

import discord

# --- 3. CẤU HÌNH BOT ---
# Lấy Token từ Environment Variables trên Render
TOKEN = os.getenv('DISCORD_TOKEN')

CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559 
TARGET_MC_NAME = ".binsonub"
CHECK_INTERVAL = 120  # Kiểm tra mỗi 2 phút

class MCStatusBot(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_status = "unknown"

    async def on_ready(self):
        print(f"✅ Đã kết nối Discord: {self.user}")
        print(f"📡 Đang giám sát người chơi: {TARGET_MC_NAME}")
        
        while not self.is_closed():
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                try:
                    # Gửi lệnh !stats vào channel
                    await channel.send(f"!stats {TARGET_MC_NAME}")
                except Exception as e:
                    print(f"❌ Lỗi gửi lệnh: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

    async def on_message(self, message):
        # Lắng nghe phản hồi từ bot DonutStats
        if message.author.id == APPLICATION_ID and message.channel.id == CHANNEL_ID:
            full_data = [message.content or ""]
            if message.embeds:
                e = message.embeds[0]
                full_data.extend([e.title or "", e.description or ""])
                for f in e.fields:
                    full_data.append(f"{f.name} {f.value}")
            
            content = " ".join(full_data).lower()
            
            # Kiểm tra từ khóa Online/Offline
            is_offline = any(x in content for x in ["offline", "🔴", "ngoại tuyến"])
            is_online = any(x in content for x in ["online", "🟢", "trực tuyến"])

            if is_offline:
                if self.last_status == "online":
                    await message.channel.send(f"⚠️ **CẢNH BÁO:** {TARGET_MC_NAME} đã thoát game! @everyone")
                self.last_status = "offline"
                print(f"🔴 Trạng thái: {TARGET_MC_NAME} đang Offline")
            elif is_online:
                self.last_status = "online"
                print(f"🟢 Trạng thái: {TARGET_MC_NAME} đang Online")

if __name__ == "__main__":
    if not TOKEN:
        print("❌ LỖI: Thiếu biến DISCORD_TOKEN trong Environment Variables!")
    else:
        # Chạy server Flask trước khi chạy Bot Discord
        keep_alive()
        
        client = MCStatusBot()
        client.run(TOKEN.strip())