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

    url = f"https://www.sofascore.com/api/v1/team/{team['id']}/events/next/0"

    headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Referer": "https://www.sofascore.com/"
}

response = requests.get(
    url,
    headers=headers,
    timeout=30
)
    response.raise_for_status()

    events = response.json()["events"]

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
            f"Match ID: {match['id']}"
        )

        calendar.events.add(event)

with open("sports.ics", "w", encoding="utf-8") as file:
    file.writelines(calendar)

print("Calendar generated")
