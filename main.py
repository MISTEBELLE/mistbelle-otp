from pyrogram import Client
import asyncio
import os
from dotenv import load_dotenv
import logging

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")

logging.basicConfig(level=logging.INFO)

app = Client(
    "mistbelle_auto",
    api_id=API_ID,
    api_hash=API_HASH,
    phone_number=PHONE,
    device_model="Railway",
    system_version="1.0",
    app_version="1.0"
)

async def main():
    await app.start()
    logging.info("✅ Bot berhasil terkoneksi ke Telegram!")
    await asyncio.Event().wait()   # keep running

if __name__ == "__main__":
    asyncio.run(main())
