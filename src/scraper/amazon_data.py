
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US, en;q=0.5"
}

# Function to extract product details
def extract_product_details(item):
    title_tag = item.find("span", class_="a-size-medium a-color-base a-text-normal")
    title = title_tag.text.strip() if title_tag else "N/A"
    
    link_tag = item.find("a", class_="a-link-normal s-no-outline")
    product_link = urljoin("https://www.amazon.com", link_tag["href"]) if link_tag else "N/A"
    
    price_tag = item.find("span", class_="a-offscreen")
    price = price_tag.text.strip() if price_tag else "N/A"
    
    rating_tag = item.find("span", class_="a-icon-alt")
    rating = rating_tag.text.strip() if rating_tag else "N/A"
    
    reviews_tag = item.find("span", class_="a-size-base")
    reviews = reviews_tag.text.strip() if reviews_tag else "N/A"
    
    return [title, product_link, price, rating, reviews]

# Function to scrape Amazon data
def scrape_amazon_data(base_url, num_pages, output_file):
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Link", "Price", "Rating", "Reviews"])

        for page in range(1, num_pages + 1):
            page_url = f"{base_url}&page={page}"  # Fix: Directly append the page parameter
            print(f"Fetching: {page_url}")  # Debugging

            try:
                response = requests.get(page_url, headers=HEADERS)
                response.raise_for_status()  # Check for request errors
                soup = BeautifulSoup(response.text, "html.parser")
                items = soup.find_all("div", class_="s-main-slot s-result-list s-search-results sg-row")[0].find_all("div", class_="s-result-item")

                for item in items:
                    product_data = extract_product_details(item)
                    writer.writerow(product_data)

                time.sleep(2)  # Avoid rate limiting
            except requests.exceptions.RequestException as e:
                print(f"Request failed: {e}")
                continue


# Example usage
base_url = "https://www.amazon.com/s?k=laptop&crid=1O1GHJWV4730K&sprefix=laptop%2Caps%2C787&ref=nb_sb_noss_1"
scrape_amazon_data(base_url, 5, "amazon_products.csv")



































# import time
# import os
# import csv
# import requests
# import certifi
# from selenium import webdriver
# from selenium.webdriver.common.by import By





















# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
# from bs4 import BeautifulSoup
# from fake_useragent import UserAgent
# def configure_driver():
#     options = Options()
#     options.add_argument("--headless")  # Run in headless mode
#     options.add_argument("--disable-blink-features=AutomationControlled")
#     options.add_argument(f"user-agent={UserAgent().random}")  # Random User-Agent
#     service = Service(ChromeDriverManager().install())
#     driver = webdriver.Chrome(service=service, options=options)
#     return driver

# def get_product_links(category_url, max_pages=3):
#     driver = configure_driver()
#     driver.get(category_url)
#     time.sleep(3)  # Allow page to load
#     product_links = set()
    
#     for page in range(max_pages):
#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         products = soup.select('a.a-link-normal.s-no-outline')  # Extract product URLs
        
#         for product in products:
#             link = product.get('href')
#             if link and "/dp/" in link:
#                 product_links.add("https://www.amazon.com" + link)
        
#         try:
#             next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
#             driver.execute_script("arguments[0].scrollIntoView();", next_button)
#             time.sleep(2)
#             next_button.click()
#             time.sleep(3)  # Allow time for the next page to load
#         except Exception as e:
#             print(f"No more pages or error: {e}")
#             break  # No next page available
    
#     driver.quit()
#     return list(product_links)

# def get_product_details(product_url):
#     headers = {"User-Agent": UserAgent().random}
#     response = requests.get(product_url, headers=headers, verify=certifi.where())
#     if response.status_code != 200:
#         print(f"Failed to fetch {product_url}, Status Code: {response.status_code}")
#         return None
    
#     soup = BeautifulSoup(response.text, "html.parser")
    
#     def get_text(selector, attr="text"):
#         try:
#             return soup.select_one(selector).text.strip() if attr == "text" else soup.select_one(selector)[attr]
#         except Exception:
#             return "N/A"

#     title = get_text("#productTitle")
#     price = get_text(".a-price .a-offscreen")
#     rating = get_text("span.a-icon-alt")
#     # num_reviews = get_text("#acrCustomerReviewText")
#     description = get_text("#productDescription")
#     # image_url = get_text("#imgTagWrapperId img", "src")
    
#     features = [feature.text.strip() for feature in soup.select("#feature-bullets ul li span.a-list-item")]
#     tech_details = [f"{row.find_all('td')[0].text.strip()}: {row.find_all('td')[1].text.strip()}" 
#                     for row in soup.select("#productDetails_techSpec_section_1 tr") if len(row.find_all('td')) == 2]
#     # additional_details = [f"{row.find_all('td')[0].text.strip()}: {row.find_all('td')[1].text.strip()}" 
#                           #for row in soup.select("#productDetails_detailBullets_sections1 tr") if len(row.find_all('td')) == 2]
#     # best_sellers_rank = get_text("#productDetails_detailBullets_sections1 .a-list-item")

#     return {
#         "Title": title,
#         "Price": price,
#         "Rating": rating,
#         # "Reviews": num_reviews,
#         "Description": description,
#         # "Image URL": image_url,
#         "Features": "; ".join(features),
#         "Technical Details": "; ".join(tech_details),
#         # "Additional Details": "; ".join(additional_details),
#         # "Best Sellers Rank": best_sellers_rank,
#         "Product URL": product_url
#     }

# def scrape_amazon_category(category_url, output_file="amazon_products.csv", max_pages=3):
#     product_links = get_product_links(category_url, max_pages)
#     fieldnames = ["Title", "Price", "Rating",  "Description",  "Features", "Technical Details", "Product URL"]
    
#     with open(output_file, "w", encoding="utf-8", newline="") as file:
#         writer = csv.DictWriter(file, fieldnames=fieldnames)
#         writer.writeheader()
        
#         for idx, product_url in enumerate(product_links):
#             print(f"Scraping {idx+1}/{len(product_links)}: {product_url}")
#             details = get_product_details(product_url)
#             if details:
#                 writer.writerow(details)
    
#     print(f"Scraping completed! Data saved in {output_file}")

# if __name__ == "__main__":
#     category_url = input("Enter the Amazon category URL: ").strip()
#     scrape_amazon_category(category_url, max_pages=2)