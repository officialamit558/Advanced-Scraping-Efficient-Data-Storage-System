# src/scraper/scraper.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from twocaptcha import TwoCaptcha
import time
from config.config import Config
from src.scraper.crawling_map import CrawlingMap
from src.orchestrator.orchestrator import Orchestrator

class RobustSpider(scrapy.Spider):
    name = "robust_spider"
    orchestrator = Orchestrator()  # Class-level orchestrator instance

    def __init__(self, start_url, socketio=None, max_depth=2, *args, **kwargs):
        super(RobustSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.max_depth = max_depth  # Limit recursion depth
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_driver_path = r"C:\Users\amit7\advanced_scraping_system\advanced_scraping_system\src\scraper\chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            self.log(f"Failed to initialize WebDriver: {e}")
            raise
        
        self.crawler = CrawlingMap(socketio)
        self.solver = TwoCaptcha(Config.TWO_CAPTCHA_API_KEY)
        self.allowed_domains = [start_url.split("://")[1].split("/")[0]]  # Restrict to domain

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, callback=self.parse, meta={"depth": 0, "path": [url]})

    def parse(self, response):
        path = response.meta.get("path", [response.url])
        depth = response.meta.get("depth", 0)
        challenge = None

        # Handle dynamic content with Selenium if needed
        try:
            self.driver.get(response.url)
            time.sleep(2)  # Wait for dynamic content to load
            page_source = self.driver.page_source
        except Exception as e:
            self.log(f"Failed to load page with Selenium: {e}")
            page_source = response.text  # Fall back to Scrapy response

        # Check for CAPTCHA
        captcha_detected = "captcha" in page_source.lower()
        if captcha_detected:
            challenge = "CAPTCHA"
            try:
                captcha_url = response.xpath("//img[@id='captcha']/@src").get()
                if captcha_url:
                    result = self.solver.normal(captcha_url)
                    captcha_input = self.driver.find_element(By.ID, "captcha_input")
                    captcha_input.send_keys(result["code"])
                    self.driver.find_element(By.ID, "submit").click()
                    time.sleep(2)  # Wait for page to refresh
                    page_source = self.driver.page_source  # Update page source after CAPTCHA
                    challenge = "CAPTCHA_SOLVED"
            except Exception as e:
                self.log(f"CAPTCHA solving failed: {e}")
                challenge = "CAPTCHA_FAILED"

        # Log the crawl action
        status = "success" if not challenge or challenge == "CAPTCHA_SOLVED" else "blocked"
        self.crawler.log(response.url, status, challenge, path)

        # Extract data comprehensively
        data = {
            "url": response.url,
            "title": response.xpath("//title/text()").get(default="No title"),
            "structured": {
                "tables": response.xpath("//table//tr").extract(),
                "lists": response.xpath("//ul//li | //ol//li").extract(),
            },
            "unstructured": {
                "paragraphs": response.xpath("//p/text()").getall(),
                "headings": response.xpath("//h1/text() | //h2/text() | //h3/text()").getall(),
            },
            "metadata": {
                "links": response.xpath("//a/@href").getall(),
                "meta_tags": response.xpath("//meta/@content").getall(),
            },
            "type": "mixed",
            "depth": depth
        }

        # Process data through orchestrator
        try:
            self.orchestrator.process(data)
        except Exception as e:
            self.log(f"Orchestrator processing failed: {e}")

        yield data

        # Follow links recursively if within depth limit
        if depth < self.max_depth:
            for link in response.xpath("//a/@href").getall():
                if link.startswith("http") and any(domain in link for domain in self.allowed_domains):
                    new_path = path + [link]
                    yield Request(
                        link,
                        callback=self.parse,
                        meta={"depth": depth + 1, "path": new_path},
                        errback=self.handle_error
                    )

    def handle_error(self, failure):
        self.log(f"Request failed: {failure.request.url}, Error: {failure.value}")
        self.crawler.log(failure.request.url, "failed", str(failure.value), failure.request.meta.get("path", [failure.request.url]))

    def closed(self, reason):
        try:
            self.driver.quit()
            self.log(f"Spider closed: {reason}")
        except Exception as e:
            self.log(f"Error closing WebDriver: {e}")

def run_scraper(url, socketio=None, max_depth=2):
    process = CrawlerProcess(settings={
        "FEEDS": {"output.json": {"format": "json"}},
        "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "DOWNLOAD_DELAY": Config.DOWNLOAD_DELAY,
        "ROBOTSTXT_OBEY": False,  # Ignore robots.txt for testing (adjust as needed)
        "DOWNLOAD_TIMEOUT": 30,   # Handle slow responses
        "RETRY_TIMES": 3,         # Retry failed requests
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 400, 403, 404],
    })
    process.crawl(RobustSpider, start_url=url, socketio=socketio, max_depth=max_depth)
    process.start()

if __name__ == "__main__":
    run_scraper("https://example.com")