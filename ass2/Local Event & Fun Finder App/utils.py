# utils.py
import os
from dotenv import load_dotenv

load_dotenv()  # loads .env file

EVENT_API_KEY = os.getenv("EVENT_API_KEY")


def is_valid_city(city: str) -> bool:
    return len(city.strip()) > 1
