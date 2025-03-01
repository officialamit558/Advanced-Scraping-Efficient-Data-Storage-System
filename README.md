# Project documentation
# Advanced Scraping System

## Setup
1. Install Docker and Docker Compose.
2. Run `docker-compose up -d` to start services (MongoDB, MySQL, Neo4j, ElasticSearch, Redis).
3. Install dependencies: `pip install -r requirements.txt`.
4. Set environment variables in `.env` (e.g., TWO_CAPTCHA_API_KEY, MYSQL_URI).

## Usage
- Run scraper: `python src/scraper/scraper.py`.
- Monitor crawling: Check MongoDB `crawling_map` collection.
- Query MySQL: `SELECT * FROM contacts;` (use any MySQL client).
- Query ElasticSearch: `curl -X GET "localhost:9200/scraped_data/_search"`.

## Architecture
- Scraper → Crawling Map → Storage (MongoDB/MySQL) → Neo4j → ElasticSearch → Orchestrator → NLP (optional).