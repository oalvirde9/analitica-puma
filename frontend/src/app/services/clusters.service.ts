import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { API_BASE_URL } from '../config/api.config';

export interface ClusterPlayer {
  player_id: number;
  player_name: string;
  position_group: string;
  total_valid_minutes: number;
  cluster: number;
  profile_name: string;
  profile_description: string;
  shots_per90: number;
  key_passes_per90: number;
  passes_in_final_third_per90: number;
  successful_dribbles_per90: number;
  passes_per90: number;
  pass_accuracy: number;
  total_duels_per90: number;
  duel_success: number;
  ball_recoveries_per90: number;
  interceptions_per90: number;
}

export interface ClusterResponse {
  tournament: string;
  count: number;
  data: ClusterPlayer[];
}

export interface PcaPlayer {
  player_id: number;
  player_name: string;
  position_group: string;
  total_valid_minutes: number;
  cluster: number;
  profile_name: string;
  PC1: number;
  PC2: number;
  PC3: number;
  PC4: number;
  PC5: number;
}

export interface PcaResponse {
  tournament: string;
  count: number;
  components_used_for_clustering: number;
  data: PcaPlayer[];
}

@Injectable({
  providedIn: 'root'
})
export class ClustersService {
  private readonly http = inject(HttpClient);
  private readonly apiUrl = `${API_BASE_URL}/api`;

  getClusters(tournament: string): Observable<ClusterResponse> {
    return this.http.get<ClusterResponse>(
      `${this.apiUrl}/clusters/${encodeURIComponent(tournament)}`
    );
  }

  getPca(tournament: string): Observable<PcaResponse> {
    return this.http.get<PcaResponse>(
      `${this.apiUrl}/pca/${encodeURIComponent(tournament)}`
    );
  }
}
