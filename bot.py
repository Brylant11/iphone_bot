import requests
from bs4 import BeautifulSoup
from geopy.distance import geodesic
from telegram import Bot
from telegram.ext import Application, CommandHandler
import asyncio
from datetime import datetime, timedelta
from flask import Flask
import threading
import time

# ======= KONFIGURACJA =======
TOKEN = '8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs'
CHAT_ID = '192506976'  # lub użyj update.effective_chat.id w handlerze
CITY_COORDS = (50.9844, 23.1735)  # Krasnystaw
RADIUS_KM = 30
KEYWORD = 'iphone'
START_TIME = datetime.now()
# ============================

# Godziny działania bota
START_HOUR = 8
END_HOUR = 20

# ============================

app = Flask(__name__)

# Funkcja do pobierania ofert z OLX
def get_olx_offers():
    url = f'https://www.olx.pl/oferty/q-{KEYWORD}/'
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(response.text, 'html.parser')

    offers = []
    for offer in soup.select('div[data-cy="l-card"]'):
        try:
            title = offer.select_one('h6').text.strip()
            price_text = offer.select_one('p[data-testid="ad-price"]').text.strip().replace('zł', '').replace(' ', '').replace(',', '.')
            price = float(price_text)

            location_raw = offer.select_one('p[data-testid="location-date"]').text.strip()
            location = location_raw.split('-')[0].strip()
            link = offer.select_one('a')['href']

            # Sprawdzamy czy oferta jest nowa, tzn. po czasie uruchomienia bota
            offer_time = offer.select_one('p[data-testid="location-date"]').text.strip()
            if 'min' in offer_time or 'godz' in offer_time:
                timestamp = datetime.now()
            else:
                timestamp = datetime(2025, 1, 1)  # Służy do oddzielenia ofert starszych

            offers.append({'title': title, 'price': price, 'location': location, 'link': link, 'timestamp': timestamp})
        except Exception as e:
            continue

    return offers

# Funkcja do obliczania średniej ceny
def calculate_average_price(offers):
    prices = [offer['price'] for offer in offers if offer['price'] > 100]  # ignorujemy fejkowe
    if not prices:
        return 0
    return sum(prices) / len(prices)

# Funkcja do pobierania współrzędnych miasta
def get_coordinates(city_name):
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={city_name}"
        response = requests.get(url)
        data = response.json()
        if data:
            lat = float(data[0]["lat"])
            lon = float(data[0]["lon"])
            return (lat, lon)
    except:
        return None

# Funkcja do sprawdzania, czy oferta jest w promieniu 30 km
def is_within_radius(city_name):
    coords = get_coordinates(city_name)
    if coords:
        distance = geodesic(CITY_COORDS, coords).km
        return distance <= RADIUS_KM
    return False

# Funkcja do sprawdzania ofert
async def check_offers(bot: Bot):
    print("Sprawdzanie ofert...")
    all_offers = get_olx_offers()
    avg_price = calculate_average_price(all_offers)
    print(f"Średnia cena: {avg_price:.2f} zł")

    new_deals = []
    for offer in all_offers:
        if offer['price'] <= avg_price - 100 and is_within_radius(offer['location']):
            new_deals.append(offer)

    for deal in new_deals:
        message = f"🛒 *{deal['title']}*\n💸 {deal['price']} zł\n📍 {deal['location']}\n🔗 [Zobacz ofertę]({deal['link']})"
        await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

# Funkcja startowa dla komendy /start
async def start(update, context):
    await update.message.reply_text("Bot uruchomiony i szuka iPhone'ów! 🔍")

# Główna funkcja uruchamiająca bota
async def run():
    bot = Bot(token=TOKEN)

    # Zainicjujemy pierwsze wyszukiwanie
    await check_offers(bot)

    # Co 10 minut sprawdzaj oferty, ale tylko w godzinach 8-20
    while True:
        current_time = datetime.now()
        if START_HOUR <= current_time.hour < END_HOUR:
            await check_offers(bot)
        else:
            print(f"Bot jest poza godzinami działania ({START_HOUR}:00 - {END_HOUR}:00), czekam do następnej okazji.")

        # Sprawdzaj co 10 minut
        await asyncio.sleep(600)  # 10 minut

# Funkcja do pingowania serwera co 5 minut
def keep_alive():
    while True:
        # Pingowanie co 5 minut
        print("Pingowanie serwera... Utrzymanie aktywności!")
        try:
            requests.get("http://127.0.0.1:10000")
        except requests.exceptions.RequestException:
            pass
        time.sleep(300)  # co 5 minut

# Funkcja do uruchomienia bota
def start_bot():
    app_flask = Application.builder().token(TOKEN).build()
    app_flask.add_handler(CommandHandler("start", start))

    # Dodanie prostego route dla `/` w Flask
    @app.route('/')
    def home():
        return "Bot działa prawidłowo!"

    # Startuje tylko Flask w osobnym wątku
    threading.Thread(target=lambda: app.run(host="0.0.0.0", port=10000), daemon=True).start()
    threading.Thread(target=keep_alive, daemon=True).start()  # Pingowanie co 5 minut
    print("Flask działa w tle")

    asyncio.run(run())

# ========== MAIN ========== 
if __name__ == '__main__':
    start_bot()