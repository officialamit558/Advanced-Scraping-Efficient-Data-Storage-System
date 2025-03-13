# src/scraper/scraper.py
import sys
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import csv

class RobustScraper:
    def __init__(self, start_url, max_depth=2, two_captcha_api_key=None):
        self.start_url = start_url
        self.max_depth = max_depth
        self.visited_urls = set()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.output_file = f"scraped_data_{timestamp}.txt"
        self.output_csv_file = f"scraped_data_{timestamp}.csv"
        
        # Create CSV file with headers
        with open(self.output_csv_file, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["URL", "Title", "Depth", "Headings", "Paragraphs", "Links", "Tables", "Lists"])
    
        # Initialize Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_driver_path = r"C:\Users\amit7\advanced_scraping_system\advanced_scraping_system\src\scraper\chromedriver.exe"
        service = Service(executable_path=chrome_driver_path)
        try:
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        except Exception as e:
            print(f"Failed to initialize ChromeDriver: {e}")
            print("Ensure ChromeDriver version matches your Chrome browser version.")
            sys.exit(1)
        
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.allowed_domains = [urlparse(start_url).netloc]
        self.two_captcha_api_key = two_captcha_api_key

    def save_to_file(self, data):
        """Save scraped data to both a text file and a CSV file in structured formats"""
        try:
            # Save to .txt file
            with open(self.output_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*50}\n")
                f.write(f"URL: {data['url']}\n")
                f.write(f"Title: {data['title']}\n")
                f.write(f"Depth: {data['depth']}\n")
                f.write("\nHeadings:\n")
                for heading in data['unstructured']['headings']:
                    f.write(f"- {heading}\n")
                f.write("\nParagraphs:\n")
                for para in data['unstructured']['paragraphs']:
                    f.write(f"- {para}\n")
                f.write("\nLinks:\n")
                for link in data['metadata']['links']:
                    f.write(f"- {link}\n")
                if data['structured']['tables']:
                    f.write("\nTables found: " + str(len(data['structured']['tables'])) + "\n")
                if data['structured']['lists']:
                    f.write("\nLists found: " + str(len(data['structured']['lists'])) + "\n")
                f.write(f"{'='*50}\n")

            # Save to .csv file
            with open(self.output_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow([
                    data['url'],
                    data['title'],
                    data['depth'],
                    " | ".join(data['unstructured']['headings']),
                    " | ".join(data['unstructured']['paragraphs']),
                    " | ".join(data['metadata']['links']),
                    len(data['structured']['tables']),
                    len(data['structured']['lists'])
                ])
        except Exception as e:
            print(f"Error saving to file: {e}")

    def solve_captcha(self, captcha_url):
        """Placeholder for CAPTCHA solving (requires TwoCaptcha or manual implementation)"""
        if not self.two_captcha_api_key:
            print("No TwoCaptcha API key provided, cannot solve CAPTCHA")
            return None
        try:
            from twocaptcha import TwoCaptcha
            solver = TwoCaptcha(self.two_captcha_api_key)
            result = solver.normal(captcha_url)
            return result["code"]
        except Exception as e:
            print(f"CAPTCHA solving failed: {e}")
            return None

    def scrape_page(self, url, depth=0, path=None):
        """Main scraping function using BeautifulSoup and requests"""
        if depth > self.max_depth or url in self.visited_urls:
            return

        self.visited_urls.add(url)
        path = path or [url]

        # Try with requests first
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            page_content = response.text
        except requests.RequestException as e:
            print(f"Failed to fetch {url} with requests: {e}")
            # Fallback to Selenium for dynamic content
            try:
                self.driver.get(url)
                time.sleep(2)
                page_content = self.driver.page_source
            except Exception as e:
                print(f"Failed to fetch {url} with Selenium: {e}")
                return

        # Parse with BeautifulSoup
        soup = BeautifulSoup(page_content, 'html.parser')

        # Check for CAPTCHA
        captcha_detected = soup.find(text=lambda text: text and "captcha" in text.lower())
        if captcha_detected:
            try:
                captcha_img = soup.find('img', id='captcha')
                if captcha_img:
                    captcha_url = urljoin(url, captcha_img['src'])
                    captcha_code = self.solve_captcha(captcha_url)
                    if captcha_code:
                        captcha_input = self.driver.find_element(By.ID, "captcha_input")
                        captcha_input.send_keys(captcha_code)
                        self.driver.find_element(By.ID, "submit").click()
                        time.sleep(2)
                        page_content = self.driver.page_source
                        soup = BeautifulSoup(page_content, 'html.parser')
                        print("CAPTCHA solved successfully")
                    else:
                        print("Failed to solve CAPTCHA")
            except Exception as e:
                print(f"CAPTCHA handling failed: {e}")

        # Extract data
        data = {
            "url": url,
            "title": soup.title.text if soup.title else "No title",
            "structured": {
                "tables": [str(table) for table in soup.find_all('table')],
                "lists": [str(li) for li in soup.find_all(['ul', 'ol'])],
            },
            "unstructured": {
                "paragraphs": [p.get_text(strip=True) for p in soup.find_all('p')],
                "headings": [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2', 'h3'])],
            },
            "metadata": {
                "links": [a['href'] for a in soup.find_all('a', href=True)],
                "meta_tags": [meta.get('content') for meta in soup.find_all('meta') if meta.get('content')],
            },
            "type": "mixed",
            "depth": depth
        }

        # Save to both files
        self.save_to_file(data)

        # Follow links
        if depth < self.max_depth:
            for link in soup.find_all('a', href=True):
                next_url = urljoin(url, link['href'])
                if (next_url.startswith('http') and 

                    any(domain in urlparse(next_url).netloc for domain in self.allowed_domains) and 
                    next_url not in self.visited_urls):
                    new_path = path + [next_url]
                    self.scrape_page(next_url, depth + 1, new_path)

    def close(self):
        """Clean up resources"""
        try:
            self.driver.quit()
            self.session.close()
            print(f"Scraped data saved to {self.output_file} and {self.output_csv_file}")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def run_scraper(url, max_depth=2, two_captcha_api_key=None):
    """Run the scraper"""
    scraper = RobustScraper(url, max_depth, two_captcha_api_key)
    try:
        scraper.scrape_page(url)
    finally:
        scraper.close()

if __name__ == "__main__":
    # Take URL as user input
    url = input("Enter the URL to scrape (e.g., https://example.com): ").strip()
    if not url.startswith("http"):
        url = "https://" + url  # Add https if not present
    max_depth = int(input("Enter the maximum depth for crawling (default is 2): ").strip() or 2)
    two_captcha_api_key = input("Enter TwoCaptcha API key (or press Enter to skip): ").strip() or None
    number_of_word = int(input())
    run_scraper(url, max_depth, two_captcha_api_key)

    # https://en.wikipedia.org/wiki/Artificial_intelligence