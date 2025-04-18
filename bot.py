import logging
import threading
import time
import datetime
import asyncio  # Dodajemy import asyncio, aby naprawić błąd
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from keep_alive import keep_alive  # Jeśli potrzebujesz keep_alive

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # Wstaw swój token bota

# Funkcja do startu bota
async def start(update, context):
    current_time = datetime.datetime.now().strftime("%H:%M")
    await update.message.reply_text(f"Bot jest aktywny! Aktualny czas: {current_time}")

# Funkcja, aby bot działał tylko w określonych godzinach (8:00-20:00)
async def check_time(update, context):
    now = datetime.datetime.now()
    if now.hour >= 8 and now.hour < 20:
        await update.message.reply_text("Bot jest aktywny.")
    else:
        await update.message.reply_text("Bot nie jest aktywny. Przepraszamy, wróć później.")

# Funkcja scrapowania OLX (przykład, wymaga implementacji scrapowania)
def scrap_olx():
    # Tutaj dodaj kod scrapujący OLX
    print("Scrapowanie OLX...")

# Funkcja do uruchamiania scrapowania co np. 5 minut
def start_scraping():
    while True:
        scrap_olx()
        time.sleep(300)  # czekaj 5 minut

# Funkcja uruchamiająca bota
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    # Komendy
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, check_time))

    # Startowanie bota
    await app.run_polling()

# Funkcja uruchamiająca Flask w tle
def run_flask():
    keep_alive()  # Uruchomienie Flask (jeśli potrzeba)

# Funkcja uruchamiająca bota w tle
def start_bot_in_background():
    loop = asyncio.get_event_loop()  # Tworzymy pętlę wydarzeń asyncio
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