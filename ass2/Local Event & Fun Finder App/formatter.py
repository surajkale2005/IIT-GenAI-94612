def format_events(events, city):
    if not events:
        return f"\n No events found in {city}."

    output = f"\n Top Events in {city}:\n"
    output += "-" * 30 + "\n"

    for event in events[:5]:
        name = event.get("name", "N/A")
        date = event.get("dates", {}).get("start", {}).get("localDate", "N/A")
        venue = event.get("_embedded", {}).get("venues", [{}])[0].get("name", "N/A")

        output += (
            f"\n Event: {name}"
            f"\n Date: {date}"
            f"\n Venue: {venue}\n"
        )

    return output
