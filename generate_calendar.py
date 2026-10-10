import os
import requests
from datetime import datetime, timezone, timedelta
from ics import Calendar, Event

TEAMS = [
    {
        "id": 266195,
        "name": "Napoli Basket"
    },
    {
        "id": 2714,
        "name": "SSC Napoli"
    },
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


def load_events(url, headers):

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.json()["events"]


for team in TEAMS:

    headers = {
        "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
        "x-rapidapi-host": "sofascore-sport-api.p.rapidapi.com",
        "accept": "application/json"
    }

    future_url = (
        f"https://sofascore-sport-api.p.rapidapi.com/"
        f"api/team/{team['id']}/events/next/0"
    )

    past_url = (
        f"https://sofascore-sport-api.p.rapidapi.com/"
        f"api/team/{team['id']}/events/last/0"
    )

    future_events = load_events(future_url, headers)

    # ultimi 10 risultati
    past_events = load_events(past_url, headers)[:10]

    events = future_events + past_events

    for match in events:

        home = match["homeTeam"]["name"]
        away = match["awayTeam"]["name"]

        competition = match["tournament"]["uniqueTournament"]["name"]

        icon = get_icon(competition)

        start = datetime.fromtimestamp(
            match["startTimestamp"],
            timezone.utc
        )

        event = Event()

        event.uid = f"{team['id']}-{match['id']}"

        status = match.get("status", {}).get("type", "")

        if status == "finished":

            home_score = (
                match.get("homeScore", {})
                .get("current", 0)
            )

            away_score = (
                match.get("awayScore", {})
                .get("current", 0)
            )

            event.name = (
                f"✅ {icon} "
                f"[{competition}] "
                f"{home} {home_score}-{away_score} {away}"
            )

        else:

            event.name = (
                f"{icon} "
                f"[{competition}] "
                f"{home} vs {away}"
            )

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
