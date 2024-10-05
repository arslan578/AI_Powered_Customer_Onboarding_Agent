# app/config.py
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

SaaS_API_KEY = os.getenv("SaaS_API_KEY", "test_api_key")
