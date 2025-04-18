import logging
import asyncio
import datetime
import time
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from keep_alive import keep_alive  # Jeśli masz funkcję keep_alive, żeby utrzymać aplikację aktywną

# Ustawienie logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Token bota (wstaw swój token)
TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"

# Funkcja do startu bota
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_time = datetime.datetime.now().strftime("%H:%M")
    await update.message.reply_text(f"Bot jest aktywny! Aktualny czas: {current_time}")

# Funkcja, aby bot działał tylko w określonych godzinach (8:00-20:00)
async def check_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()
    if now.hour >= 8 and now.hour < 20:
        await update.message.reply_text("Bot jest aktywny.")
    else:
        await update.message.reply_text("Bot nie jest aktywny. Przepraszamy, wróć później.")

# Funkcja scrapowania OLX (przykład, wymaga implementacji scrapowania)
def scrap_olx():
    # Tutaj dodaj kod scrapujący OLX
    logger.info("Scrapowanie OLX...")  # Logowanie scrapowania OLX

# Funkcja do uruchamiania scrapowania co np. 5 minut
def start_scraping():
    while True:
        scrap_olx()
        time.sleep(300)  # czekaj 5 minut

# Funkcja uruchamiająca bota
async def run_bot():
    logger.info("🔄 Bot startuje...")  # Logowanie startu bota
    try:
        app = Application.builder().token(TOKEN).build()

        # Komendy
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT, check_time))

        # Startowanie bota
        await app.run_polling()
        logger.info("✅ Bot działa.")  # Logowanie, gdy bot zacznie działać
    except Exception as e:
        logger.error(f"❌ Błąd podczas uruchamiania bota: {e}")  # Logowanie błędu, jeśli wystąpi

# Funkcja uruchamiająca Flask w tle
def run_flask():
    keep_alive()  # Uruchomienie Flask (jeśli potrzeba)

# Funkcja uruchamiająca bota w tle
def start_bot_in_background():
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # Dodajemy zadanie do pętli zdarzeń

    logger.info("🔄 Bot uruchomiony w tle.")  # Logowanie, że bot jest uruchomiony w tle

# Funkcja do uruchomienia wszystkiego
def start_all():
    logger.info("🔄 Uruchamiam wszystkie usługi...")

    # Uruchomienie scrapowania w osobnym wątku
    scraping_thread = Thread(target=start_scraping)
    scraping_thread.start()

    # Uruchomienie Flask w osobnym wątku
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Uruchomienie bota w tle
    start_bot_in_background()

    logger.info("✅ Wszystko uruchomione.")

if __name__ == "__main__":
    start_all()