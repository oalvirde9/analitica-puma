import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  PlayerEvaluation,
  PlayerProfileEvaluation,
  PlayerProfileResponse,
  PlayersService,
  TournamentName
} from '../../services/players.service';

@Component({
  selector: 'app-jugadores-page',
  standalone: true,
  template: `
    <section class="players-evaluation-page">

      <div class="players-evaluation-heading">
        <div>
          <span class="section-kicker">Evaluación de jugadores</span>
          <h2>Rendimiento individual · PPS / IGR</h2>
          <p class="muted">
            Temporada 2025/26 · Evaluación independiente por torneo
          </p>
        </div>

        <div class="players-tournament-control">
          <span>TORNEO</span>

          <div class="players-tournament-selector">
            <button
              type="button"
              [class.active]="selectedTournament === 'Apertura'"
              (click)="selectTournament('Apertura')">
              Apertura
            </button>

            <button
              type="button"
              [class.active]="selectedTournament === 'Clausura'"
              (click)="selectTournament('Clausura')">
              Clausura
            </button>
          </div>
        </div>
      </div>

      @if (loading) {
        <div class="panel players-status">
          Cargando evaluaciones...
        </div>
      }

      @if (error) {
        <div class="panel players-status players-error">
          {{ error }}
        </div>
      }

      @if (!loading && !error) {


@if (selectedPlayer) {
  <div class="player-profile-header">
    <button
      type="button"
      class="player-profile-back"
      (click)="closePlayer()">
      ← Volver al ranking
    </button>

    <div>
      <span class="section-kicker">
        Perfil individual · {{ selectedTournament }} 2025/26
      </span>

      <h2>{{ selectedPlayer.player_name }}</h2>

      <p class="muted">
        {{ positionLabel(selectedPlayer.position_group) }}
      </p>
    </div>
  </div>
}

@if (selectedPlayerEvaluation) {
  <div class="stat-grid players-stat-grid">

    <article class="stat-card">
      <span class="stat-label">PPS</span>
      <strong class="stat-value">
        {{ selectedPlayerEvaluation.pps_v1.toFixed(2) }}
      </strong>
    </article>

    <article class="stat-card accent-gold">
      <span class="stat-label">IGR</span>
      <strong class="stat-value">
        {{ selectedPlayerEvaluation.igr_v1.toFixed(2) }}
      </strong>
    </article>

    <article class="stat-card">
      <span class="stat-label">Partidos</span>
      <strong class="stat-value">
        {{ selectedPlayerEvaluation.appearances }}
      </strong>
    </article>

    <article class="stat-card accent-slate">
      <span class="stat-label">Minutos</span>
      <strong class="stat-value">
        {{ selectedPlayerEvaluation.total_valid_minutes }}
      </strong>
    </article>

  </div>
}

@if (selectedPlayerEvaluation) {
  <article class="panel player-profile-metrics">

    <div class="panel-heading">
      <div>
        <span class="section-kicker">
          Perfil de rendimiento
        </span>
        <h3>Métricas que explican su rendimiento</h3>
      </div>
    </div>

    <div class="player-metrics-list">
      @for (
        metric of selectedPlayerEvaluation.metrics;
        track metric.metric
      ) {
        <div class="player-metric-row">

<div class="player-metric-name">
  {{ metric.metric_label }}
</div>

<div class="player-metric-value">
  @if (metric.display_format === 'percentage') {
    <strong>
      {{ (metric.player_value * 100).toFixed(1) }}%
    </strong>
  } @else {
    <strong>
      {{ metric.player_value.toFixed(2) }}
    </strong>
    <span>por 90 min</span>
  }
</div>

<div class="player-metric-reference">
  Referencia {{ positionLabel(selectedPlayer!.position_group) }}:
  @if (metric.display_format === 'percentage') {
    {{ (metric.reference_value * 100).toFixed(1) }}%
  } @else {
    {{ metric.reference_value.toFixed(2) }}
  }
</div>

<div class="player-metric-comparison">
  <span>
    {{ metric.difference_pct > 0 ? '+' : '' }}
    {{ metric.difference_pct.toFixed(1) }}%
  </span>

  <strong>
    {{ metric.classification }}
  </strong>
</div>

    </div>
      }
    </div>
  </article>
}

@if (!selectedPlayer) {       
 <div class="stat-grid players-stat-grid">

          <article class="stat-card">
            <div class="stat-top">
              <span class="stat-label">Jugadores evaluados</span>
            </div>

            <strong class="stat-value">
              {{ filteredEvaluations.length }}
            </strong>

            <div class="stat-foot">
              <span>{{ selectedTournament }} 2025/26</span>
            </div>
          </article>

          <article class="stat-card accent-gold">
            <div class="stat-top">
              <span class="stat-label">Líder IGR</span>
            </div>

            <strong class="stat-value players-leader-value">
              {{ leader?.igr_v1?.toFixed(1) ?? '—' }}
            </strong>

            <div class="stat-foot">
              <span>{{ leader?.player_name ?? '—' }}</span>
            </div>
          </article>

          <article class="stat-card accent-slate">
            <div class="stat-top">
              <span class="stat-label">IGR promedio</span>
            </div>

            <strong class="stat-value">
              {{ averageIgr.toFixed(1) }}
            </strong>

            <div class="stat-foot">
              <span>Jugadores elegibles del torneo</span>
            </div>
          </article>

         
        </div>

        <article class="panel players-ranking-panel">

          <div class="panel-heading players-ranking-heading">
            <div>
              <span class="section-kicker">
                {{ selectedTournament }} · 2025/26
              </span>
              <h3>Ranking de evaluación individual</h3>
            </div>

            <span class="players-count">
              {{ filteredEvaluations.length }} jugadores
            </span>
          </div>

          <div class="players-table-scroll">
            <table class="players-evaluation-table">
              <thead>
                <tr>
                  <th># IGR</th>
                  <th>Jugador</th>
                  <th>Pos.</th>
                  <th>PJ</th>
                  <th>Min.</th>
                  <th>PPS</th>
                  <th>IGR</th>
                  <th>Rating proveedor</th>
                </tr>
              </thead>

              <tbody>
                @for (
                  player of filteredEvaluations;
                  track player.player_id
                ) {
<tr
  [class.players-top-row]="player.igr_rank <= 3"
  (click)="openPlayer(player.player_id)">
                    <td>
                      <strong class="players-rank">
                        {{ player.igr_rank }}
                      </strong>
                    </td>

                    <td>
                      <strong>{{ player.player_name }}</strong>
                    </td>

                    <td>
                      <span
                        class="position-tag"
                        [class.goalkeeper]="player.position_group === 'GK'"
                        [class.midfield]="player.position_group === 'MF'">
                        {{ positionLabel(player.position_group) }}
                      </span>
                    </td>

                    <td>{{ player.appearances }}</td>

                    <td>
                      {{ player.total_valid_minutes }}
                    </td>

                    <td>
                      <strong class="players-metric">
                        {{ player.pps_v1.toFixed(2) }}
                      </strong>
                    </td>


                    <td>
                      <strong class="players-igr">
                        {{ player.igr_v1.toFixed(2) }}
                      </strong>
                    </td>


                    <td>
                      {{
                        player.provider_rating_tournament !== null
                          ? player.provider_rating_tournament.toFixed(2)
                          : '—'
                      }}
                    </td>
                  </tr>
                }
              </tbody>
            </table>
          </div>

          <div class="players-method-note">
  <strong>PPS</strong> evalúa el rendimiento del jugador
  considerando las métricas relevantes para su posición.
  <strong>IGR</strong> ajusta esa evaluación según la cantidad
  de minutos disputados.
  El rating del proveedor se muestra únicamente como referencia.
</div>

        </article>
}
      }
    </section>
  `
})
export class JugadoresPage implements OnInit {
  private readonly playersService = inject(PlayersService);
  private readonly cdr = inject(ChangeDetectorRef);

  selectedTournament: TournamentName = 'Apertura';

  evaluations: PlayerEvaluation[] = [];
  filteredEvaluations: PlayerEvaluation[] = [];
  selectedPlayer: PlayerProfileResponse | null = null;
  selectedPlayerEvaluation: PlayerProfileEvaluation | null = null;

playerLoading = false;
playerError = '';

  
  loading = true;
  error = '';

  ngOnInit(): void {
    this.loadEvaluations();
  }

  get leader(): PlayerEvaluation | undefined {
    return this.filteredEvaluations[0];
  }

  get averageIgr(): number {
    if (!this.filteredEvaluations.length) {
      return 0;
    }

    return (
      this.filteredEvaluations.reduce(
        (sum, player) => sum + player.igr_v1,
        0
      ) / this.filteredEvaluations.length
    );
  }


  positionLabel(position: string): string {
    const labels: Record<string, string> = {
      GK: 'POR',
      DF: 'DEF',
      MF: 'MED',
      FW: 'DEL'
    };

    return labels[position] ?? position;
  }

selectTournament(tournament: TournamentName): void {
  if (this.selectedTournament === tournament) {
    return;
  }

  this.selectedTournament = tournament;
  this.applyTournament();

  if (this.selectedPlayer) {
    this.selectedPlayerEvaluation =
      this.selectedPlayer.evaluations.find(
        evaluation =>
          evaluation.tournament_name ===
          this.selectedTournament
      ) ?? null;
  }
}


openPlayer(playerId: number): void {
  this.playerLoading = true;
  this.playerError = '';

  this.playersService.getPlayer(playerId).subscribe({
    next: response => {
      this.selectedPlayer = response;

      this.selectedPlayerEvaluation =
        response.evaluations.find(
          evaluation =>
            evaluation.tournament_name ===
            this.selectedTournament
        ) ?? null;

      this.playerLoading = false;
      this.cdr.markForCheck();
    },
    error: error => {
      console.error(
        'Error cargando perfil del jugador:',
        error
      );

      this.playerError =
        'No fue posible cargar el perfil del jugador.';
      this.playerLoading = false;
      this.cdr.markForCheck();
    }
  });
}

closePlayer(): void {
  this.selectedPlayer = null;
  this.selectedPlayerEvaluation = null;
  this.playerError = '';
}


  private loadEvaluations(): void {
    this.loading = true;
    this.error = '';

    this.playersService.getEvaluations().subscribe({
      next: response => {
        this.evaluations = response.data;
        this.applyTournament();
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: error => {
        console.error(
          'Error cargando evaluaciones de jugadores:',
          error
        );

        this.error =
          'No fue posible cargar las evaluaciones de jugadores.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }

  private applyTournament(): void {
    this.filteredEvaluations = this.evaluations
      .filter(
        player =>
          player.tournament_name === this.selectedTournament
      )
      .sort((a, b) => a.igr_rank - b.igr_rank);

    this.cdr.markForCheck();
  }
}
