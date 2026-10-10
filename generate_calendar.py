import os
import requests
from datetime import datetime, timezone, timedelta
from ics import Calendar, Event

TEAMS = [
    {
        "id": 266195,
        "name": "Napoli Basket"
    }
]

calendar = Calendar()

for team in TEAMS:

    url = f"https://sofascore-sport-api.p.rapidapi.com/api/team/{team['id']}/events/next/0"

    headers = {
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
        "x-rapidapi-host": "sofascore-sport-api.p.rapidapi.com",
        "accept": "application/json"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()
    events = data["events"]

    for match in events:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        competition = match["tournament"]["uniqueTournament"]["name"]

        start = datetime.fromtimestamp(
            match["startTimestamp"],
            timezone.utc
        )

        event = Event()

        event.uid = str(match["id"])

        event.name = f"[{competition}] {home} vs {away}"

        event.begin = start

        event.duration = timedelta(hours=2)

        event.description = (
            f"Competition: {competition}\n"
            f"Match: {home} vs {away}\n"
            f"https://www.sofascore.com/{match['slug']}/{match['id']}"
        )

        calendar.events.add(event)

with open("sports.ics", "w", encoding="utf-8") as file:
    file.writelines(calendar)

print(f"Generated {len(calendar.events)} events")
