# MongoDB for documents
# src/storage/document_store.py
from pymongo import MongoClient
from config.config import Config
import datetime

class DocumentStore:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["scraped_data"]
        self.collection = self.db["documents"]

    # src/storage/document_store.py (reference)
    def save(self, data):
        doc = {
            "url": data.get("url"),
            "content": data.get("unstructured", ""),
            "title": data.get("title", "No title"),
            "depth": data.get("depth", 0),
            "timestamp": datetime.datetime.utcnow()
        }
        self.collection.insert_one(doc)
        return doc["_id"]

# Example usage
if __name__ == "__main__":
    store = DocumentStore()
    store.save({"unstructured": "Sample text", "url": "https://example.com"})