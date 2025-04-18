from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import logging
from datetime import datetime
import asyncio
import threading
import time
from keep_alive import keep_alive  # Jeśli potrzebujesz keep_alive

# Konfiguracja logowania
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger()

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # Wstaw swój token bota

# Funkcja do startu bota
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.now().strftime("%H:%M")
    logger.info(f"Received /start command at {current_time}")
    await update.message.reply_text(f"Bot jest aktywny! Aktualny czas: {current_time}")

# Funkcja, aby bot działał tylko w określonych godzinach (8:00-20:00)
async def check_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    if now.hour >= 8 and now.hour < 20:
        logger.info("Bot działa w godzinach aktywności.")
        await update.message.reply_text("Bot jest aktywny.")
    else:
        logger.info("Bot jest poza godzinami aktywności.")
        await update.message.reply_text("Bot nie jest aktywny. Przepraszamy, wróć później.")

# Funkcja scrapowania OLX (przykład, wymaga implementacji scrapowania)
def scrap_olx():
    # Tutaj dodaj kod scrapujący OLX
    logger.info("Scrapowanie OLX...")

# Funkcja do uruchamiania scrapowania co np. 5 minut
def start_scraping():
    while True:
        scrap_olx()
        time.sleep(300)  # czekaj 5 minut

# Funkcja uruchamiająca bota
async def run_bot():
    app = ApplicationBuilder().token(TOKEN).build()

    # Komendy
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_time))

    # Startowanie bota
    logger.info("🔄 Uruchamiam bota...")
    await app.run_polling()
    logger.info("✅ Bot działa.")

# Funkcja uruchamiająca Flask w tle
def run_flask():
    keep_alive()  # Uruchomienie Flask (jeśli potrzeba)

# Funkcja uruchamiająca bota w tle
def start_bot_in_background():
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # Dodajemy zadanie do pętli zdarzeń

# Funkcja do uruchomienia wszystkiego
def start_all():
    # Uruchomienie scrapowania w osobnym wątku
    scraping_thread = threading.Thread(target=start_scraping)
    scraping_thread.start()

    # Uruchomienie Flask w osobnym wątku
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Uruchomienie bota w tle
    start_bot_in_background()

if __name__ == "__main__":
    start_all()