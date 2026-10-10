import os
import requests
from datetime import datetime, timezone, timedelta
from ics import Calendar, Event

TEAMS = [
    {
        "id": 266195,
        "name": "Napoli Basket"
    }  , 
    {
        "id": 2714,
        "name": "SSC Napoli"
    }  , 
    {
        "id": 7057,
        "name": "Italia"
    }
]

calendar = Calendar()

def get_icon(competition):

    competition = competition.lower()

    if "lega a" in competition:
        return "🏀"

    if "eurocup" in competition:
        return "🏆🏀"

    if "serie a" in competition:
        return "⚽"

    if "champions" in competition:
        return "🌟⚽"

    if "six nations" in competition:
        return "🏉🇪🇺"

    if "world cup" in competition:
        return "🏆🏉"

    if "rugby" in competition:
        return "🏉"

    return "📅"

for team in TEAMS:


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

        icon = get_icon(competition)

        event.name = f"{icon} {home} vs {away}"

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
