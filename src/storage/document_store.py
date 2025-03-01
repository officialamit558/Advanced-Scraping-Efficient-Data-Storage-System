# MongoDB for documents
# src/storage/document_store.py
from pymongo import MongoClient
from config.config import Config

class DocumentStore:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client["scraped_data"]
        self.collection = self.db["documents"]

    def save(self, data):
        doc = {
            "content": data.get("unstructured", ""),
            "source": data["url"],
            "timestamp": datetime.datetime.utcnow()
        }
        self.collection.insert_one(doc)
        return doc["_id"]

# Example usage
if __name__ == "__main__":
    store = DocumentStore()
    store.save({"unstructured": "Sample text", "url": "https://example.com"})