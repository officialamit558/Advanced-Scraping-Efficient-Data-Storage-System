# dashboard/app.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from src.scraper.scraper import run_scraper
from src.scraper.crawling_map import CrawlingMap
from config.config import Config
import threading

app = Flask(__name__)
socketio = SocketIO(app)
crawler = CrawlingMap(socketio)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            # Run scraper in a separate thread to avoid blocking Flask
            threading.Thread(target=run_scraper, args=(url, socketio)).start()
    logs = crawler.get_logs(limit=50)
    return render_template('index.html', logs=logs)

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('update_logs', {'logs': crawler.get_logs(limit=50)})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=Config.PORT, debug=True)