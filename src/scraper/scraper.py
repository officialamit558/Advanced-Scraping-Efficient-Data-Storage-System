# src/scraper/scraper.py (update parse method)
import scrapy
from scrapy.crawler import CrawlerProcess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from twocaptcha import TwoCaptcha
from config.config import Config
from src.scraper.crawling_map import CrawlingMap
from src.orchestrator.orchestrator import Orchestrator

class RobustSpider(scrapy.Spider):
    name = "robust_spider"
    orchestrator = Orchestrator()

    def __init__(self, start_url, socketio=None):
        self.start_urls = [start_url]
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.driver = webdriver.Chrome(executable_path="C:\Users\amit7\advanced_scraping_system\advanced_scraping_system\src\scraper\chromedriver.exe")
        self.crawler = CrawlingMap(socketio)
        self.solver = TwoCaptcha(Config.TWO_CAPTCHA_API_KEY)

    def parse(self, response):
        path = response.meta.get("path", [response.url])
        challenge = None
        if "captcha" in response.text.lower():
            challenge = "CAPTCHA"
            captcha_url = response.xpath("//img[@id='captcha']/@src").get()
            result = self.solver.normal(captcha_url)
            self.driver.get(response.url)
            self.driver.find_element_by_id("captcha_input").send_keys(result["code"])
            self.driver.find_element_by_id("submit").click()

        self.crawler.log(response.url, "success" if not challenge else "blocked", challenge, path)

        data = {
            "url": response.url,
            "structured": response.xpath("//table//tr").extract(),
            "unstructured": response.xpath("//p/text()").getall(),
            "type": "mixed"
        }
        self.orchestrator.process(data)  # Process data via orchestrator

        yield data

    def closed(self, reason):
        self.driver.quit()

def run_scraper(url, socketio=None):
    process = CrawlerProcess(settings={
        "FEEDS": {"output.json": {"format": "json"}},
        "USER_AGENT": "Mozilla/5.0",
        "DOWNLOAD_DELAY": Config.DOWNLOAD_DELAY,
    })
    process.crawl(RobustSpider, start_url=url, socketio=socketio)
    process.start()

if __name__ == "__main__":
    run_scraper("https://example.com")