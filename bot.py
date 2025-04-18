from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from datetime import datetime
import asyncio
import os

# Token bota
TOKEN = os.getenv("BOT_TOKEN") or "8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs"

# Tworzymy aplikację Flask
app_flask = Flask(__name__)

# Endpoint żeby Render nie usypiał bota
@app_flask.route('/')
def home():
    print("Flask działa!")  # Logowanie, aby sprawdzić, czy Flask działa
    return "Bot działa."

# Komenda testowa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_hour = datetime.now().hour
    if 8 <= current_hour < 20:
        await update.message.reply_text("Cześć! Bot działa 🚀")
    else:
        await update.message.reply_text("Bot śpi 😴 (dostępny od 8:00 do 20:00)")

# Funkcja uruchamiająca bota
async def run_bot():
    print("🔄 Bot startuje...")  # Logowanie przed uruchomieniem bota
    app = ApplicationBuilder().token(TOKEN).build()
    print("🔄 Bot zbudowany")  # Logowanie po zbudowaniu aplikacji

    app.add_handler(CommandHandler("start", start))
    print("🔄 Dodano handler")  # Logowanie po dodaniu handlera

    try:
        await app.run_polling()
    except Exception as e:
        print(f"❌ Błąd przy uruchomieniu bota: {e}")
    print("✅ Bot działa.")  # Logowanie po uruchomieniu bota

# Funkcja startująca Flask + Bota
def start_all():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    loop.create_task(run_bot())

    print("Scrapowanie OLX...")  # Logowanie przed uruchomieniem Flask
    app_flask.run(host="0.0.0.0", port=10000)

# Start całej apki
if __name__ == "__main__":
    start_all()