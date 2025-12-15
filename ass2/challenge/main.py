from events_api import get_events
from formatter import format_events
from utils import is_valid_city


def main():
    print(" City Event Finder App")

    city = input("Enter city name: ")

    if not is_valid_city(city):
        print(" Invalid city name.")
        return

    events = get_events(city)
    print(format_events(events, city))


if __name__ == "__main__":
    main()
