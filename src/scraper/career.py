from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Auto-install latest ChromeDriver
service = Service(ChromeDriverManager().install())

# Chrome Options to fix GPU & network errors
options = Options()
options.add_argument("--headless")  # Run in headless mode (Remove if you want UI)
options.add_argument("--disable-gpu")  # Fix GPU errors
options.add_argument("--no-sandbox")
options.add_argument("--disable-software-rasterizer")
options.add_argument("--disable-features=NetworkService")
options.add_argument("--disable-features=VizDisplayCompositor")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--proxy-server='direct://'")
options.add_argument("--proxy-bypass-list=*")
options.add_argument("--disable-webrtc")  # Fix STUN errors

# Start WebDriver
driver = webdriver.Chrome(service=service, options=options)

# Open LinkedIn Jobs Page (Public URL)
driver.get("https://www.linkedin.com/jobs/collections/recommended/?currentJobId=4156603602&discover=recommended&discoveryOrigin=JOBS_HOME_JYMBII")

# Wait for page to load (Max 10 sec)
wait = WebDriverWait(driver, 10)
wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='main-content']/section[2]/ul")))

# Find all job listings
job_listings = driver.find_elements(By.XPATH, "//*[@id='main-content']/section[2]/ul/li")

# Loop through each job listing
for job in job_listings:
    try:
        job_title = job.find_element(By.XPATH, ".//span[@aria-hidden='true']/strong").text.strip()
    except Exception:
        job_title = "N/A"

    try:
        job_address = job.find_element(By.CLASS_NAME, "job-card-container__metadata-wrapper").text.strip()
    except Exception:
        job_address = "N/A"

    print(f"Job Title: {job_title}")
    print(f"Job Location: {job_address}")
    print("-" * 50)

# Close the driver
driver.quit()
