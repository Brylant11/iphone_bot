from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
import datetime
import logging
from keep_alive import keep_alive  # importujemy keep_alive

# Ustawienie logów
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # Podstaw swój token bota

# Funkcja uruchamiająca bota
async def start(update, context):
    current_time = datetime.datetime.now().strftime("%H:%M")
    await update.message.reply_text(f"Bot jest aktywny! Aktualny czas: {current_time}")

# Funkcja sprawdzająca godzinę
async def check_time(update, context):
    now = datetime.datetime.now()
    if now.hour >= 8 and now.hour < 20:
        await update.message.reply_text("Bot jest aktywny.")
    else:
        await update.message.reply_text("Bot nie jest aktywny. Przepraszamy, wróć później.")

# Funkcja scrapowania OLX
def scrap_olx():
    print("Scrapowanie OLX...")

# Funkcja uruchamiania scrapowania co 5 minut
def start_scraping():
    while True:
        scrap_olx()
        time.sleep(300)

# Funkcja uruchamiająca bota
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_time))

    # Uruchomienie bota
    await app.run_polling()

# Funkcja uruchamiająca Flask w tle
def run_flask():
    keep_alive()  # Uruchomienie Flask, aby Render nie usypiał bota

# Funkcja uruchamiająca bota w tle
def start_bot_in_background():
    loop = asyncio.get_event_loop()
    loop.create_task(run_bot())  # Dodanie zadania bota do pętli zdarzeń

# Funkcja uruchamiająca wszystko
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