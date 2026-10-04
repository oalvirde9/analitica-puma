import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export type TournamentName = 'Apertura' | 'Clausura';

export interface PlayerEvaluation {
  season_name: string;
  tournament_name: TournamentName;
  player_id: number;
  player_name: string;
  position_group: string;
  appearances: number;
  total_valid_minutes: number;
  pps_v1: number;
  pps_position_rank: number;
  benchmark_pps_pct: number;
  igr_reliability: number;
  igr_v1: number;
  igr_rank: number;
  provider_rating_tournament: number | null;
}

export interface PlayerProfileMetric {
  metric: string;
  metric_label: string;
  direction: 'positive' | 'inverse' | 'descriptive';
  display_format: 'per90' | 'percentage';
  player_value: number;
  reference_value: number;
  difference_pct: number;
  classification: 'Destaca' | 'En línea' | 'Por debajo';
  benchmark_n: number;
}

export interface PlayerProfileEvaluation extends PlayerEvaluation {
  metrics: PlayerProfileMetric[];
}

export interface PlayerProfileResponse {
  player_id: number;
  player_name: string;
  position_group: string;
  evaluations: PlayerProfileEvaluation[];
}


export interface PlayerEvaluationsResponse {
  count: number;
  data: PlayerEvaluation[];
}

export interface PlayerTop10Response {
  tournament: string;
  count: number;
  data: PlayerEvaluation[];
}

@Injectable({
  providedIn: 'root'
})
export class PlayersService {
  private readonly http = inject(HttpClient);

  private readonly evaluationsApiUrl =
    `${API_BASE_URL}/api/evaluations`;

  private readonly playersApiUrl =
    `${API_BASE_URL}/api/players`;

  getEvaluations(): Observable<PlayerEvaluationsResponse> {
    return this.http.get<PlayerEvaluationsResponse>(
      this.evaluationsApiUrl
    );
  }

  getTop10(
    tournament: TournamentName
  ): Observable<PlayerTop10Response> {
    const params = new HttpParams()
      .set('tournament', tournament);

    return this.http.get<PlayerTop10Response>(
      `${this.evaluationsApiUrl}/top10`,
      { params }
    );
  }
  getPlayer(
    playerId: number
  ): Observable<PlayerProfileResponse> {
    return this.http.get<PlayerProfileResponse>(
      `${this.playersApiUrl}/${playerId}`
    );
  }
}
