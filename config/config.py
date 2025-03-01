# Configuration settings (e.g., database credentials, API keys)
# config/config.py
import os

class Config:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/scraped_data")
    MYSQL_URI = os.getenv("MYSQL_URI", "mysql+mysqlconnector://user:password@localhost:3306/contacts")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
    ES_HOST = os.getenv("ES_HOST", "localhost:9200")
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost:6379")
    TWO_CAPTCHA_API_KEY = os.getenv("TWO_CAPTCHA_API_KEY", "your_2captcha_key")