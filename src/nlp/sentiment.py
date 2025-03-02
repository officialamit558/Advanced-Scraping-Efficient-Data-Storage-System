# src/nlp/sentiment.py
from transformers import pipeline
from src.storage.document_store import DocumentStore
from config.config import Config

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline("sentiment-analysis", model=Config.NLP_MODEL)
        self.store = DocumentStore()

    def analyze(self, data):
        """Perform sentiment analysis on unstructured data."""
        text = data.get("unstructured", "")
        if not text:
            return data
        
        result = self.analyzer(text)[0]
        data["sentiment"] = result["label"].lower()  # e.g., "positive", "negative"
        data["sentiment_score"] = result["score"]
        
        # Update the document in MongoDB with sentiment
        self.store.collection.update_one(
            {"source": data["url"]},
            {"$set": {"sentiment": data["sentiment"], "sentiment_score": data["sentiment_score"]}}
        )
        return data

# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    sample_data = {"unstructured": "I love this product!", "url": "https://example.com"}
    result = analyzer.analyze(sample_data)
    print(result)