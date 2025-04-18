# bot.py

import os
import time
import logging
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask
from geopy.distance import geodesic
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

# ——— Konfiguracja logów ———
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ——— Token i stałe ———
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    logger.error("BRAK TOKENA! Ustaw zmienną środowiskową BOT_TOKEN.")
    exit(1)

AVERAGE_PRICE = {
    'iphone x 64 gb': 650,    'iphone x 256 gb': 800,
    'iphone xr 64 gb': 700,   'iphone xr 128 gb': 800,
    'iphone 11 64 gb': 750,   'iphone 11 128 gb': 800,  'iphone 11 256 gb': 900,
    'iphone 11 pro 64 gb': 1000,  'iphone 11 pro 256 gb': 1200,
    'iphone 11 pro max 64 gb': 1100,'iphone 11 pro max 256 gb': 1300,
    'iphone 12 64 gb': 1100,  'iphone 12 128 gb': 1200, 'iphone 12 256 gb': 1300,
    'iphone 12 pro 128 gb': 1400,'iphone 12 pro 256 gb': 1600,
    'iphone 12 pro max 128 gb':1500,'iphone 12 pro max 256 gb':1700,
    'iphone 13 128 gb':1600,  'iphone 13 256 gb':1800, 'iphone 13 512 gb':2000,
    'iphone 13 pro 128 gb':1900,'iphone 13 pro 256 gb':2100,'iphone 13 pro 512 gb':2300,
    'iphone 13 pro max 128 gb':2000,'iphone 13 pro max 256 gb':2200,'iphone 13 pro max 512 gb':2400,
}

BASE_COORDS = (50.9849, 23.1721)
MAX_DISTANCE_KM = 30
PRICE_THRESHOLD = 100

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
        title_el = card.select_one("h6")
        link_el  = card.select_one("a")
        price_el = card.select_one("p[data-testid='ad-price']")
        lat_el   = card.select_one("meta[itemprop='latitude']")
        lon_el   = card.select_one("meta[itemprop='longitude']")
        time_el  = card.select_one("time")
        if not (title_el and link_el and price_el and lat_el and lon_el and time_el):
            continue

        title = title_el.get_text(strip=True).lower()
        price = extract_price(price_el.get_text())
        link  = link_el["href"]
        ad_id = card.get("data-id")
        lat   = float(lat_el["content"])
        lon   = float(lon_el["content"])
        ts    = time_el["datetime"]  # "2025-04-18T12:34:56"
        created = time.mktime(time.strptime(ts, "%Y-%m-%dT%H:%M:%S"))

        offers.append({
            "id": ad_id,
            "title": title,
            "link": link,
            "price": price,
            "coords": (lat, lon),
            "created": created
        })
    return offers

def filter_offers(context):
    chat_id = context.job.context
    offers = get_olx_ads()
    for o in offers:
        if o["id"] in sent_ads: 
            continue
        if o["created"] <= bot_start_time: 
            continue
        if o["price"] is None: 
            continue
        dist = geodesic(BASE_COORDS, o["coords"]).km
        if dist > MAX_DISTANCE_KM: 
            continue

        for model, avg in AVERAGE_PRICE.items():
            if model in o["title"] and o["price"] < avg - PRICE_THRESHOLD:
                text = (
                    f"📱 *{o['title']}*\n"
                    f"💰 {o['price']} zł (avg {avg} zł)\n"
                    f"🌍 {dist:.1f} km od Krasnegostawu\n"
                    f"🔗 [Link]({o['link']})"
                )
                context.bot.send_message(chat_id, text, parse_mode="Markdown")
                sent_ads.add(o["id"])
                break

@app_flask.route("/")
def home():
    return "Bot działa!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if chat_id in jobs_started:
        await update.message.reply_text("Monitor już działa 😉")
        return

    await update.message.reply_text("Uruchamiam monitoring OLX iPhone’ów…")

    # Zaplanuj job co 10 minut
    context.job_queue.run_repeating(
        filter_offers,
        interval=600,  # co 10 minut
        first=1,
        context=chat_id
    )
    jobs_started.add(chat_id)

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

def main():
    # 1) Start Flask
    threading.Thread(target=run_flask, daemon=True).start()
    logger.info("Flask działa w tle")

    # 2) Build and start bot
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))

    # Usuń zaległe update’y przed pollingiem
    app.bot.delete_webhook(drop_pending_updates=True)

    logger.info("Start polling…")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()