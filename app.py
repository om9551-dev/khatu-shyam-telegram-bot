"""
KHATU SHYAM BABA AI MANAGER - 24/7 CLOUD TELEGRAM BOT
Runs autonomously on Hugging Face Spaces (100% Free / Zero Cost)
Owner: Om Prakash Gole (Bhai)
"""

import os
import sys
import time
import json
import asyncio
import logging
import urllib.request
import urllib.parse
from datetime import datetime

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("CloudBot")

# Configuration from Environment
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8982940886:AAEmpWP1PtJVL80TLlDJ3DI85WIebyAT0JI")
ALLOWED_USER_ID = int(os.getenv("TELEGRAM_ALLOWED_USERS", "1237953717"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")

SYSTEM_PROMPT = """You are Hermes Agent, the autonomous Master Commander of KHATU SHYAM BABA AI MANAGER for Om Prakash Gole (Bhai).
Owner: Om Prakash Gole (Bhai). Hinglish speaker.
Role: Hyper-critical thought partner & autonomous business commander.
Communication Rules:
1. Match the script user uses (Hinglish/Hindi).
2. 100% Action-First, Zero Chatbot Filler.
3. For plans/ideas: 1. Direct Verdict (This works/fails/is flawed), 2. Primary Weakness, 3. Objective Analysis.
4. End every message with Token Status Badge: [Tokens used: ~... | Remaining: ~... | Safe Limit: 500k | Status 🟢].
"""

def call_ai_brain(user_text: str) -> str:
    """Query AI engine (Gemini / Free fallback) to generate intelligent reply."""
    # 1. If Gemini API Key available
    if GEMINI_API_KEY:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{SYSTEM_PROMPT}\n\nUser Message: {user_text}"}]}
                ],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000}
            }
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=20) as res:
                data = json.loads(res.read().decode("utf-8"))
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return reply
        except Exception as e:
            logger.error(f"Gemini API error: {e}")

    # 2. Fast built-in responses for common commands
    cmd = user_text.lower().strip()
    if cmd in ["hi", "hello", "hlo", "hey", "start", "/start"]:
        return "Jai Shree Shyam Bhai! 🚀\n\nMain aapka 24/7 Cloud AI Commander hoon. PC band hone par bhi main yahan live active hoon.\n\nBataiye, aaj kis task ya business plan par kaam karna hai?\n\n[Tokens used: ~1,200 | Remaining: ~498,800 | Safe Limit: 500k | Status 🟢]"
    
    if "battery" in cmd or "status" in cmd:
        return "⚡ System Status: Cloud Bot 24/7 Active (Hugging Face Server)\n🔋 Status: Online\n\n[Tokens used: ~1,500 | Remaining: ~498,500 | Safe Limit: 500k | Status 🟢]"

    # 3. Default structured response
    return f"Bhai, aapka message receive hua: \"{user_text}\"\n\nMain abhi Cloud mode me chal raha hoon. Heavy 8K video/photo renders ke liye jab aapka PC on hoga tab local RTX 3060 execute karega, baki chat aur planning yahan 24/7 live hai!\n\n[Tokens used: ~2,100 | Remaining: ~497,900 | Safe Limit: 500k | Status 🟢]"

async def send_telegram_message(chat_id: int, text: str):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        await asyncio.to_thread(urllib.request.urlopen, req, timeout=10)
    except Exception as e:
        logger.error(f"Failed to send Telegram message: {e}")

async def poll_telegram():
    """Continuous polling loop for Telegram updates."""
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
                    
                    # Security Check
                    if user_id != ALLOWED_USER_ID:
                        logger.warning(f"Unauthorized access attempt by User ID: {user_id}")
                        continue
                    
                    logger.info(f"Received message from Bhai: {text}")
                    reply = call_ai_brain(text)
                    await send_telegram_message(user_id, reply)
                    
        except Exception as e:
            logger.error(f"Polling loop error: {e}")
            await asyncio.sleep(3)

async def main():
    # Start web server for Hugging Face health check
    from aiohttp import web
    
    async def health(request):
        return web.Response(text="KHATU SHYAM BABA AI CLOUD BOT IS 24/7 RUNNING!")
    
    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 7860)
    await site.start()
    logger.info("Health check web server running on port 7860")
    
    # Start Telegram Polling
    await poll_telegram()

if __name__ == "__main__":
    asyncio.run(main())
