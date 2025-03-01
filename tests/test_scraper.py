# Unit tests for scraper
# tests/test_scraper.py
import pytest
from src.scraper.scraper import RobustSpider
from src.scraper.crawling_map import CrawlingMap
from scrapy.http import Request, Response
from unittest.mock import Mock, patch
import time

# Fixture for CrawlingMap
@pytest.fixture
def crawling_map():
    return CrawlingMap()

# Unit Test: Test spider parsing static content
def test_parse_static_content():
    # Mock a simple HTML response
    html = """
    <html>
        <table><tr><td>Data</td></tr></table>
        <p>Unstructured text</p>
    </html>
    """
    request = Request(url="https://example.com")
    response = Response(url="https://example.com", body=html.encode(), request=request)
    
    spider = RobustSpider()
    result = next(spider.parse(response))  # Parse returns a generator
    
    assert result["url"] == "https://example.com"
    assert len(result["structured"]) > 0  # Table data
    assert "Unstructured text" in result["unstructured"]

# Unit Test: Test CAPTCHA handling (mocked)
@patch("twocaptcha.TwoCaptcha.normal")
def test_parse_with_captcha(mock_captcha, monkeypatch):
    # Mock CAPTCHA response
    mock_captcha.return_value = {"code": "12345"}
    
    html = "<html><p>CAPTCHA detected</p><img id='captcha' src='captcha.jpg'></html>"
    request = Request(url="https://example.com")
    response = Response(url="https://example.com", body=html.encode(), request=request)
    
    # Mock Selenium driver
    mock_driver = Mock()
    monkeypatch.setattr("selenium.webdriver.Chrome", lambda *args, **kwargs: mock_driver)
    
    spider = RobustSpider()
    result = next(spider.parse(response))
    
    assert mock_driver.get.called
    assert mock_driver.find_element_by_id.called_with("captcha_input")
    assert "12345" in mock_driver.find_element_by_id().send_keys.call_args[0]

# Unit Test: Test crawling map logging
def test_crawling_map_logging(crawling_map):
    crawling_map.log("https://example.com", "success")
    result = crawling_map.collection.find_one({"url": "https://example.com"})
    
    assert result["status"] == "success"
    assert "timestamp" in result

# Stress Test: Simulate scraping multiple URLs
def test_stress_scraper():
    urls = [f"https://example.com/page{i}" for i in range(100)]
    spider = RobustSpider()
    spider.start_urls = urls
    
    start_time = time.time()
    process = scrapy.crawler.CrawlerProcess(settings={
        "FEEDS": {"output.json": {"format": "json"}},
        "DOWNLOAD_DELAY": 0.1,  # Minimal delay for testing
    })
    process.crawl(RobustSpider)
    process.start()
    duration = time.time() - start_time
    
    # Verify output file exists and has data
    with open("output.json", "r") as f:
        data = f.read()
        assert len(data) > 0
    
    # Check performance (e.g., under 60 seconds for 100 pages)
    assert duration < 60, f"Stress test took too long: {duration} seconds"

if __name__ == "__main__":
    pytest.main(["-v"])