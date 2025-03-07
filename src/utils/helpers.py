# src/utils/helpers.py
# Logging, async utilities
from celery import Celery
from config.config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery with Redis broker
app = Celery("tasks", broker=f"redis://{Config.REDIS_HOST}/0", backend=f"redis://{Config.REDIS_HOST}/0")

@app.task(bind=True, max_retries=3)
def process_data(self, data):
    """Process data asynchronously, triggering NLP if needed."""
    try:
        # Import inside task to avoid circular imports
        from src.orchestrator.orchestrator import Orchestrator
        from src.nlp.sentiment import SentimentAnalyzer

        # Process data with orchestrator
        orchestrator = Orchestrator()
        result = orchestrator.process(data)
        
        # Check if NLP is triggered (based on orchestrator's result)
        if result.get("nlp_triggered", False):
            logger.info("NLP triggered for %s", data.get("url", "unknown"))
            analyzer = SentimentAnalyzer()
            analyzed_data = analyzer.analyze(data)
            logger.info("Sentiment analysis completed for %s: %s", 
                        data.get("url", "unknown"), analyzed_data.get("sentiment", "N/A"))
            return analyzed_data
        else:
            logger.info("No NLP needed for %s", data.get("url", "unknown"))
            return result

    except Exception as e:
        logger.error("Error processing data for %s: %s", data.get("url", "unknown"), e)
        # Retry on failure with exponential backoff
        self.retry(exc=e, countdown=5 * (self.request.retries + 1))

# Example usage
if __name__ == "__main__":
    sample_data = {
        "url": "https://example.com",
        "title": "Example Page",
        "unstructured": {
            "paragraphs": ["This is a great review of the product!"],
            "headings": ["Product Overview"]
        },
        "structured": {
            "tables": ["<tr><td>John</td><td>xAI</td></tr>"]
        },
        "metadata": {"links": ["https://example.com/about"]},
        "type": "mixed",
        "depth": 0
    }
    result = process_data.delay(sample_data)
    print(f"Task queued with ID: {result.id}")