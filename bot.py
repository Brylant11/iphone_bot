from telegram import Bot
from telegram.ext import Application, CommandHandler
import logging

# Ustawienie tokena bota
TOKEN = '8078750965:AAHOJreGct5e0mxEva8QIjPbUXMpSQromfs'
'  # <-- Pamiętaj, aby tu wstawić swój token!

# Konfiguracja logów (opcjonalnie)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# Funkcja obsługująca komendę /start
async def start(update, context):
    await update.message.reply_text("Witaj! Twój bot działa!")

def main():
    # Tworzymy aplikację
    application = Application.builder().token(TOKEN).build()

    # Dodajemy handler komendy '/start'
    application.add_handler(CommandHandler('start', start))

    # Uruchamiamy bota
    application.run_polling()

if __name__ == '__main__':
    main()