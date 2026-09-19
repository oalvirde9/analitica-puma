"""Transformaciones puras de respuestas de Sportmonks."""

from datetime import date, datetime
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


def transform_match(
    fixture: dict[str, Any],
    season_internal_id: int,
    team_id_by_external_id: dict[str, int],
) -> dict[str, Any]:
    """Transforma un fixture al formato de inserción de matches."""
    participants = fixture.get("participants", [])
    home_participants = [
        participant
        for participant in participants
        if isinstance(participant.get("meta"), dict)
        and participant["meta"].get("location") == "home"
    ]
    away_participants = [
        participant
        for participant in participants
        if isinstance(participant.get("meta"), dict)
        and participant["meta"].get("location") == "away"
    ]
    if len(home_participants) != 1:
        raise ValueError("El fixture debe contener exactamente un participante home")
    if len(away_participants) != 1:
        raise ValueError("El fixture debe contener exactamente un participante away")

    home_external_id = str(home_participants[0]["id"])
    away_external_id = str(away_participants[0]["id"])
    if home_external_id not in team_id_by_external_id:
        raise ValueError(
            f"No existe ID interno para el equipo home {home_external_id}"
        )
    if away_external_id not in team_id_by_external_id:
        raise ValueError(
            f"No existe ID interno para el equipo away {away_external_id}"
        )

    current_scores = [
        score
        for score in fixture.get("scores", [])
        if score.get("description") == "CURRENT"
    ]

    def get_current_score(participant_id: str, location: str) -> Any:
        matching_scores = [
            score
            for score in current_scores
            if str(score.get("participant_id")) == participant_id
        ]
        if len(matching_scores) != 1:
            raise ValueError(
                f"Debe existir exactamente un score CURRENT para {location}"
            )
        value = matching_scores[0].get("score")
        if isinstance(value, dict):
            value = value.get("goals")
        if value is None:
            raise ValueError(f"El score CURRENT de {location} no contiene goles")
        return value

    home_score = get_current_score(home_external_id, "home")
    away_score = get_current_score(away_external_id, "away")

    return {
        "external_id": str(fixture["id"]),
        "season_id": season_internal_id,
        "date": datetime.strptime(fixture["starting_at"], "%Y-%m-%d %H:%M:%S").date(),
        "home_team_id": team_id_by_external_id[home_external_id],
        "away_team_id": team_id_by_external_id[away_external_id],
        "home_score": home_score,
        "away_score": away_score,
        "home_xg": None,
        "away_xg": None,
        "status": None,
        "venue": None,
    }


def transform_team_stats(
    fixture: dict[str, Any],
    match_internal_id: int,
    team_id_by_external_id: dict[str, int],
) -> list[dict[str, Any]]:
    """Transforma estadísticas crudas de equipos al formato de match_team_stats."""
    participants = fixture.get("participants", [])
    if not isinstance(participants, list):
        raise ValueError("fixture.participants debe ser una lista")
    home_participants = []
    away_participants = []
    for participant in participants:
        if not isinstance(participant, dict):
            raise ValueError("Cada participante debe ser un diccionario")
        if participant.get("id") is None:
            raise ValueError("Cada participante debe contener id")
        meta = participant.get("meta")
        location = meta.get("location") if isinstance(meta, dict) else None
        if location == "home":
            home_participants.append(participant)
        elif location == "away":
            away_participants.append(participant)

    if len(home_participants) != 1:
        raise ValueError("El fixture debe contener exactamente un participante home")
    if len(away_participants) != 1:
        raise ValueError("El fixture debe contener exactamente un participante away")

    ordered_participants = [home_participants[0], away_participants[0]]
    internal_ids = []
    for participant in ordered_participants:
        external_id = str(participant["id"])
        if external_id not in team_id_by_external_id:
            raise ValueError(f"No existe ID interno para el equipo {external_id}")
        internal_ids.append(team_id_by_external_id[external_id])

    statistic_columns = {
        45: "possession",
        42: "shots",
        86: "shots_on_target",
        80: "passes",
        81: "passes_completed",
        82: "pass_accuracy",
        34: "corners",
        56: "fouls",
        84: "yellow_cards",
        83: "red_cards",
        49: "shots_inside_box",
        50: "shots_outside_box",
        58: "shots_blocked",
        62: "long_passes",
        78: "tackles",
        98: "total_crosses",
        99: "accurate_crosses",
        100: "interceptions",
        108: "dribble_attempts",
        109: "successful_dribbles",
        117: "key_passes",
        580: "big_chances_created",
        581: "big_chances_missed",
        27264: "successful_long_passes",
    }
    statistics = fixture.get("statistics")
    if statistics is None:
        statistics = []
    if not isinstance(statistics, list):
        raise ValueError("fixture.statistics debe ser una lista o None")

    lookup = {}
    for row in statistics:
        if not isinstance(row, dict):
            raise ValueError("Cada fila de statistics debe ser un diccionario")
        if "participant_id" not in row or "type_id" not in row:
            raise ValueError("Cada fila de statistics debe contener participant_id y type_id")
        key = (str(row["participant_id"]), row["type_id"])
        if key in lookup:
            raise ValueError(
                "Estadística duplicada para "
                f"participant_id={row['participant_id']}, type_id={row['type_id']}"
            )
        lookup[key] = row

    def get_value(participant: dict[str, Any], type_id: int) -> Any:
        participant_id = str(participant["id"])
        row = lookup.get((participant_id, type_id))
        if row is None:
            return None
        data = row.get("data")
        if not isinstance(data, dict):
            raise ValueError(
                f"data inválido para participant_id={participant_id}, type_id={type_id}"
            )
        if "value" not in data:
            raise ValueError(
                f"Falta data.value para participant_id={participant_id}, type_id={type_id}"
            )
        value = data["value"]
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            raise ValueError(
                f"Valor inválido para participant_id={participant_id}, type_id={type_id}"
            )
        return value

    result = []
    for participant, internal_id in zip(ordered_participants, internal_ids):
        team_stats = {
            "match_id": match_internal_id,
            "team_id": internal_id,
        }
        values = {}
        for type_id, column in statistic_columns.items():
            values[column] = get_value(participant, type_id)
        for column in (
            "possession",
            "shots",
            "shots_on_target",
            "passes",
            "passes_completed",
            "pass_accuracy",
            "corners",
            "fouls",
            "yellow_cards",
            "red_cards",
        ):
            team_stats[column] = values[column]
        team_stats["xg"] = None
        for column in (
            "shots_inside_box",
            "shots_outside_box",
            "shots_blocked",
            "long_passes",
            "tackles",
            "total_crosses",
            "accurate_crosses",
            "interceptions",
            "dribble_attempts",
            "successful_dribbles",
            "key_passes",
            "big_chances_created",
            "big_chances_missed",
            "successful_long_passes",
        ):
            team_stats[column] = values[column]
        result.append(team_stats)
    return result


def transform_season(season: dict[str, Any]) -> dict[str, Any]:
    """Transforma una temporada al formato de inserción de seasons."""
    return {
        "external_id": str(season["id"]),
        "name": season["name"],
        "start_date": date.fromisoformat(season["starting_at"]),
        "end_date": date.fromisoformat(season["ending_at"]),
    }
