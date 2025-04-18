import os
import time
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask, request
from geopy.distance import geodesic
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)
import asyncio

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
    'iphone 13 pro max 512 gb': 2400, 'iphone 12 64 gb': 1500,
    'iphone 12 128 gb': 1800, 'iphone 13 64 gb': 2200,
    'iphone 13 256 gb': 2600, 'iphone 14 pro 128 gb': 4500,
    'iphone 14 pro 256 gb': 5000, 'iphone 14 pro max 128 gb': 5300,
    'iphone 14 pro max 256 gb': 5800,
    'iphone 14 pro max 512 gb': 6300,
    'iphone 13 pro 128 gb': 2900, 'iphone 13 pro 256 gb': 3300,
    'iphone 13 128 gb': 2500, 'iphone 14 128 gb': 4200,
    'iphone 14 256 gb': 4600, 'iphone 12 pro 64 gb': 2800,
    'iphone 12 pro 128 gb': 3200, 'iphone 12 pro 256 gb': 3600,
    'iphone 11 64 gb': 1300, 'iphone 11 128 gb': 1700,
    'iphone 11 pro 64 gb': 2400, 'iphone 11 pro 256 gb': 2800,
    'iphone 11 pro max 64 gb': 3000, 'iphone 11 pro max 256 gb': 3400,
    'iphone se 64 gb': 800, 'iphone se 128 gb': 1000,
    'iphone se 256 gb': 1200,
    'iphone 7 32 gb': 500, 'iphone 7 128 gb': 600,
    'iphone 8 64 gb': 800, 'iphone 8 128 gb': 1000,
    'iphone 8 256 gb': 1200,
}

BASE_COORDS = (50.9849, 23.1721)  # Przykładowa lokalizacja (np. Krasnystaw)
MAX_DISTANCE_KM = 30
PRICE_THRESHOLD = 100

app_flask = Flask(__name__)

# ——— Funkcje pomocnicze ———
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
        title = card.select_one(".css-1g20a2m").text.strip()
        price = extract_price(card.select_one(".css-1hbw00a").text.strip())
        link = card.select_one("a")["href"]
        coords = (float(card.select_one(".css-vpzd7v").text.split(",")[0]),
                  float(card.select_one(".css-vpzd7v").text.split(",")[1]))
        offers.append({
            "title": title,
            "price": price,
            "link": link,
            "coords": coords,
            "id": hash(link),  # unique id
            "created": int(time.time())
        })
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
            if model in o["title"].lower() and o["price"] < avg - PRICE_THRESHOLD:
                text = (
                    f"📱 *{o['title']}*\n"
                    f"💰 {o['price']} zł (średnia {avg} zł)\n"
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

# Tworzenie aplikacji
application = Application.builder().token(TOKEN).build()

# Dodaj handler
application.add_handler(CommandHandler("start", start))

# ——— Webhook endpoint Flask ———
@app_flask.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "OK"

# ——— Keep‑alive endpoint ———
@app_flask.route("/", methods=["GET"])
def health():
    return "Bot działa!"

async def set_webhook():
    if await application.bot.set_webhook(WEBHOOK_URL):
        logger.info(f"Webhook ustawiony na {WEBHOOK_URL}")
    else:
        logger.error("Nie udało się ustawić webhooka")

async def run():
    # 1) Ustaw webhook
    await set_webhook()

    # 2) Start Flask
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# Uruchamianie aplikacji
if __name__ == "__main__":
    asyncio.run(run())