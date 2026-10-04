from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from requests import RequestException

from backend.services.sportmonks import (
    get_current_standings,
    get_latest_and_upcoming,
    get_pumas_current_standing,
    get_pumas_season_schedule,
)

app = FastAPI(
    title="Analítica Puma API",
    description="Backend de Analítica Puma",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",
        "http://127.0.0.1:4200",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
EVALUATIONS_FILE = (
    BASE_DIR / "data" / "processed" / "pumas_player_evaluation_2025_2026.csv"
)


@app.get("/health", tags=["Sistema"])
def health():
    return {
        "status": "ok",
        "service": "analitica-puma-api",
    }


@app.get("/api/evaluations", tags=["Evaluación"])
def get_evaluations(
    tournament: str | None = Query(
        default=None,
        description="Filtrar por torneo, por ejemplo Apertura o Clausura",
    )
):
    if not EVALUATIONS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de evaluaciones.",
        )

    df = pd.read_csv(EVALUATIONS_FILE)

    if tournament:
        mask = (
            df["tournament_name"]
            .str.casefold()
            .eq(tournament.casefold())
        )
        df = df.loc[mask]

    df = df.sort_values(
        ["tournament_name", "igr_rank"],
        ascending=[True, True],
    )

    return {
        "count": len(df),
        "data": df.to_dict(orient="records"),
    }


@app.get("/api/evaluations/top10", tags=["Evaluación"])
def get_top10_evaluations(
    tournament: str = Query(
        ...,
        description="Torneo: Apertura o Clausura",
    )
):
    if not EVALUATIONS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de evaluaciones.",
        )

    df = pd.read_csv(EVALUATIONS_FILE)

    mask = (
        df["tournament_name"]
        .str.casefold()
        .eq(tournament.casefold())
    )
    df = df.loc[mask]

    if df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron evaluaciones para {tournament}.",
        )

    top10 = (
        df.sort_values("igr_rank")
        .head(10)
    )

    return {
        "tournament": tournament,
        "count": len(top10),
        "data": top10.to_dict(orient="records"),
    }

PLAYER_PROFILE_FILE = (
    BASE_DIR / "data" / "processed" / "pumas_player_profile_2025_2026.csv"
)



@app.get("/api/players/{player_id}", tags=["Jugadores"])
def get_player(player_id: int):
    if not EVALUATIONS_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de evaluaciones.",
        )

    if not PLAYER_PROFILE_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de perfiles de jugadores.",
        )

    # Evaluación principal: PPS / IGR
    evaluations_df = pd.read_csv(EVALUATIONS_FILE)

    player_df = evaluations_df.loc[
        evaluations_df["player_id"] == player_id
    ].copy()

    if player_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontró el jugador con player_id={player_id}.",
        )

    player_df = player_df.sort_values("tournament_name")

    # Métricas explicativas del perfil individual
    profiles_df = pd.read_csv(PLAYER_PROFILE_FILE)

    player_metrics = profiles_df.loc[
        profiles_df["player_id"] == player_id
    ].copy()

    evaluations = []

    for evaluation in player_df.to_dict(orient="records"):
        season = evaluation["season_name"]
        tournament = evaluation["tournament_name"]

        metrics = player_metrics.loc[
            (player_metrics["season_name"] == season)
            & (player_metrics["tournament_name"] == tournament)
        ].copy()

        metric_columns = [
            "metric",
            "metric_label",
            "direction",
            "display_format",
            "player_value",
            "reference_value",
            "difference_pct",
            "classification",
            "benchmark_n",
        ]

        metrics = metrics[metric_columns]

        evaluation["metrics"] = metrics.to_dict(orient="records")
        evaluations.append(evaluation)

    return {
        "player_id": player_id,
        "player_name": player_df.iloc[0]["player_name"],
        "position_group": player_df.iloc[0]["position_group"],
        "evaluations": evaluations,
    }



PCA_CLUSTERING_FILE = (
    BASE_DIR / "data" / "processed" / "pumas_pca_clustering_2025_2026.csv"
)


@app.get("/api/clusters/{tournament}", tags=["Modelos"])
def get_clusters(tournament: str):
    if not PCA_CLUSTERING_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de PCA y clustering.",
        )

    df = pd.read_csv(PCA_CLUSTERING_FILE)

    tournament_df = df.loc[
        df["tournament"]
        .str.casefold()
        .eq(tournament.casefold())
    ].copy()

    if tournament_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron perfiles para {tournament}.",
        )

    columns = [
        "player_id",
        "player_name",
        "position_group",
        "total_valid_minutes",
        "cluster",
        "profile_name",
        "profile_description",
        "shots_per90",
        "key_passes_per90",
        "passes_in_final_third_per90",
        "successful_dribbles_per90",
        "passes_per90",
        "pass_accuracy",
        "total_duels_per90",
        "duel_success",
        "ball_recoveries_per90",
        "interceptions_per90",
    ]

    tournament_df = tournament_df[columns].sort_values(
        ["cluster", "player_name"]
    )

    return {
        "tournament": tournament,
        "count": len(tournament_df),
        "data": tournament_df.to_dict(orient="records"),
    }


@app.get("/api/pca/{tournament}", tags=["Modelos"])
def get_pca(tournament: str):
    if not PCA_CLUSTERING_FILE.exists():
        raise HTTPException(
            status_code=500,
            detail="No se encontró el archivo de PCA y clustering.",
        )

    df = pd.read_csv(PCA_CLUSTERING_FILE)

    tournament_df = df.loc[
        df["tournament"]
        .str.casefold()
        .eq(tournament.casefold())
    ].copy()

    if tournament_df.empty:
        raise HTTPException(
            status_code=404,
            detail=f"No se encontraron datos PCA para {tournament}.",
        )

    columns = [
        "player_id",
        "player_name",
        "position_group",
        "total_valid_minutes",
        "cluster",
        "profile_name",
        "PC1",
        "PC2",
        "PC3",
        "PC4",
        "PC5",
    ]

    tournament_df = tournament_df[columns].sort_values(
        ["cluster", "player_name"]
    )

    return {
        "tournament": tournament,
        "count": len(tournament_df),
        "components_used_for_clustering": 5,
        "data": tournament_df.to_dict(orient="records"),
    }


@app.get("/api/matches/latest", tags=["Partidos"])
def get_latest_match():
    try:
        result = get_latest_and_upcoming()
    except (RequestException, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible obtener los partidos desde Sportmonks.",
        ) from exc

    if result["latest"] is None:
        raise HTTPException(
            status_code=404,
            detail="No se encontró un partido terminado de Pumas.",
        )

    return result["latest"]


@app.get("/api/matches/upcoming", tags=["Partidos"])
def get_upcoming_matches():
    try:
        result = get_latest_and_upcoming()
    except (RequestException, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible obtener los partidos desde Sportmonks.",
        ) from exc

    return {
        "count": len(result["upcoming"]),
        "data": result["upcoming"],
    }


@app.get("/api/tournaments/current/fixtures", tags=["Torneo"])
def get_current_tournament_fixtures():
    try:
        fixtures = get_pumas_season_schedule()
    except (RequestException, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible obtener el calendario desde Sportmonks.",
        ) from exc

    return {
        "season": "2026/2027",
        "tournament": "Apertura",
        "count": len(fixtures),
        "data": fixtures,
    }


@app.get("/api/tournaments/current/standings", tags=["Torneo"])
def get_current_tournament_standings():
    try:
        standings = get_current_standings()
    except (RequestException, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible obtener la clasificación desde Sportmonks.",
        ) from exc

    return {
        "season": "2026/2027",
        "tournament": "Apertura",
        "count": len(standings),
        "data": standings,
    }


@app.get("/api/tournaments/current/pumas", tags=["Torneo"])
def get_current_pumas_standing():
    try:
        pumas = get_pumas_current_standing()
    except (RequestException, RuntimeError) as exc:
        raise HTTPException(
            status_code=502,
            detail="No fue posible obtener la posición de Pumas desde Sportmonks.",
        ) from exc

    if pumas is None:
        raise HTTPException(
            status_code=404,
            detail="Pumas no apareció en la clasificación actual.",
        )

    return {
        "season": "2026/2027",
        "tournament": "Apertura",
        "data": pumas,
    }

