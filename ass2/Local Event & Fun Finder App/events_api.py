import requests
from utils import EVENT_API_KEY


def get_events(city):
    if not EVENT_API_KEY:
        print(" API key not found!")
        return []

    url = (
        "https://app.ticketmaster.com/discovery/v2/events.json"
        f"?city={city}&apikey={EVENT_API_KEY}"
    )

    response = requests.get(url)

    if response.status_code != 200:
        return []

    data = response.json()
    return data.get("_embedded", {}).get("events", [])
