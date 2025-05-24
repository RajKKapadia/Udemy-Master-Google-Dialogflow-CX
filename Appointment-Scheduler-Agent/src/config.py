import os
import json

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

X_API_KEY = os.getenv("X_API_KEY")

SERVICE_ACCOUNT_JSON = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))
GOOGLE_CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

MEETING_TIME = 30
