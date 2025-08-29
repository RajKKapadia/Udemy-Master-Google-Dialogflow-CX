import os
import json

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

X_API_KEY = os.getenv("X_API_KEY")

SERVICE_ACCOUNT_JSON = json.loads(os.getenv("SERVICE_ACCOUNT_JSON"))

PROJECT_ID = "youtube-dialogflow-cx"
LOCATION = "global"
AGENT_ID = "d23c3df0-06ff-4e38-9ea3-469630288825"

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
