import sys, types, asyncio, os, discord
from flask import Flask
from threading import Thread

# --- 1. KHỞI TẠO WEB SERVER (KEEP-ALIVE) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot đang chạy! Đừng lo, Render sẽ không cho tôi ngủ đâu."

def run():
    # Render yêu cầu chạy trên port được chỉ định hoặc mặc định 8080
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. VÁ LỖI MÔI TRƯỜNG (CHO RENDER/PYTHON 3.12+) ---
if "audioop" not in sys.modules:
    sys.modules["audioop"] = types.ModuleType("audioop")

# --- 3. CẤU HÌNH BOT ---
# Chú ý: Giữ nguyên Token này nếu bạn muốn dán thẳng vào code
TOKEN = "MTE0MDg4OTgxNTYwOTUyODM2MA.GxkmaN.5yuoiiGZ_5U-3G4jPBRgKJ4NTmiM4c6kD-T4rs"
CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559
TARGET_MC_NAME = ".binsonub"

# THỜI GIAN NGHỈ (300 giây = 5 phút)
# Nên để từ 300 trở lên để tránh bị Cloudflare chặn IP (Lỗi 1015)
CHECK_INTERVAL = 300 

class MyBot(discord.Client):
    async def on_ready(self):
        print(f'✅ Đã đăng nhập thành công tài khoản: {self.user}')
        
        while not self.is_closed():
            channel = self.get_channel(CHANNEL_ID)
            if channel:
                try:
                    await channel.send(f"!stats {TARGET_MC_NAME}")
                    print(f"[LOG] Đã gửi lệnh stats cho {TARGET_MC_NAME}")
                except Exception as e:
                    print(f"❌ Lỗi khi gửi tin nhắn: {e}")
            
            # Bot sẽ nghỉ theo thời gian bạn đã chỉnh ở trên
            await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Khởi động server web trước
    keep_alive()
    
    # Khởi tạo bot
    client = MyBot()
    
    # Thêm một khoảng nghỉ ngắn trước khi login để tránh gửi request dồn dập
    import time
    time.sleep(5)
    
    try:
        client.run(TOKEN)
    except Exception as e:
        print(f"❌ Lỗi đăng nhập hoặc bị Cloudflare chặn: {e}")
