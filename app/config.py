
import os

from dotenv import load_dotenv

load_dotenv()

ALLRATES_API_KEY = os.getenv("ALLRATES_API_KEY")

ALLRATES_BASE_URL = "https://allratestoday.com/api"

if not ALLRATES_API_KEY:
    raise RuntimeError(
        "ALLRATES_API_KEY is missing. Please configure it in your .env file."
    )
