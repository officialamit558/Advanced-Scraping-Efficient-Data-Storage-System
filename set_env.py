# set_env.py
import os
from dotenv import load_dotenv
import subprocess

load_dotenv()  # Load .env file
app_name = "scraping-efficient-data-app"  # Replace with your app name

for key, value in os.environ.items():
    if key in [
        "MONGO_URI", "PG_URI", "NEO4J_URI", "NEO4J_PASSWORD", "ES_HOST", "REDIS_HOST",
        "TWO_CAPTCHA_API_KEY", "PROXY_HOST", "PROXY_PORT", "PROXY_USER", "PROXY_PASSWORD",
        "DOWNLOAD_DELAY", "LOG_LEVEL"
    ]:
        subprocess.run(["heroku", "config:set", f"{key}={value}", "-a", app_name])
        print(f"Set {key}={value}")