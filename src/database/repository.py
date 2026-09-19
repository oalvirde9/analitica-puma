"""Persistencia mínima para el catálogo de equipos."""

from typing import Any

import duckdb


def upsert_team(
    connection: duckdb.DuckDBPyConnection,
    team: dict[str, Any],
) -> int:
    """Inserta o actualiza un equipo y devuelve su identificador interno."""
    result = connection.execute(
        """
        INSERT INTO teams (external_id, name, short_name, country)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (external_id) DO UPDATE SET
            name = EXCLUDED.name,
            short_name = EXCLUDED.short_name,
            country = EXCLUDED.country
        RETURNING id
        """,
        [
            team["external_id"],
            team["name"],
            team["short_name"],
            team["country"],
        ],
    )
    return int(result.fetchone()[0])


def upsert_season(
    connection: duckdb.DuckDBPyConnection,
    season: dict[str, Any],
) -> int:
    """Inserta o actualiza una temporada y devuelve su identificador interno."""
    result = connection.execute(
        """
        INSERT INTO seasons (external_id, name, start_date, end_date)
        VALUES (?, ?, ?, ?)
        ON CONFLICT (external_id) DO UPDATE SET
            name = EXCLUDED.name,
            start_date = EXCLUDED.start_date,
            end_date = EXCLUDED.end_date
        RETURNING id
        """,
        [
            season["external_id"],
            season["name"],
            season["start_date"],
            season["end_date"],
        ],
    )
    return int(result.fetchone()[0])


def upsert_match(
    connection: duckdb.DuckDBPyConnection,
    match: dict[str, Any],
) -> int:
    """Inserta o actualiza un partido y devuelve su identificador interno."""
    result = connection.execute(
        """
        INSERT INTO matches (
            external_id,
            season_id,
            date,
            home_team_id,
            away_team_id,
            home_score,
            away_score,
            home_xg,
            away_xg,
            status,
            venue
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (external_id) DO UPDATE SET
            season_id = EXCLUDED.season_id,
            date = EXCLUDED.date,
            home_team_id = EXCLUDED.home_team_id,
            away_team_id = EXCLUDED.away_team_id,
            home_score = EXCLUDED.home_score,
            away_score = EXCLUDED.away_score,
            home_xg = EXCLUDED.home_xg,
            away_xg = EXCLUDED.away_xg,
            status = EXCLUDED.status,
            venue = EXCLUDED.venue
        RETURNING id
        """,
        [
            match["external_id"],
            match["season_id"],
            match["date"],
            match["home_team_id"],
            match["away_team_id"],
            match["home_score"],
            match["away_score"],
            match["home_xg"],
            match["away_xg"],
            match["status"],
            match["venue"],
        ],
    )
    return int(result.fetchone()[0])
