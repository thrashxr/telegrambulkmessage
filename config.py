import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent
SESSIONS_DIR = BASE_DIR / "sessions"

SESSIONS_DIR.mkdir(exist_ok=True)

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")

DEFAULT_MESSAGE_DELAY = 60
DEFAULT_GROUP_DELAY = 30
DEFAULT_LOOP_DELAY = 300

def validate_credentials() -> bool:
    if not API_ID or not API_HASH:
        return False
    if API_ID == "your_api_id" or API_HASH == "your_api_hash":
        return False
    return True
