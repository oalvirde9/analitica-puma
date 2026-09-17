"""Transformaciones puras de respuestas de Sportmonks."""

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
