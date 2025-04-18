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

BASE_URL = os.getenv("RENDER_EXTERNAL_URL")
if not BASE_URL:
    logger.error("BRAK EXTERNAL URL! Ustaw RENDER_EXTERNAL_URL.")
    exit(1)
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = BASE_URL + WEBHOOK_PATH

# ——— Stałe i ceny ———
AVERAGE_PRICE = {
    'iphone x 64 gb': 650, 'iphone x 256 gb': 800,
    'iphone xs 64 gb': 700, 'iphone xs 256 gb': 850, 'iphone xs 512 gb': 1000,
    'iphone xs max 64 gb': 750, 'iphone xs max 256 gb': 900, 'iphone xs max 512 gb': 1050,
    'iphone xr 64 gb': 600, 'iphone xr 128 gb': 750, 'iphone xr 256 gb': 900,
    'iphone 11 pro max 64 gb': 900, 'iphone 11 pro max 256 gb': 1100, 'iphone 11 pro max 512 gb': 1300,
    'iphone 11 64 gb': 700, 'iphone 11 128 gb': 900, 'iphone 11 256 gb': 1100,
    'iphone 12 mini 64 gb': 1100, 'iphone 12 mini 128 gb': 1300, 'iphone 12 mini 256 gb': 1500,
    'iphone 12 64 gb': 1200, 'iphone 12 128 gb': 1400, 'iphone 12 256 gb': 1600,
    'iphone 12 pro 128 gb': 1500, 'iphone 12 pro 256 gb': 1700, 'iphone 12 pro 512 gb': 1900,
    'iphone 12 pro max 128 gb': 1700, 'iphone 12 pro max 256 gb': 1900, 'iphone 12 pro max 512 gb': 2100,
}

BASE_COORDS = (50.9849, 23.1721)
MAX_DISTANCE_KM = 30
PRICE_THRESHOLD = 100

bot = Bot(TOKEN)
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
        title = card.select_one("h6").text.strip()
        link = card.select_one("a")["href"]
        price_text = card.select_one("p[data-cy='ad-price']").text.strip()
        price = extract_price(price_text)
        created = float(card.select_one("time")["data-time"])
        coords = (50.9849, 23.1721)  # Wstaw tutaj odpowiednie współrzędne z ogłoszenia (np. z atrybutów w HTML)
        
        offers.append({
            "id": link,
            "title": title,
            "link": link,
            "price": price,
            "created": created,
            "coords": coords
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

# ——— Ustawienie webhooka w Telegramie ———
async def set_webhook():
    if await bot.set_webhook(WEBHOOK_URL):
        logger.info(f"Webhook ustawiony na {WEBHOOK_URL}")
    else:
        logger.error("Nie udało się ustawić webhooka")

# ——— Webhook endpoint Flask ———
@app_flask.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    await application.process_update(update)
    return "OK"

# ——— Keep‑alive endpoint ———
@app_flask.route("/", methods=["GET"])
def health():
    return "Bot działa!"

def run():
    # 1) Ustaw webhook
    asyncio.run(set_webhook())

    # 2) Start Flask
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    run()