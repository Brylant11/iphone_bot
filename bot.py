import time
from datetime import datetime
from telegram import Bot
from telegram.ext import Updater, CommandHandler

# Wprowadź swój token API bota (musisz go zdobyć na BotFather)
TOKEN = 'TWÓJ_TOKEN_Z_TELEGRAMU'  # Zamień na swój token

# Funkcja do sprawdzania godziny
def should_run():
    current_hour = datetime.now().hour
    # Bot działa tylko w godzinach 8:00 do 20:00
    return 8 <= current_hour < 20

# Komenda startowa, aby użytkownik wiedział, że bot działa
def start(update, context):
    update.message.reply_text('Cześć! Bot działa i będzie Cię informować o ofertach telefonów!')

# Funkcja do uruchomienia bota
def run_bot():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    # Dodanie komendy "/start"
    dp.add_handler(CommandHandler("start", start))

    updater.start_polling()

    # Główna pętla, która sprawdza godzinę i uruchamia zadanie bota
    while True:
        if should_run():
            print("Bot działa...")  # Tutaj będziesz mógł dodać logikę do zbierania ofert
            time.sleep(600)  # Sprawdzanie co 10 minut
        else:
            print("Bot jest teraz wyłączony (poza godzinami 8:00 - 20:00).")
            time.sleep(600)  # Czekaj 10 minut, aby ponownie sprawdzić godzinę

    updater.stop()

if __name__ == "__main__":
    run_bot()