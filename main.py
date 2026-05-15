from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
import re
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

load_dotenv()

# ================== CONFIG ==================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
PHONE = os.getenv("PHONE")
BOT_USERNAME = "msbelleotp_bot"
NOTIF_CHANNEL = os.getenv("NOTIF_CHANNEL")   # Kosongkan jika tidak pakai

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Client("mistbelle_auto", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

# ================== SETTING ==================
COUNTRIES = ["Indonesia", "United States"]
SERVICES = ["TELEGRAM", "WA"]

# Kata kunci untuk deteksi saldo kurang
LOW_BALANCE_KEYWORDS = ["saldo kurang", "insufficient", "balance not enough", "top up", "isi ulang", "tidak cukup"]

# ================== HELPER ==================
async def send_msg(text, delay=2.5):
    try:
        await app.send_message(BOT_USERNAME, text)
        await asyncio.sleep(delay)
        return True
    except Exception as e:
        logging.error(f"Gagal kirim: {e}")
        return False

async def send_notif(text):
    if NOTIF_CHANNEL:
        try:
            await app.send_message(NOTIF_CHANNEL, f"🔰 Mistbelle Auto\n{text}")
        except:
            pass

# ================== AUTO CANCEL KALAU SALDO KURANG ==================
async def cancel_and_refund():
    logging.info("🛑 Saldo kurang terdeteksi → Cancel & Refund")
    await send_msg("cancel", 2)
    await send_msg("refund", 2)
    await send_msg("ya", 2)
    await send_notif("⚠️ Saldo kurang → Order dibatalkan & refund diminta")

# ================== AUTO ORDER ==================
async def order_otp(service="TELEGRAM", country="Indonesia"):
    logging.info(f"🚀 Order → {country} | {service}")
    await send_notif(f"Memulai order\nNegara: {country}\nLayanan: {service}")

    try:
        await send_msg("/order", 3)
        await send_msg(country, 3)
        await send_msg(service, 4)

        logging.info("💰 Menunggu pembayaran...")
        await asyncio.sleep(7)

        logging.info("⏳ Menunggu nomor...")
        await send_notif("✅ Order terkirim, menunggu nomor...")

    except Exception as e:
        logging.error(f"Order gagal: {e}")
        await send_notif(f"❌ Order gagal: {e}")

# ================== AUTO AMBIL OTP + DETEKSI SALDO KURANG ==================
@app.on_message(filters.chat(BOT_USERNAME) & \~filters.me)
async def handle_bot_reply(client, message: Message):
    text = message.text or message.caption or ""
    if not text:
        return

    logging.info(f"Bot: {text[:300]}")

    # Cek saldo kurang
    if any(keyword in text.lower() for keyword in LOW_BALANCE_KEYWORDS):
        logging.warning("⚠️ Saldo kurang terdeteksi!")
        await send_notif("⚠️ Saldo kurang terdeteksi!")
        await cancel_and_refund()
        return

    # Deteksi nomor
    number_match = re.search(r'(\+?\d{10,15})', text)
    if number_match:
        nomor = number_match.group(1)
        logging.info(f"📱 Nomor: {nomor}")
        with open("nomor_aktif.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | {nomor}\n")
        await send_notif(f"📱 Nomor diterima:\n{nomor}")

    # Deteksi OTP
    otp_match = re.search(r'(?:kode|otp|code|verifikasi)[\s:]*(\d{4,10})', text, re.IGNORECASE) or re.search(r'\b(\d{5,8})\b', text)
    if otp_match:
        otp = otp_match.group(1)
        logging.info(f"🔑 OTP: {otp}")
        with open("otp_result.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()} | OTP: {otp}\n")
        await send_notif(f"🔑 OTP BERHASIL\n{otp}")

# ================== AUTO LOOP ==================
async def auto_loop(interval_minutes=8):
    while True:
        for country in COUNTRIES:
            for service in SERVICES:
                await order_otp(service=service, country=country)
                await asyncio.sleep(45)   # jeda antar order
logging.info(f"⏳ Tunggu {interval_minutes} menit untuk loop berikutnya...")
        await asyncio.sleep(interval_minutes * 60)

# ================== MAIN ==================
async def main():
    await app.start()
    logging.info("✅ Mistbelle Auto Order v3.1 BERJALAN (Indonesia & USA + Auto Cancel)")

    asyncio.create_task(auto_loop(interval_minutes=8))   # Ubah angka sesuai kebutuhan

    await asyncio.Event().wait()

if name == "main":
    asyncio.run(main())
