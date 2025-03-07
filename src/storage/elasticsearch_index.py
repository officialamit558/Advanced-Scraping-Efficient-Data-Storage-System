# src/storage/elasticsearch_index.py
from elasticsearch import Elasticsearch
from config.config import Config
import datetime
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ESIndex:
    def __init__(self):
        """Initialize the Elasticsearch client."""
        try:
            self.es = Elasticsearch([Config.ES_HOST], timeout=30, max_retries=3, retry_on_timeout=True)
            if not self.es.ping():
                raise ValueError("Elasticsearch connection failed")
            logger.info("Connected to Elasticsearch at %s", Config.ES_HOST)
            
            # Create index if it doesn’t exist
            if not self.es.indices.exists(index="scraped_data"):
                self.es.indices.create(index="scraped_data", body={
                    "mappings": {
                        "properties": {
                            "url": {"type": "keyword"},
                            "title": {"type": "text"},
                            "content": {"type": "text"},
                            "structured": {"type": "object"},
                            "metadata": {"type": "object"},
                            "sentiment": {"type": "keyword"},
                            "sentiment_score": {"type": "float"},
                            "timestamp": {"type": "date"},
                            "depth": {"type": "integer"}
                        }
                    }
                })
                logger.info("Created Elasticsearch index 'scraped_data'")
        except Exception as e:
            logger.error("Failed to initialize Elasticsearch: %s", e)
            raise

    def index(self, data):
        """Index the provided data in Elasticsearch."""
        try:
            # Prepare document for indexing
            unstructured = data.get("unstructured", {})
            content = " ".join(
                unstructured.get("paragraphs", []) + unstructured.get("headings", [])
            ).strip()

            doc = {
                "url": data.get("url", "unknown"),
                "title": data.get("title", "No title"),
                "content": content,
                "structured": data.get("structured", {}),
                "metadata": data.get("metadata", {}),
                "sentiment": data.get("sentiment"),  # From sentiment.py if present
                "sentiment_score": data.get("sentiment_score"),  # From sentiment.py if present
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "depth": data.get("depth", 0)
            }

            # Index the document
            response = self.es.index(index="scraped_data", body=doc)
            logger.info("Indexed document for %s with ID %s", doc["url"], response["_id"])
            return response["_id"]

        except Exception as e:
            logger.error("Failed to index data for %s: %s", data.get("url", "unknown"), e)
            raise

    def close(self):
        """Close the Elasticsearch client (optional cleanup)."""
        try:
            if self.es:
                self.es.close()
                logger.info("Elasticsearch client closed")
        except Exception as e:
            logger.error("Error closing Elasticsearch client: %s", e)

# Example usage
if __name__ == "__main__":
    indexer = ESIndex()
    sample_data = {
        "url": "https://example.com",
        "title": "Example Page",
        "unstructured": {
            "paragraphs": ["This is a great product!"],
            "headings": ["Product Review"]
        },
        "structured": {
            "tables": ["<tr><td>John</td><td>xAI</td></tr>"],
            "lists": ["<li>Jane at xAI</li>"]
        },
        "metadata": {
            "links": ["https://example.com/about"],
            "meta_tags": ["description"]
        },
        "depth": 0
    }
    doc_id = indexer.index(sample_data)
    print(f"Indexed document with ID: {doc_id}")
    indexer.close()