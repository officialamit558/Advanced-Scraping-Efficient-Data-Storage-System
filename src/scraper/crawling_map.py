# Crawling map logger
# src/scraper/crawling_map.py
from pymongo import MongoClient
from config.config import Config
import datetime

class CrawlingMap:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["scraped_data"]
        self.collection = self.db["crawling_map"]

    def log(self, url, status, challenge=None):
        entry = {
            "url": url,
            "status": status,
            "timestamp": datetime.datetime.utcnow(),
            "challenge": challenge or "none"
        }
        self.collection.insert_one(entry)
        print(f"Logged: {entry}")

# Example usage
if __name__ == "__main__":
    crawler = CrawlingMap()
    crawler.log("https://example.com", "success")
    crawler.log("https://example.com/captcha", "blocked", "CAPTCHA")