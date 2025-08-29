import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

X_API_KEY = os.getenv("X_API_KEY")
