# bot.py
from keep_alive import keep_alive
import asyncio
import datetime
from telegram.ext import Application, CommandHandler

TOKEN = "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"  # <-- pamiętaj, schowaj go później ;)

# Komenda /start
async def start(update, context):
    print("Odebrano komendę /start")
    await update.message.reply_text("Witaj, bot działa!")

# Główna funkcja
async def run_bot():
    keep_alive()

    app = Application.builder().token(TOKEN).build()
    await app.bot.delete_webhook(drop_pending_updates=True)

    app.add_handler(CommandHandler("start", start))

    print("Bot wystartował i nasłuchuje!")

    # Tu najważniejsze: polling!
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(run_bot())