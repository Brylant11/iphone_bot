# bot.py
from keep_alive import keep_alive
import time
import datetime
import asyncio
from telegram.ext import Application, CommandHandler

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"

# Funkcja startowa
async def start(update, context):
    print(f"Command received: {update.message.text}")  # Dodaj to do logów
    await update.message.reply_text("Witaj, bot działa!")

# Główna funkcja
async def run_bot():
    keep_alive()  # <- URUCHAMIAMY serwer Flask
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    print("Bot wystartował!")

    await app.initialize()
    await app.start()

    try:
        while True:
            current_hour = datetime.datetime.now().hour
            if 8 <= current_hour < 20:
                await asyncio.sleep(10)
            else:
                print("Poza godzinami pracy (8–20), bot śpi 😴")
                await asyncio.sleep(60 * 10)
    finally:
        await app.stop()
        await app.shutdown()

# Start wszystkiego
if __name__ == "__main__":
    asyncio.run(run_bot())