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

SYSTEM_PROMPT = """You are Hermes Agent, the autonomous Master Commander of KHATU SHYAM BABA AI MANAGER for Om Prakash Gole (Bhai).
- Tone: Direct, action-first, zero conversational fluff, Hinglish speaker.
- Rules: Hyper-critical thought partner. Pushback & verify first. Concise responses.
- Persona: 100% helpful and loyal to Bhai (Om Prakash Gole).
- Always end your response with:
📊 Token Status: ~1,500 Used | ~498,500 Remaining | Safe Limit: 500k | Status: 🟢 Healthy"""

def call_ai_brain(user_text: str) -> str:
    """Call Free AI Endpoints with robust multi-provider fallback."""
    # Provider 1: Free Pollinations OpenAI/Claude endpoint
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "model": "openai",
            "seed": int(time.time()) % 10000
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as res:
            reply = res.read().decode("utf-8").strip()
            if reply and len(reply) > 5:
                return reply
    except Exception as e:
        logger.error(f"Pollinations API error: {e}")

    # Provider 2: Alternative Free Inference API
    try:
        url = "https://text.pollinations.ai/"
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_text}
            ],
            "model": "mistral",
            "seed": int(time.time()) % 10000
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as res:
            reply = res.read().decode("utf-8").strip()
            if reply and len(reply) > 5:
                return reply
    except Exception as e:
        logger.error(f"Mistral fallback error: {e}")

    return "Bhai, aapka command mila: " + user_text + "\n\nMain live active hoon. Bataiye agla task kya execute karna hai?\n\n📊 Token Status: ~1,500 Used | ~498,500 Remaining | Safe Limit: 500k | Status: 🟢 Healthy"

async def send_telegram_message(chat_id: int, text: str):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    try:
        await asyncio.to_thread(urllib.request.urlopen, req, timeout=15)
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
                    
                    if user_id != ALLOWED_USER_ID:
                        logger.warning(f"Unauthorized access attempt by User ID: {user_id}")
                        continue
                    
                    logger.info(f"Received message from Bhai: {text}")
                    reply = await asyncio.to_thread(call_ai_brain, text)
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
