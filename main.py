from pyrogram import Client
import asyncio
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# ================== CONFIG ==================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

app = Client("mistbelle_auto", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

async def main():
    logging.info("🚀 Sedang mencoba login ke Telegram...")
    try:
        await app.start()
        logging.info("✅ Berhasil terkoneksi ke Telegram!")
        logging.info("Bot sedang berjalan... (tekan Ctrl+C untuk stop)")
    except Exception as e:
        logging.error(f"Error: {e}")
    
    await asyncio.sleep(999999)  # keep running

if name == "main":
    asyncio.run(main())
