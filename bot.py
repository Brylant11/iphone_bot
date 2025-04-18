# bot.py
from keep_alive import keep_alive
import time
import datetime
import asyncio
from telegram.ext import Application, CommandHandler

TOKEN = "TU_WSTAW_TOKEN"  # <== Wklej tu swój token

# Funkcja startowa
async def start(update, context):
    print("Odebrano komendę /start")
    await update.message.reply_text("Witaj, bot działa!")

# Główna funkcja
async def run_bot():
    keep_alive()  # Start Flask serwera (anty-usypiacz)

    app = Application.builder().token(TOKEN).build()

    # Usuń webhooka (ważne przy pracy na polling)
    await app.bot.delete_webhook(drop_pending_updates=True)

    # Rejestruj komendy
    app.add_handler(CommandHandler("start", start))

    print("Bot wystartował!")

    # Startuj bota w tle
    await app.initialize()
    await app.start()

    while True:
        current_hour = datetime.datetime.utcnow().hour + 2  # CEST (UTC+2)
        if 8 <= current_hour < 20:
            print("Bot aktywny 🟢", datetime.datetime.now())
            await asyncio.sleep(10)
        else:
            print("Poza godzinami pracy 💤", datetime.datetime.now())
            await asyncio.sleep(60 * 10)  # 10 minut

# Start wszystkiego
if __name__ == "__main__":
    asyncio.run(run_bot())