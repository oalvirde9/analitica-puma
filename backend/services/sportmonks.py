import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SPORTMONKS_API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN")
SPORTMONKS_BASE_URL = "https://api.sportmonks.com/v3/football"

PUMAS_TEAM_ID = 2989


def get_pumas_fixtures():
    if not SPORTMONKS_API_TOKEN:
        raise RuntimeError("SPORTMONKS_API_TOKEN no está configurado.")

    today = date.today()

    # Ventana suficiente para encontrar el último partido
    # y los siguientes encuentros programados.
    start_date = today - timedelta(days=45)
    end_date = today + timedelta(days=60)

    url = (
        f"{SPORTMONKS_BASE_URL}/fixtures/between/"
        f"{start_date.isoformat()}/{end_date.isoformat()}/"
        f"{PUMAS_TEAM_ID}"
    )

    response = requests.get(
        url,
        params={
            "api_token": SPORTMONKS_API_TOKEN,
            "include": "participants;scores",
        },
        timeout=30,
    )

    response.raise_for_status()

    return response.json().get("data", [])


def format_fixture(fixture):
    participants = fixture.get("participants", [])
    scores = fixture.get("scores", [])

    home = next(
        (
            team for team in participants
            if team.get("meta", {}).get("location") == "home"
        ),
        None,
    )

    away = next(
        (
            team for team in participants
            if team.get("meta", {}).get("location") == "away"
        ),
        None,
    )

    current_scores = {
        score["participant_id"]: score.get("score", {}).get("goals")
        for score in scores
        if score.get("description") == "CURRENT"
    }

    return {
        "fixture_id": fixture.get("id"),
        "starting_at": fixture.get("starting_at"),
        "state_id": fixture.get("state_id"),
        "home_team": {
            "id": home.get("id"),
            "name": home.get("name"),
            "short_code": home.get("short_code"),
            "image": home.get("image_path"),
            "score": current_scores.get(home.get("id")),
        } if home else None,
        "away_team": {
            "id": away.get("id"),
            "name": away.get("name"),
            "short_code": away.get("short_code"),
            "image": away.get("image_path"),
            "score": current_scores.get(away.get("id")),
        } if away else None,
    }


def get_latest_and_upcoming():
    from datetime import datetime

    fixtures = get_pumas_fixtures()
    now = datetime.now()

    finished = []
    upcoming = []

    for fixture in fixtures:
        starting_at = fixture.get("starting_at")

        if not starting_at:
            continue

        fixture_datetime = datetime.strptime(
            starting_at,
            "%Y-%m-%d %H:%M:%S",
        )

        if fixture.get("state_id") == 5 and fixture_datetime < now:
            finished.append((fixture_datetime, fixture))

        elif fixture_datetime > now:
            upcoming.append((fixture_datetime, fixture))

    finished.sort(key=lambda item: item[0], reverse=True)
    upcoming.sort(key=lambda item: item[0])

    latest = (
        format_fixture(finished[0][1])
        if finished
        else None
    )

    next_three = [
        format_fixture(fixture)
        for _, fixture in upcoming[:3]
    ]

    return {
        "latest": latest,
        "upcoming": next_three,
    }


# ---------------------------------------------------------------------------
# Apertura 2026
# ---------------------------------------------------------------------------

LIGA_MX_LEAGUE_ID = 743
CURRENT_SEASON_ID = 28009
CURRENT_STAGE_ID = 77482470
CURRENT_SEASON_NAME = "2026/2027"
CURRENT_TOURNAMENT_NAME = "Apertura"


# IDs oficiales de Sportmonks para detalles de standings.
STANDING_DETAIL_TYPES = {
    129: "played",
    130: "wins",
    131: "draws",
    132: "losses",
    133: "goals_for",
    134: "goals_against",
    179: "goal_difference",
    187: "points",
}


def get_pumas_season_schedule():
    """Obtiene y aplana el calendario de Pumas para la temporada actual."""
    if not SPORTMONKS_API_TOKEN:
        raise RuntimeError("SPORTMONKS_API_TOKEN no está configurado.")

    url = (
        f"{SPORTMONKS_BASE_URL}/schedules/seasons/"
        f"{CURRENT_SEASON_ID}/teams/{PUMAS_TEAM_ID}"
    )

    response = requests.get(
        url,
        params={"api_token": SPORTMONKS_API_TOKEN},
        timeout=30,
    )
    response.raise_for_status()

    stages = response.json().get("data", [])
    fixtures = []

    for stage in stages:
        if stage.get("id") != CURRENT_STAGE_ID:
            continue

        for round_data in stage.get("rounds", []):
            round_name = round_data.get("name")

            for fixture in round_data.get("fixtures", []):
                formatted = format_fixture(fixture)

                formatted["round_id"] = round_data.get("id")
                formatted["round"] = round_name
                formatted["season_id"] = CURRENT_SEASON_ID
                formatted["season_name"] = CURRENT_SEASON_NAME
                formatted["stage_id"] = CURRENT_STAGE_ID
                formatted["tournament_name"] = CURRENT_TOURNAMENT_NAME
                formatted["result_info"] = fixture.get("result_info")

                fixtures.append(formatted)

    fixtures.sort(
        key=lambda fixture: fixture.get("starting_at") or ""
    )

    return fixtures


def get_current_standings():
    """Obtiene la tabla del Apertura actual en un formato propio del backend."""
    if not SPORTMONKS_API_TOKEN:
        raise RuntimeError("SPORTMONKS_API_TOKEN no está configurado.")

    url = (
        f"{SPORTMONKS_BASE_URL}/standings/seasons/"
        f"{CURRENT_SEASON_ID}"
    )

    response = requests.get(
        url,
        params={
            "api_token": SPORTMONKS_API_TOKEN,
            "include": "participant;details",
        },
        timeout=30,
    )
    response.raise_for_status()

    standings = []

    for row in response.json().get("data", []):
        if row.get("stage_id") != CURRENT_STAGE_ID:
            continue

        participant = row.get("participant") or {}

        details = {
            STANDING_DETAIL_TYPES[item["type_id"]]: item.get("value")
            for item in row.get("details", [])
            if item.get("type_id") in STANDING_DETAIL_TYPES
        }

        # "points" también viene directamente en el registro principal.
        points = row.get("points")
        if points is None:
            points = details.get("points")

        standings.append(
            {
                "position": row.get("position"),
                "team": {
                    "id": participant.get("id"),
                    "name": participant.get("name"),
                    "short_code": participant.get("short_code"),
                    "image": participant.get("image_path"),
                },
                "played": details.get("played"),
                "wins": details.get("wins"),
                "draws": details.get("draws"),
                "losses": details.get("losses"),
                "goals_for": details.get("goals_for"),
                "goals_against": details.get("goals_against"),
                "goal_difference": details.get("goal_difference"),
                "points": points,
                "movement": row.get("result"),
                "round_id": row.get("round_id"),
                "season_id": CURRENT_SEASON_ID,
                "season_name": CURRENT_SEASON_NAME,
                "stage_id": CURRENT_STAGE_ID,
                "tournament_name": CURRENT_TOURNAMENT_NAME,
            }
        )

    standings.sort(
        key=lambda row: (
            row["position"] is None,
            row["position"] if row["position"] is not None else 999,
        )
    )

    return standings


def get_pumas_current_standing():
    """Devuelve únicamente la posición actual de Pumas."""
    standings = get_current_standings()

    return next(
        (
            row
            for row in standings
            if row.get("team", {}).get("id") == PUMAS_TEAM_ID
        ),
        None,
    )
