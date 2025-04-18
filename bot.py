from keep_alive import keep_alive
import datetime
import asyncio
from telegram.ext import Application, CommandHandler

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # Upewnij się, że prawidłowy

# Funkcja startowa
async def start(update, context):
    await update.message.reply_text("Witaj, bot działa!")

async def run_bot():
    app = Application.builder().token(TOKEN).build()

    await app.bot.delete_webhook(drop_pending_updates=True)  # <== To ważne!
    app.add_handler(CommandHandler("start", start))

    print("Bot wystartował!")

    await app.initialize()
    await app.start()

    while True:
        current_hour = datetime.datetime.now().hour
        if 8 <= current_hour < 20:
            await asyncio.sleep(10)
        else:
            print("Poza godzinami pracy (8–20), bot śpi 😴")
            await asyncio.sleep(60 * 10)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(run_bot())