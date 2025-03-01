# ElasticSearch integration
# src/storage/elasticsearch_index.py
from elasticsearch import Elasticsearch
from config.config import Config

class ESIndex:
    def __init__(self):
        self.es = Elasticsearch([Config.ES_HOST])

    def index(self, data):
        doc = {
            "url": data["url"],
            "content": data.get("unstructured", ""),
            "timestamp": datetime.datetime.utcnow()
        }
        self.es.index(index="scraped_data", body=doc)

# Example usage
if __name__ == "__main__":
    indexer = ESIndex()
    indexer.index({"url": "https://example.com", "unstructured": "Sample text"})