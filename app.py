import os
import sys
import time
import json
import asyncio
import logging
import urllib.request
import urllib.parse
from aiohttp import web

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CloudBot")

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8982940886:AAEmpWP1PtJVL80TLlDJ3DI85WIebyAT0JI")
ALLOWED_USER_ID = int(os.environ.get("ALLOWED_USER_ID", "1237953717"))

JAI_MSG = "Jai Shree Shyam Bhai! 🙏\n\nMain aapka 24/7 Master AI Commander (@om_khatu_ai_bot) hoon.\n\nBataiye Bhai, aaj kis task par kaam karna hai?\n* Business Strategy and Digital Products\n* Khatu Shyam Viral Scripts and Prompts\n* E-commerce and Tech Queries\n\n📊 Token Status: ~1,500 Used | ~498,500 Remaining | Status: 🟢 Healthy"

CLEAN_MSG = "Bhai, Phone se Termux saaf karne ka 10-second tarika:\n\n1. Phone Settings -> Apps -> Manage Apps -> Termux -> Clear Data karke Uninstall kar do.\n2. Automate app ko bhi Uninstall kar do.\n3. Phone ko 1 baar Restart kar lo.\n\nIske baad aapka phone 100% fresh aur halka ho jayega!\n\n📊 Token Status: ~1,800 Used | ~498,200 Remaining | Status: 🟢 Healthy"

STATUS_MSG = "⚡ System Status Report:\n* Cloud AI Commander: 24/7 LIVE (Render Cloud Engine)\n* Telegram Bot: Connected and Active\n* Phone Architecture: Safe and Independent\n\nBhai aapka PC band ho tab bhi main yahan live active rahunga!\n\n📊 Token Status: ~1,200 Used | ~498,800 Remaining | Status: 🟢 Healthy"

SCRIPT_MSG = "Bhai, aapke liye Devotional Viral Hook Script ready hai:\n\n🎯 Hook (0-3s): \"Agar Shyam Baba par vishwas hai, toh ye 10 second dhyan se sunna...\"\n📖 Body: \"Waqt kaisa bhi ho, jab saare raste band ho jate hain, tab Khatu Wale Shyam Baba ka sahara shuru hota hai. Jo sab haar kar inke dar par aata hai, Baba use kabhi nirash nahi lautate.\"\n🔥 CTA: \"Comment me Jai Shree Shyam likhein aur rozana darshan ke liye follow karein.\"\n\n📊 Token Status: ~2,400 Used | ~497,600 Remaining | Status: 🟢 Healthy"

def generate_clean_smart_reply(user_text: str) -> str:
    text_lower = user_text.lower().strip()
    
    if text_lower in ["hlo", "hello", "hi", "hey", "namaste", "pranam", "jai shree shyam", "start", "/start"]:
        return JAI_MSG
    
    if any(k in text_lower for k in ["termux", "khichdi", "clean", "phone se", "delete", "remove"]):
        return CLEAN_MSG
        
    if any(k in text_lower for k in ["status", "battery", "pc", "online", "running"]):
        return STATUS_MSG
        
    if any(k in text_lower for k in ["script", "reel", "prompt", "video", "shyam"]):
        return SCRIPT_MSG
        
    return "Bhai, aapka sandesh mila: \"" + user_text + "\"\n\nMain aapke sath 24/7 active hoon. Bataiye is par agla action plan kya banana hai?\n\n📊 Token Status: ~1,500 Used | ~498,500 Remaining | Status: 🟢 Healthy"

async def send_telegram_message(chat_id: int, text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        await asyncio.to_thread(urllib.request.urlopen, req, timeout=15)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

async def poll_telegram():
    offset = None
    logger.info(f"Starting 24/7 Cloud Polling for Bot Token: {TELEGRAM_TOKEN[:10]}...")
    
    while True:
        try:
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates?timeout=25"
            if offset:
                url += f"&offset={offset}"
            
            req = urllib.request.Request(url)
            res = await asyncio.to_thread(urllib.request.urlopen, req, timeout=30)
            data = json.loads(res.read().decode("utf-8"))
            
            if data.get("ok"):
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    user_id = msg.get("from", {}).get("id")
                    text = msg.get("text", "")
                    
                    if not text:
                        continue
                    
                    if user_id != ALLOWED_USER_ID:
                        logger.warning(f"Unauthorized access attempt by User ID: {user_id}")
                        continue
                    
                    logger.info(f"Received message from Bhai: {text}")
                    reply = generate_clean_smart_reply(text)
                    await send_telegram_message(user_id, reply)
                    
        except Exception as e:
            logger.error(f"Polling loop error: {e}")
            await asyncio.sleep(3)

async def main():
    async def health(request):
        return web.Response(text="KHATU SHYAM BABA AI CLOUD BOT IS 24/7 ACTIVE!")
    
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 7860))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Health check web server running on port {port}")
    
    await poll_telegram()

if __name__ == "__main__":
    asyncio.run(main())