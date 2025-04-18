from keep_alive import keep_alive
import time
import datetime
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
    from keep_alive import keep_alive
    keep_alive(port=5000)  # Uruchomienie Flask na porcie 5000

# Start wszystkiego
if __name__ == "__main__":
    # Uruchomienie Flask w osobnym wątku
    flask_thread = Thread(target=run_flask)
    flask_thread.start()

    # Uruchomienie bota
    asyncio.run(run_bot())