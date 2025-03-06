# dashboard/app.py
import sys
import os

# Ensure the project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
from flask import Flask, render_template, request
from flask_socketio import SocketIO
from src.scraper.scraper import *  # Explicit import
from src.scraper.crawling_map import CrawlingMap
from config.config import Config

# Ensure the project root is in sys.path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

app = Flask(__name__)
socketio = SocketIO(app)
crawler = CrawlingMap(socketio)  # Initialize with SocketIO for real-time updates

@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        if request.method == 'POST':
            url = request.form.get('url')
            if url:
                # Validate URL minimally
                if not url.startswith("http"):
                    url = "https://" + url
                # Run scraper in a separate thread to avoid blocking Flask
                thread = threading.Thread(
                    target=run_scraper,
                    args=(url, socketio, 2),  # Pass max_depth=2 as per scraper
                    daemon=True
                )
                thread.start()
                return render_template('index.html', logs=crawler.get_logs(limit=50), message=f"Scraping started for {url}")
        
        logs = crawler.get_logs(limit=50) or []
        return render_template('index.html', logs=logs)
    except Exception as e:
        return render_template('index.html', logs=crawler.get_logs(limit=50), error=f"Error: {str(e)}")

@socketio.on('connect')
def handle_connect():
    print("Client connected")
    try:
        socketio.emit('update_logs', {'logs': crawler.get_logs(limit=50)})
    except Exception as e:
        print(f"Error emitting logs on connect: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")

if __name__ == "__main__":
    # Use Config.PORT if defined, else default to 5000
    port = getattr(Config, "PORT", 5000)
    socketio.run(app, host="0.0.0.0", port=port, debug=True)