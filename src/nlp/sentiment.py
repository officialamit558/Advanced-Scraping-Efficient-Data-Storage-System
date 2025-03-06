# src/nlp/sentiment.py
from transformers import pipeline
from src.storage.document_store import DocumentStore
from config.config import Config  # Corrected import from earlier fix

class SentimentAnalyzer:
    def __init__(self):
        try:
            # Use Config.NLP_MODEL if defined, else default to a standard model
            model = getattr(Config, "NLP_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
            self.analyzer = pipeline("sentiment-analysis", model=model)
            self.store = DocumentStore()
        except Exception as e:
            print(f"Failed to initialize SentimentAnalyzer: {e}")
            raise

    def analyze(self, data):
        """Perform sentiment analysis on unstructured data."""
        try:
            # Extract text from nested unstructured fields (paragraphs, headings)
            unstructured = data.get("unstructured", {})
            text_content = " ".join(
                unstructured.get("paragraphs", []) + unstructured.get("headings", [])
            ).strip()

            if not text_content:
                print(f"No text content to analyze for URL: {data.get('url', 'unknown')}")
                return data

            # Perform sentiment analysis
            result = self.analyzer(text_content)[0]
            data["sentiment"] = result["label"].lower()  # e.g., "positive", "negative"
            data["sentiment_score"] = result["score"]

            # Update the document in MongoDB with sentiment
            self.store.collection.update_one(
                {"url": data["url"]},  # Match by URL (consistent with DocumentStore)
                {"$set": {
                    "sentiment": data["sentiment"],
                    "sentiment_score": data["sentiment_score"],
                    "analyzed_at": datetime.datetime.utcnow().isoformat()
                }},
                upsert=False  # Only update existing documents
            )
            print(f"Sentiment updated for {data['url']}: {data['sentiment']} ({data['sentiment_score']})")

        except Exception as e:
            print(f"Error analyzing sentiment for {data.get('url', 'unknown')}: {e}")
            data["sentiment_error"] = str(e)

        return data

# Example usage
if __name__ == "__main__":
    import datetime
    analyzer = SentimentAnalyzer()
    sample_data = {
        "url": "https://example.com",
        "unstructured": {
            "paragraphs": ["I love this product! It’s amazing."],
            "headings": ["Product Review"]
        }
    }
    result = analyzer.analyze(sample_data)
    print(result)