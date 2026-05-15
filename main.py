from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
BOT_USERNAME = "msbelleotp_bot"
NOTIF_CHANNEL = os.getenv("NOTIF_CHANNEL")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Client("mistbelle_auto", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

COUNTRIES = ["Indonesia", "United States"]
SERVICES = ["TELEGRAM", "WA"]

# ================== HELPER ==================
async def send_msg(text, delay=2.5):
    try:
        await app.send_message(BOT_USERNAME, text)
        await asyncio.sleep(delay)
    except Exception as e:
        logging.error(f"Gagal kirim: {e}")

async def send_notif(text):
    if NOTIF_CHANNEL and NOTIF_CHANNEL.strip():
        try:
            await app.send_message(NOTIF_CHANNEL, f"🔰 Mistbelle Auto\n{text}")
        except:
            pass

async def cancel_and_refund():
    logging.info("🛑 Cancel & Refund")
    await send_msg("cancel", 2)
    await send_msg("refund", 2)
    await send_msg("ya", 2)
    await send_notif("🛑 Order dibatalkan")

async def order_otp(service="TELEGRAM", country="Indonesia"):
    logging.info(f"🚀 Order → {country} | {service}")
    await send_notif(f"Memulai order\nNegara: {country}\nLayanan: {service}")

    await send_msg("/order", 3)
    await send_msg(country, 3)
    await send_msg(service, 4)
    await asyncio.sleep(7)

# ================== HANDLER BOT ==================
async def handle_bot_reply(client, message: Message):
    text = message.text or message.caption or ""
    if not text:
        return

    logging.info(f"Bot: {text[:200]}")

    if any(kw in text.lower() for kw in ["saldo kurang", "insufficient", "balance not enough", "top up"]):
        await cancel_and_refund()
        return

    if number := re.search(r'(\+?\d{10,15})', text):
        await send_notif(f"📱 Nomor: {number.group(1)}")

    if otp := re.search(r'\b(\d{5,8})\b', text):
        await send_notif(f"🔑 OTP: {otp.group(1)}")

# Daftarkan handler dengan cara paling aman
app.add_handler(Client.on_message(filters.chat("msbelleotp_bot") & filters.me)(handle_bot_reply))

# ================== AUTO LOOP ==================
async def auto_loop():
    while True:
        for country in COUNTRIES:
            for service in SERVICES:
                await order_otp(service=service, country=country)
                await asyncio.sleep(50)
        await asyncio.sleep(8 * 60)

async def main():
    await app.start()
    logging.info("✅ Mistbelle Auto Order BERJALAN!")

    asyncio.create_task(auto_loop())
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
