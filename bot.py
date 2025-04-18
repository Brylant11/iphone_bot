from keep_alive import keep_alive
import asyncio
from telegram.ext import Application, CommandHandler
from threading import Thread

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # Wstaw tutaj swój token

# Funkcja startowa
async def start(update, context):
    print("Odebrano komendę /start")
    await update.message.reply_text("Witaj, bot działa!")

# Funkcja do uruchamiania bota
async def run_bot():
    app = Application.builder().token(TOKEN).build()

    # Usuń webhooka (ważne przy pracy na polling)
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Rejestruj komendy
    app.add_handler(CommandHandler("start", start))

    print("Bot wystartował!")

    # Startuj bota
    await app.run_polling()

# Funkcja do uruchamiania Flask w tle
def run_flask():
    keep_alive()  # Uruchomienie Flask bez portu

# Funkcja do uruchomienia wszystkiego
def start_all():
    # Uruchomienie Flask w osobnym wątku
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Utworzenie pętli zdarzeń
    loop = asyncio.get_event_loop()

    # Uruchomienie zadania bota w pętli
    loop.create_task(run_bot())

    # Uruchomienie pętli zdarzeń
    loop.run_forever()

if __name__ == "__main__":
    start_all()