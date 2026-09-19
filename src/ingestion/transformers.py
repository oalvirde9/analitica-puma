"""Transformaciones puras de respuestas de Sportmonks."""

from datetime import date
from typing import Any


def flatten_schedule(schedule: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aplana stages, rounds y fixtures conservando cada fixture."""
    return [
        fixture
        for stage in schedule
        for round_data in stage.get("rounds", [])
        for fixture in round_data.get("fixtures", [])
    ]


def transform_team(team: dict[str, Any]) -> dict[str, Any]:
    """Transforma un equipo al formato de inserción de teams."""
    country = team.get("country")
    return {
        "external_id": str(team["id"]),
        "name": team["name"],
        "short_name": team.get("short_code"),
        "country": country if isinstance(country, str) else None,
    }


def extract_unique_teams(
    fixtures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Extrae y transforma los equipos únicos de una lista de fixtures."""
    teams_by_external_id = {}
    for fixture in fixtures:
        for participant in fixture["participants"]:
            team = transform_team(participant)
            teams_by_external_id[team["external_id"]] = team

    return sorted(
        teams_by_external_id.values(),
        key=lambda team: int(team["external_id"]),
    )


def transform_season(season: dict[str, Any]) -> dict[str, Any]:
    """Transforma una temporada al formato de inserción de seasons."""
    return {
        "external_id": str(season["id"]),
        "name": season["name"],
        "start_date": date.fromisoformat(season["starting_at"]),
        "end_date": date.fromisoformat(season["ending_at"]),
    }
