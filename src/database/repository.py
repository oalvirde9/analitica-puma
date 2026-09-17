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
