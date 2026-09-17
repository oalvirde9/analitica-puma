-- Esquema principal de Analítica Puma para datos de Liga MX.
-- No incluye tablas de PPS, TPI, Elo ni modelos de aprendizaje automático.

CREATE SEQUENCE IF NOT EXISTS teams_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS seasons_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS players_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS matches_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS match_team_stats_id_seq START 1;
CREATE SEQUENCE IF NOT EXISTS player_match_stats_id_seq START 1;

-- Catálogo de equipos.
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY DEFAULT nextval('teams_id_seq'),
    external_id VARCHAR UNIQUE,
    name VARCHAR NOT NULL,
    short_name VARCHAR,
    country VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name)
);

-- Catálogo de temporadas.
CREATE TABLE IF NOT EXISTS seasons (
    id INTEGER PRIMARY KEY DEFAULT nextval('seasons_id_seq'),
    external_id VARCHAR UNIQUE,
    name VARCHAR NOT NULL,
    start_date DATE,
    end_date DATE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (name),
    CHECK (end_date IS NULL OR start_date IS NULL OR end_date >= start_date)
);

-- Catálogo de jugadores.
CREATE TABLE IF NOT EXISTS players (
    id INTEGER PRIMARY KEY DEFAULT nextval('players_id_seq'),
    external_id VARCHAR UNIQUE,
    name VARCHAR NOT NULL,
    first_name VARCHAR,
    last_name VARCHAR,
    position VARCHAR,
    date_of_birth DATE,
    nationality VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Partidos disputados, con sus equipos, marcador y métricas agregadas.
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY DEFAULT nextval('matches_id_seq'),
    external_id VARCHAR UNIQUE,
    season_id INTEGER NOT NULL,
    date DATE NOT NULL,
    home_team_id INTEGER NOT NULL,
    away_team_id INTEGER NOT NULL,
    home_score INTEGER,
    away_score INTEGER,
    home_xg DOUBLE,
    away_xg DOUBLE,
    status VARCHAR NOT NULL,
    venue VARCHAR,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (season_id) REFERENCES seasons (id),
    FOREIGN KEY (home_team_id) REFERENCES teams (id),
    FOREIGN KEY (away_team_id) REFERENCES teams (id),
    CHECK (home_team_id <> away_team_id),
    CHECK (home_score IS NULL OR home_score >= 0),
    CHECK (away_score IS NULL OR away_score >= 0),
    CHECK (home_xg IS NULL OR home_xg >= 0),
    CHECK (away_xg IS NULL OR away_xg >= 0)
);

-- Estadísticas agregadas de cada equipo en un partido.
CREATE TABLE IF NOT EXISTS match_team_stats (
    id INTEGER PRIMARY KEY DEFAULT nextval('match_team_stats_id_seq'),
    match_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    possession DOUBLE,
    shots INTEGER,
    shots_on_target INTEGER,
    passes INTEGER,
    passes_completed INTEGER,
    pass_accuracy DOUBLE,
    corners INTEGER,
    fouls INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    xg DOUBLE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches (id),
    FOREIGN KEY (team_id) REFERENCES teams (id),
    UNIQUE (match_id, team_id),
    CHECK (possession IS NULL OR (possession >= 0 AND possession <= 100)),
    CHECK (pass_accuracy IS NULL OR (pass_accuracy >= 0 AND pass_accuracy <= 100)),
    CHECK (shots IS NULL OR shots >= 0),
    CHECK (shots_on_target IS NULL OR shots_on_target >= 0),
    CHECK (xg IS NULL OR xg >= 0)
);

-- Estadísticas individuales de cada jugador en un partido.
CREATE TABLE IF NOT EXISTS player_match_stats (
    id INTEGER PRIMARY KEY DEFAULT nextval('player_match_stats_id_seq'),
    match_id INTEGER NOT NULL,
    player_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    minutes INTEGER,
    started BOOLEAN,
    goals INTEGER,
    assists INTEGER,
    shots INTEGER,
    shots_on_target INTEGER,
    xg DOUBLE,
    xa DOUBLE,
    passes INTEGER,
    passes_completed INTEGER,
    key_passes INTEGER,
    dribbles INTEGER,
    tackles INTEGER,
    interceptions INTEGER,
    recoveries INTEGER,
    duels_won INTEGER,
    duels_lost INTEGER,
    fouls INTEGER,
    yellow_cards INTEGER,
    red_cards INTEGER,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (match_id) REFERENCES matches (id),
    FOREIGN KEY (player_id) REFERENCES players (id),
    FOREIGN KEY (team_id) REFERENCES teams (id),
    UNIQUE (match_id, player_id),
    CHECK (minutes IS NULL OR (minutes >= 0 AND minutes <= 120)),
    CHECK (goals IS NULL OR goals >= 0),
    CHECK (assists IS NULL OR assists >= 0),
    CHECK (xg IS NULL OR xg >= 0),
    CHECK (xa IS NULL OR xa >= 0)
);

-- Índices para las relaciones y consultas frecuentes por temporada, fecha y equipo.
CREATE INDEX IF NOT EXISTS idx_matches_season_id ON matches (season_id);
CREATE INDEX IF NOT EXISTS idx_matches_date ON matches (date);
CREATE INDEX IF NOT EXISTS idx_matches_home_team_id ON matches (home_team_id);
CREATE INDEX IF NOT EXISTS idx_matches_away_team_id ON matches (away_team_id);
CREATE INDEX IF NOT EXISTS idx_match_team_stats_team_id ON match_team_stats (team_id);
CREATE INDEX IF NOT EXISTS idx_player_match_stats_player_id ON player_match_stats (player_id);
CREATE INDEX IF NOT EXISTS idx_player_match_stats_team_id ON player_match_stats (team_id);
