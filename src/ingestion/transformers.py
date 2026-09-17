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
