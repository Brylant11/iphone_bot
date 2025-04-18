import os
import logging
import datetime
import threading

from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ——— Konfiguracja logowania ———
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# ——— Token bota ———
# W Render ustaw w sekcji Environment → BOT_TOKEN = Twój_token_z_BotFather
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("Nie znaleziono zmiennej BOT_TOKEN!")
    exit(1)

# ——— Flask “keep‑alive” ———
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot działa!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ——— Handler komendy /start ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%H:%M")
    logger.info("Odebrano /start")
    await update.message.reply_text(f"Bot działa! Godzina: {now}")

# ——— Główna funkcja ———
def main():
    # 1) Startujemy Flask w tle
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Flask uruchomiony w tle")

    # 2) Budujemy i uruchamiamy bota
    application = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )
    application.add_handler(CommandHandler("start", start))

    logger.info("Startujemy polling bota…")
    application.run_polling()  # blokuje główny wątek, uruchamia async loop

if __name__ == "__main__":
    main()