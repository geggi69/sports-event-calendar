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

HEADERS = {
    "x-rapidapi-key": os.environ["RAPIDAPI_KEY"],
    "x-rapidapi-host": "sofascore-sport-api.p.rapidapi.com",
    "accept": "application/json"
}


def get_icon(competition, sport):

    competition = competition.lower()
    sport = sport.lower()

    if "lega a" in competition:
        return "🏀"

    if "eurocup" in competition:
        return "🟠🏀"

    if "champions league" in competition:
        return "🌟⚽"

    if competition == "serie a":
        return "⚽"

    if "six nations" in competition:
        return "🏉🇪🇺"

    if "world cup" in competition and sport == "rugby":
        return "🏆🏉"

    if sport == "rugby":
        return "🏉"

    return "📅"


def load_events(team_id, event_type):

    url = (
        f"https://sofascore-sport-api.p.rapidapi.com/"
        f"api/team/{team_id}/events/{event_type}/0"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    return response.json().get("events", [])


events_by_id = {}

#
# Eventi futuri
#
for team in TEAMS:

    future_events = load_events(
        team["id"],
        "next"
    )

    print(
        f"{team['name']} future events: "
        f"{len(future_events)}"
    )

    for match in future_events:

        events_by_id[
            match["id"]
        ] = match

#
# Ultimi 10 eventi passati
#
for team in TEAMS:

    past_events = load_events(
        team["id"],
        "last"
    )[:-10]

    print(
        f"{team['name']} past events: "
        f"{len(past_events)}"
    )

    for match in past_events:

        #
        # Se lo stesso match esiste già
        # nella lista future, il record
        # passato sovrascrive quello futuro
        #
        events_by_id[
            match["id"]
        ] = match

#
# Generazione calendario
#
for match in events_by_id.values():

    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]

    competition = (
        match["tournament"]
        ["uniqueTournament"]
        ["name"]
    )

    sport = (
        match["tournament"]
        ["category"]
        ["sport"]
        ["name"]
    )

    icon = get_icon(
        competition,
        sport
    )

    start = datetime.fromtimestamp(
        match["startTimestamp"],
        timezone.utc
    )

    status = (
        match
        .get("status", {})
        .get("type", "")
    )

    event = Event()

    #
    # UID stabile nel tempo
    #
    event.uid = (
        f"sofascore-{match['id']}"
    )

    event.begin = start

    event.duration = timedelta(
        hours=2
    )

    if status == "finished":

        home_score = (
            match
            .get("homeScore", {})
            .get("display", 0)
        )

        away_score = (
            match
            .get("awayScore", {})
            .get("display", 0)
        )

        event.name = (
            f"✅ {icon} "
            f"[{competition}] "
            f"{home} "
            f"{home_score}-{away_score} "
            f"{away}"
        )

        event.description = (
            f"Competition: {competition}\n"
            f"Final score: "
            f"{home_score}-{away_score}\n"
            f"https://www.sofascore.com/"
            f"{match['slug']}/"
            f"{match['id']}"
        )

    else:

        event.name = (
            f"{icon} "
            f"[{competition}] "
            f"{home} vs {away}"
        )

        event.description = (
            f"Competition: {competition}\n"
            f"Match: {home} vs {away}\n"
            f"https://www.sofascore.com/"
            f"{match['slug']}/"
            f"{match['id']}"
        )

    calendar.events.add(event)

with open(
    "sports.ics",
    "w",
    encoding="utf-8"
) as file:
    file.writelines(calendar)

print(
    f"Generated "
    f"{len(calendar.events)} events"
)
