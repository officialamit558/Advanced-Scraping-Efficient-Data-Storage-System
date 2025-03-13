# config/config.py
import os
from dotenv import load_dotenv
load_dotenv()

class Config:  
    """Central configuration class for the Advanced Scraping System."""

    # MongoDB URI (for documents and crawling map)
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/scraped_data")

    # MySQL URI (for structured contact data)
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "@#$Amit1736")
    MYSQL_DB = os.getenv("MYSQL_DB", "contacts")
    # Neo4j URI (for knowledge graph)
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

    # ElasticSearch URI (for indexing and fast retrieval)
    ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")

    # Redis URI (for caching and Celery broker)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost:6379")
    REDIS_DB = os.getenv("REDIS_DB", "0")
    REDIS_URL = f"redis://{REDIS_HOST}/{REDIS_DB}"

    # 2Captcha API Key (for CAPTCHA solving)
    TWO_CAPTCHA_API_KEY = os.getenv("TWO_CAPTCHA_API_KEY", "b43f82c2757657cba4176b62b6d32a37")

    # Proxy Service Settings (e.g., BrightData)
    PROXY_HOST = os.getenv("PROXY_HOST", "proxy.example.com")
    PROXY_PORT = os.getenv("PROXY_PORT", "8080")
    PROXY_USER = os.getenv("PROXY_USER", "username")
    PROXY_PASSWORD = os.getenv("PROXY_PASSWORD", "password")
    PROXY_URL = f"http://{PROXY_USER}:{PROXY_PASSWORD}@{PROXY_HOST}:{PROXY_PORT}"

    # Scraping Delays (to mimic human behavior)
    DOWNLOAD_DELAY = float(os.getenv("DOWNLOAD_DELAY", "2.0"))

    # Celery Configuration
    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

    # NLP Settings (optional)
    # config/config.py (append to existing)
    NLP_MODEL = os.getenv("NLP_MODEL", "distilbert-base-uncased-finetuned-sst-2-english")
    NLP_THRESHOLD = float(os.getenv("NLP_THRESHOLD", "0.7"))  # Confidence threshold for sentiment
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "scraping_system.log")

    # This for the run the schokitio in the local environment.
    HOST = os.getenv("HOST", "0.0.0.0")  # Default to all interfaces
    PORT = int(os.getenv("PORT", 5000))  # Default port 5000
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"