# Sentiment analysis
# src/nlp/sentiment.py
from transformers import pipeline
from src.storage.document_store import DocumentStore

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
        self.store = DocumentStore()

    def analyze(self, data):
        text = data.get("unstructured", "")
        result = self.analyzer(text)[0]
        data["sentiment"] = result["label"]
        data["score"] = result["score"]
        self.store.save(data)  # Update with sentiment
        return data

# Example usage
if __name__ == "__main__":
    analyzer = SentimentAnalyzer()
    result = analyzer.analyze({"unstructured": "I love this product!", "url": "https://example.com"})
    print(result)