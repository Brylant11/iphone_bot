import os
import time
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from geopy.distance import geodesic
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
)

# ——— Konfiguracja logów ———
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ——— Token i URL webhooka ———
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BRAK TOKENA! Ustaw BOT_TOKEN.")
    exit(1)

# Render dostarcza własny URL w env RENDER_EXTERNAL_URL
BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
if not BASE_URL:
    logger.error("BRAK EXTERNAL URL! Ustaw RENDER_EXTERNAL_URL.")
    exit(1)
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = BASE_URL + WEBHOOK_PATH

# ——— Stałe i ceny ———
AVERAGE_PRICE = {
    'iphone x 64 gb': 650, 'iphone x 256 gb': 800,
    # ... (reszta z poprzedniego słownika) ...
    'iphone 13 pro max 512 gb': 2400,
}
BASE_COORDS = (50.9849, 23.1721)
MAX_DISTANCE_KM = 30
PRICE_THRESHOLD = 100

# Tworzymy instancję bota za pomocą tokena
bot = Bot(TOKEN)
app_flask = Flask(__name__)

bot_start_time = time.time()
sent_ads = set()
jobs_started = set()

def extract_price(text: str):
    nums = ''.join(c for c in text if c.isdigit())
    return int(nums) if nums else None

def get_olx_ads():
    URL = "https://www.olx.pl/d/telefony/apple-iphone/"
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(URL, headers=headers)
    soup = BeautifulSoup(resp.text, "html.parser")
    offers = []
    for card in soup.select("div[data-cy='l-card']"):
        # ... (jak wcześniej) ...
        pass
    return offers

def filter_offers_and_notify(chat_id):
    offers = get_olx_ads()
    for o in offers:
        if o["id"] in sent_ads or o["created"] <= bot_start_time or o["price"] is None:
            continue
        dist = geodesic(BASE_COORDS, o["coords"]).km
        if dist > MAX_DISTANCE_KM:
            continue
        for model, avg in AVERAGE_PRICE.items():
            if model in o["title"] and o["price"] < avg - PRICE_THRESHOLD:
                text = (
                    f"📱 *{o['title']}*\n"
                    f"💰 {o['price']} zł (avg {avg} zł)\n"
                    f"🌍 {dist:.1f} km od Krasnegostawu\n"
                    f"🔗 [Link]({o['link']})"
                )
                bot.send_message(chat_id, text, parse_mode="Markdown")
                sent_ads.add(o["id"])
                break

# ——— Handlery Telegrama ———
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in jobs_started:
        await context.bot.send_message(chat_id, "Monitor już działa 😉")
        return
    await context.bot.send_message(chat_id, "Uruchamiam monitoring OLX iPhone’ów…")
    jobs_started.add(chat_id)
    # Pierwsze sprawdzenie za 1 sekundę
    context.job_queue.run_repeating(
        lambda ctx: filter_offers_and_notify(chat_id),
        interval=600,
        first=1
    )

# ——— Użycie ApplicationBuilder w nowej wersji python-telegram-bot ———
async def main():
    application = ApplicationBuilder().token(TOKEN).build()

    # Rejestracja handlerów
    application.add_handler(CommandHandler("start", start))

    # Uruchomienie bota
    await application.run_polling()

# ——— Webhook endpoint Flask ———
@app_flask.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "OK"

# ——— Keep‑alive endpoint ———
@app_flask.route("/", methods=["GET"])
def health():
    return "Bot działa!"

def set_webhook():
    # Ustawiamy webhook w Telegramie
    if bot.set_webhook(WEBHOOK_URL):
        logger.info(f"Webhook ustawiony na {WEBHOOK_URL}")
    else:
        logger.error("Nie udało się ustawić webhooka")

def run():
    # 1) Ustaw webhook
    set_webhook()

    # 2) Start Flask
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()