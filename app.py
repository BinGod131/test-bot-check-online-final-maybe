import sys, types, asyncio, os, discord
from flask import Flask
from threading import Thread

# 1. Khởi tạo Web Server
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# 2. Vá lỗi môi trường
if "audioop" not in sys.modules:
    sys.modules["audioop"] = types.ModuleType("audioop")

# 3. Cấu hình Bot (Thay Token của bạn vào đây)
TOKEN = "MTE0MDg4OTgxNTYwOTUyODM2MA.GxkmaN.5yuoiiGZ_5U-3G4jPBRgKJ4NTmiM4c6kD-T4rs"
CHANNEL_ID = 1418599629020463226
APPLICATION_ID = 1321520416677695559

class MyBot(discord.Client):
    async def on_ready(self):
        print(f'✅ Đã vào: {self.user}')
        while not self.is_closed():
            ch = self.get_channel(CHANNEL_ID)
            if ch:
                await ch.send(f"!stats .binsonub")
            await asyncio.sleep(180) # Tăng lên 3 phút để tránh bị chặn IP

if __name__ == "__main__":
    keep_alive()
    client = MyBot()
    # Thêm delay 5 giây để tránh gửi request quá nhanh khi Render khởi động
    import time
    time.sleep(5)
    client.run(TOKEN)
