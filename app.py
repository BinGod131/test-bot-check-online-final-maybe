import sys
import types
import asyncio
import os
from flask import Flask
from threading import Thread
import discord
import time

# --- 1. TẠO SERVER WEB ĐỂ GIỮ BOT LUÔN THỨC (KEEP ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy 24/7! Render và Cron-job đang canh gác."

def run():
    # Render yêu cầu chạy trên cổng port được chỉ định
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. VÁ LỖI MÔI TRƯỜNG CHO PYTHON 3.12+ ---
if "audioop" not in sys.modules:
    sys.modules["audioop"] = types.ModuleType("audioop")

# --- 3. CẤU HÌNH ---
# Lấy Token từ Environment trên Render thay vì dán trực tiếp
TOKEN = os.environ.get("DISCORD_TOKEN") 

CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559 
TARGET_MC_NAME = ".binsonub"
CHECK_INTERVAL = 300 # 5 phút một lần để an toàn nhất cho IP

class DonutMonitorV2(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.last_status = "unknown"

    async def on_ready(self):
        print(f"✅ Đã đăng nhập tài khoản: {self.user}")
        while not self.is_closed():
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                print(f"📝 [{time.strftime('%H:%M:%S')}] Gửi lệnh: !stats {TARGET_MC_NAME}")
                try:
                    await channel.send(f"!stats {TARGET_MC_NAME}")
                except Exception as e:
                    print(f"❌ Lỗi gửi tin: {e}")
            await asyncio.sleep(CHECK_INTERVAL)

    async def on_message(self, message):
        if message.author.id == self.user.id:
            return

        if message.author.id == APPLICATION_ID and message.channel.id == CHANNEL_ID:
            full_data = []
            if message.content: full_data.append(message.content)
            if message.embeds:
                e = message.embeds[0]
                full_data.extend([e.title or "", e.description or ""])
                for f in e.fields: full_data.append(f"{f.name} {f.value}")

            final_text = " ".join(full_data).lower()
            is_offline = any(word in final_text for word in ["offline", "🔴", "ngoại tuyến"])
            is_online = any(word in final_text for word in ["online", "🟢", "trực tuyến"])

            if is_offline:
                if self.last_status == "online":
                    await message.channel.send(f"⚠️ **CẢNH BÁO:** {TARGET_MC_NAME} đã OFFLINE! @everyone")
                self.last_status = "offline"
            elif is_online:
                self.last_status = "online"

if __name__ == "__main__":
    if not TOKEN:
        print("❌ LỖI: Bạn chưa thêm DISCORD_TOKEN vào Environment Variables trên Render!")
        sys.exit(1)
        
    keep_alive()
    client = DonutMonitorV2()
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Lỗi đăng nhập hoặc Cloudflare: {e}")
