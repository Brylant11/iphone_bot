import os
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return 'Bot działa!'

def keep_alive():
    port = int(os.environ.get('PORT', 8080))  # Jeśli nie ma ustawionego portu, użyj 8080
    app.run(host='0.0.0.0', port=port)