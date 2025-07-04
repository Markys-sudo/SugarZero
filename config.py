import os
from datetime import datetime

if os.path.exists(".env"):
    from dotenv import load_dotenv
    load_dotenv()

TOKEN_TG = os.getenv('TOKEN_TG')
TOKEN_GPT = os.getenv('TOKEN_GPT')
PROXY_GPT = os.getenv('PROXY_GPT')
SPOONACULAR_API = os.getenv('SPOONACULAR_API_KEY')

LOG_FILE = f"logs/log_call_{datetime.now().strftime('%Y-%m-%d')}.log"
CACHE_FILE = 'cache/nutrition_cache.json'
