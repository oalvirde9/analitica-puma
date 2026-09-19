"""Persistencia mínima para el catálogo de equipos."""

from typing import Any

import duckdb


def upsert_player(
    conn: duckdb.DuckDBPyConnection,
    player: dict[str, Any],
) -> int:
    """Inserta o actualiza un jugador y devuelve su identificador interno."""
    result = conn.execute(
        """
        INSERT INTO players (
            external_id,
            name,
            first_name,
            last_name,
            display_name,
            common_name,
            position_id,
            detailed_position_id,
            date_of_birth,
            nationality_id,
            country_id,
            height,
            weight
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (external_id) DO UPDATE SET
            name = EXCLUDED.name,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            display_name = EXCLUDED.display_name,
            common_name = EXCLUDED.common_name,
            position_id = EXCLUDED.position_id,
            detailed_position_id = EXCLUDED.detailed_position_id,
            date_of_birth = EXCLUDED.date_of_birth,
            nationality_id = EXCLUDED.nationality_id,
            country_id = EXCLUDED.country_id,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight
        RETURNING id
        """,
        [
            player["external_id"],
            player["name"],
            player["first_name"],
            player["last_name"],
            player["display_name"],
            player["common_name"],
            player["position_id"],
            player["detailed_position_id"],
            player["date_of_birth"],
            player["nationality_id"],
            player["country_id"],
            player["height"],
            player["weight"],
        ],
    )
    return int(result.fetchone()[0])


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


def upsert_match_team_stats(
    conn: duckdb.DuckDBPyConnection,
    stats: dict[str, Any],
) -> int:
    """Inserta o actualiza estadísticas de un equipo en un partido."""
    result = conn.execute(
        """
        INSERT INTO match_team_stats (
            match_id,
            team_id,
            possession,
            shots,
            shots_on_target,
            passes,
            passes_completed,
            pass_accuracy,
            corners,
            fouls,
            yellow_cards,
            red_cards,
            xg,
            shots_inside_box,
            shots_outside_box,
            shots_blocked,
            long_passes,
            tackles,
            total_crosses,
            accurate_crosses,
            interceptions,
            dribble_attempts,
            successful_dribbles,
            key_passes,
            big_chances_created,
            big_chances_missed,
            successful_long_passes
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT (match_id, team_id) DO UPDATE SET
            possession = EXCLUDED.possession,
            shots = EXCLUDED.shots,
            shots_on_target = EXCLUDED.shots_on_target,
            passes = EXCLUDED.passes,
            passes_completed = EXCLUDED.passes_completed,
            pass_accuracy = EXCLUDED.pass_accuracy,
            corners = EXCLUDED.corners,
            fouls = EXCLUDED.fouls,
            yellow_cards = EXCLUDED.yellow_cards,
            red_cards = EXCLUDED.red_cards,
            xg = EXCLUDED.xg,
            shots_inside_box = EXCLUDED.shots_inside_box,
            shots_outside_box = EXCLUDED.shots_outside_box,
            shots_blocked = EXCLUDED.shots_blocked,
            long_passes = EXCLUDED.long_passes,
            tackles = EXCLUDED.tackles,
            total_crosses = EXCLUDED.total_crosses,
            accurate_crosses = EXCLUDED.accurate_crosses,
            interceptions = EXCLUDED.interceptions,
            dribble_attempts = EXCLUDED.dribble_attempts,
            successful_dribbles = EXCLUDED.successful_dribbles,
            key_passes = EXCLUDED.key_passes,
            big_chances_created = EXCLUDED.big_chances_created,
            big_chances_missed = EXCLUDED.big_chances_missed,
            successful_long_passes = EXCLUDED.successful_long_passes
        RETURNING id
        """,
        [
            stats["match_id"],
            stats["team_id"],
            stats["possession"],
            stats["shots"],
            stats["shots_on_target"],
            stats["passes"],
            stats["passes_completed"],
            stats["pass_accuracy"],
            stats["corners"],
            stats["fouls"],
            stats["yellow_cards"],
            stats["red_cards"],
            stats["xg"],
            stats["shots_inside_box"],
            stats["shots_outside_box"],
            stats["shots_blocked"],
            stats["long_passes"],
            stats["tackles"],
            stats["total_crosses"],
            stats["accurate_crosses"],
            stats["interceptions"],
            stats["dribble_attempts"],
            stats["successful_dribbles"],
            stats["key_passes"],
            stats["big_chances_created"],
            stats["big_chances_missed"],
            stats["successful_long_passes"],
        ],
    )
    return int(result.fetchone()[0])
