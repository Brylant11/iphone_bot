from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import asyncio
import os
import threading

# Token bota
TOKEN = os.getenv("BOT_TOKEN") or "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"

app_flask = Flask(__name__)

# Endpoint żeby Render nie usypiał bota
@app_flask.route('/')
def home():
    return "Bot działa."

# Komenda testowa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Komenda '/start' została wywołana.")
    current_hour = datetime.now().hour
    print(f"Aktualna godzina: {current_hour}")
    
    if 8 <= current_hour < 20:
        await update.message.reply_text("Cześć! Bot działa 🚀")
    else:
        await update.message.reply_text("Bot śpi 😴 (dostępny od 8:00 do 20:00)")

# Funkcja uruchamiająca bota
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    print("🔄 Bot startuje...")
    await app.run_polling()
    print("✅ Bot działa.")

# Funkcja startująca Flask + Bota w osobnych wątkach
def start_all():
    # Flask działa w osobnym wątku
    threading.Thread(target=lambda: app_flask.run(host="0.0.0.0", port=10000)).start()

    # Bot działa na głównym wątku
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())
    
    print("Scrapowanie OLX...")  # Lub inne logi
    # Aplikacja Flask działa w tle

# Start całej apki
if __name__ == "__main__":
    start_all()