import time
import json
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class TwitterScraper:
    def __init__(self, username, password, target_url, max_tweets=50):
        self.username = username
        self.password = password
        self.target_url = target_url
        self.max_tweets = max_tweets
        self.tweets = []
        
        # Setup Selenium WebDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_driver_path = "C:\Users\amit7\advanced_scraping_system\advanced_scraping_system\src\scraper\chromedriver.exe"  # Update with actual path
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        
    def login(self):
        """Logs into Twitter/X."""
        self.driver.get("https://twitter.com/login")
        time.sleep(3)
        
        username_input = self.driver.find_element(By.NAME, "text")
        username_input.send_keys(self.username)
        username_input.send_keys(Keys.RETURN)
        time.sleep(3)
        
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        time.sleep(5)
    
    def scrape_tweets(self):
        """Scrapes tweets from the target URL."""
        self.driver.get(self.target_url)
        time.sleep(5)
        
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        
        while len(self.tweets) < self.max_tweets:
            tweets_elements = self.driver.find_elements(By.XPATH, "//article[@data-testid='tweet']")
            for tweet in tweets_elements[:self.max_tweets]:
                try:
                    content = tweet.find_element(By.XPATH, ".//div[@lang]").text
                    timestamp = tweet.find_element(By.XPATH, ".//time").get_attribute("datetime")
                    likes = tweet.find_element(By.XPATH, ".//div[@data-testid='like']/div/span").text
                    retweets = tweet.find_element(By.XPATH, ".//div[@data-testid='retweet']/div/span").text
                    self.tweets.append({
                        "content": content,
                        "timestamp": timestamp,
                        "likes": likes,
                        "retweets": retweets
                    })
                except Exception as e:
                    continue
            
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
    def save_tweets(self):
        """Saves scraped tweets to a JSON file."""
        filename = f"tweets_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(self.tweets, f, indent=4)
        print(f"Saved {len(self.tweets)} tweets to {filename}")
    
    def close(self):
        """Closes the WebDriver."""
        self.driver.quit()
        
    def run(self):
        self.login()
        self.scrape_tweets()
        self.save_tweets()
        self.close()

if __name__ == "__main__":
    username = input("Enter your Twitter/X username: ")
    password = input("Enter your password: ")
    target_url = input("Enter the profile or hashtag URL: ")
    scraper = TwitterScraper(username, password, target_url)
    scraper.run()
