# src/scraper/crawling_map.py
from pymongo import MongoClient
from config.config import Config
import datetime

class CrawlingMap:
    def __init__(self, socketio=None):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["scraped_data"]
        self.collection = self.db["crawling_map"]
        self.socketio = socketio  # For real-time updates

    def log(self, url, status, challenge=None, path=None):
        entry = {
            "url": url,
            "status": status,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "challenge": challenge or "none",
            "path": path or [url]
        }
        self.collection.insert_one(entry)
        print(f"Logged: {entry}")
        if self.socketio:
            self.socketio.emit('update_logs', {'logs': self.get_logs(limit=50)})
        return entry

    def get_logs(self, limit=100):
        return list(self.collection.find().sort("timestamp", -1).limit(limit))

# Example usage
if __name__ == "__main__":
    crawler = CrawlingMap()
    crawler.log("https://example.com", "success", path=["https://example.com"])