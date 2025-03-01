# Logging, async utilities
# src/utils/helpers.py
from celery import Celery
from config.config import Config

app = Celery("tasks", broker=f"redis://{Config.REDIS_HOST}/0")

@app.task
def process_data(data):
    from src.orchestrator.orchestrator import Orchestrator
    orchestrator = Orchestrator()
    needs_nlp = orchestrator.process(data)
    if needs_nlp:
        from src.nlp.sentiment import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        analyzer.analyze(data)

# Example usage
if __name__ == "__main__":
    process_data.delay({"url": "https://example.com", "unstructured": "Great review!"})