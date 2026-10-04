import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface Team {
  id: number;
  name: string;
  short_code: string;
  image: string;
  score: number | null;
}

export interface Fixture {
  fixture_id: number;
  starting_at: string;
  state_id: number;
  home_team: Team;
  away_team: Team;
  round_id?: number;
  round?: string;
  season_id?: number;
  season_name?: string;
  stage_id?: number;
  tournament_name?: string;
  result_info?: string | null;
}

export interface UpcomingMatchesResponse {
  count: number;
  data: Fixture[];
}

export interface TournamentFixturesResponse {
  season: string;
  tournament: string;
  count: number;
  data: Fixture[];
}

export interface StandingTeam {
  id: number;
  name: string;
  short_code: string;
  image: string;
}

export interface Standing {
  position: number;
  team: StandingTeam;
  played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  movement: string | null;
  round_id: number | null;
  season_id: number;
  season_name: string;
  stage_id: number;
  tournament_name: string;
}

export interface TournamentStandingsResponse {
  season: string;
  tournament: string;
  count: number;
  data: Standing[];
}

export interface PumasStandingResponse {
  season: string;
  tournament: string;
  data: Standing;
}

@Injectable({
  providedIn: 'root'
})
export class MatchesService {
  private readonly http = inject(HttpClient);

  private readonly matchesApiUrl =
    'http://127.0.0.1:8000/api/matches';

  private readonly tournamentApiUrl =
    'http://127.0.0.1:8000/api/tournaments/current';

  getLatest(): Observable<Fixture> {
    return this.http.get<Fixture>(
      `${this.matchesApiUrl}/latest`
    );
  }

  getUpcoming(): Observable<UpcomingMatchesResponse> {
    return this.http.get<UpcomingMatchesResponse>(
      `${this.matchesApiUrl}/upcoming`
    );
  }

  getCurrentFixtures(): Observable<TournamentFixturesResponse> {
    return this.http.get<TournamentFixturesResponse>(
      `${this.tournamentApiUrl}/fixtures`
    );
  }

  getCurrentStandings(): Observable<TournamentStandingsResponse> {
    return this.http.get<TournamentStandingsResponse>(
      `${this.tournamentApiUrl}/standings`
    );
  }

  getPumasStanding(): Observable<PumasStandingResponse> {
    return this.http.get<PumasStandingResponse>(
      `${this.tournamentApiUrl}/pumas`
    );
  }
}
