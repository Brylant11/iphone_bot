from flask import Flask
import threading
import time
from bot import start_bot  # lub inna funkcja bota, która uruchamia Twojego bota

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot jest aktywny!'

def run_bot():
    while True:
        start_bot()  # Upewnij się, że ta funkcja uruchamia Twój bot
        time.sleep(3600)  # Co godzinę uruchamiaj bota

if __name__ == '__main__':
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=5000)