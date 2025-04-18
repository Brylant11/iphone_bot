import logging
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import threading
import time
import os

# Konfiguracja logowania
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Token bota
TOKEN = os.getenv("BOT_TOKEN") or "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"

# Tworzymy aplikację Flask
app_flask = Flask(__name__)

# Endpoint do Rendera, aby utrzymać bota aktywnego
@app_flask.route('/')
def home():
    return "Bot działa."

# Funkcja komendy /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.datetime.now().strftime("%H:%M")
    logger.info(f"Received /start command at {current_time}")
    await update.message.reply_text(f"Bot jest aktywny! Aktualny czas: {current_time}")

# Funkcja sprawdzająca, czy bot jest aktywny (8:00 - 20:00)
async def check_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    if 8 <= now.hour < 20:
        await update.message.reply_text("Bot jest aktywny.")
    else:
        await update.message.reply_text("Bot nie jest aktywny. Przepraszamy, wróć później.")

# Funkcja scrapowania (przykładowa)
def scrap_olx():
    logger.info("Scrapowanie OLX...")
    # Możesz tu dodać kod scrapowania OLX
    time.sleep(5)  # Przykładowe opóźnienie dla testów

# Funkcja uruchamiająca scrapowanie co 5 minut
def start_scraping():
    while True:
        scrap_olx()
        time.sleep(300)  # Czekaj 5 minut

# Funkcja uruchamiająca bota
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    # Dodanie handlerów
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_time))

    logger.info("🔄 Bot startuje...")
    await app.run_polling()
    logger.info("✅ Bot działa.")

# Funkcja uruchamiająca Flask w tle
def run_flask():
    app_flask.run(host='0.0.0.0', port=10000)

# Funkcja uruchamiająca bota w tle
def start_bot_in_background():
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())

# Funkcja uruchamiająca wszystkie usługi
def start_all():
    # Uruchomienie scrapowania w osobnym wątku
    scraping_thread = threading.Thread(target=start_scraping)
    scraping_thread.start()

    # Uruchomienie Flask w osobnym wątku
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Uruchomienie bota w tle
    start_bot_in_background()

    logger.info("🔄 Uruchamiam wszystkie usługi...")

if __name__ == "__main__":
    start_all()