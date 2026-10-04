import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  ClusterPlayer,
  ClustersService
} from '../../services/clusters.service';

@Component({
  selector: 'app-clusters-page',
  standalone: true,
  template: `
    <section class="panel">
      <div>
        <h2>Perfiles de jugadores</h2>
      </div>

      <div class="tournament-switch">
        <button
          type="button"
          [class.active]="tournament === 'Apertura'"
          (click)="selectTournament('Apertura')"
        >
          Apertura
        </button>

        <button
          type="button"
          [class.active]="tournament === 'Clausura'"
          (click)="selectTournament('Clausura')"
        >
          Clausura
        </button>
      </div>

      @if (loading) {
        <p>Cargando perfiles...</p>
      }

      @if (error) {
        <p>{{ error }}</p>
      }

      @if (!loading && !error) {
        <p>
          <strong>{{ clusterPlayers.length }}</strong> jugadores analizados ·
          <strong>{{ profileCount }}</strong> perfiles estadísticos
        </p>

        <div class="profiles-grid">
          @for (profile of profiles; track profile.cluster) {
            <article class="profile-card">
              <div class="profile-card-header">
                <span>PERFIL</span>
                <strong>{{ profile.players.length }} jugadores</strong>
              </div>

              <h3>{{ profile.name }}</h3>

              <p>{{ profile.description }}</p>

              <div class="profile-players">
                @for (player of profile.players; track player.player_id) {
                  <div class="profile-player">
                    <strong>{{ player.player_name }}</strong>
                    <span>
                      {{ player.position_group }} ·
                      {{ player.total_valid_minutes }} min
                    </span>
                  </div>
                }
              </div>
            </article>
          }
        </div>
      }
    </section>
  `
})
export class ClustersPage implements OnInit {
  private readonly clustersService = inject(ClustersService);
  private readonly cdr = inject(ChangeDetectorRef);

  tournament = 'Apertura';

  clusterPlayers: ClusterPlayer[] = [];
  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.loadData();
  }

  get profileCount(): number {
    return new Set(
      this.clusterPlayers.map((player) => player.cluster)
    ).size;
  }

  get profiles(): {
    cluster: number;
    name: string;
    description: string;
    players: ClusterPlayer[];
  }[] {
    const groups = new Map<
      number,
      {
        cluster: number;
        name: string;
        description: string;
        players: ClusterPlayer[];
      }
    >();

    for (const player of this.clusterPlayers) {
      if (!groups.has(player.cluster)) {
        groups.set(player.cluster, {
          cluster: player.cluster,
          name: player.profile_name,
          description: player.profile_description,
          players: []
        });
      }

      groups.get(player.cluster)!.players.push(player);
    }

    return Array.from(groups.values()).sort(
      (a, b) => a.cluster - b.cluster
    );
  }

  selectTournament(
    tournament: 'Apertura' | 'Clausura'
  ): void {
    if (this.tournament === tournament) {
      return;
    }

    this.tournament = tournament;
    this.loadData();
  }

  private loadData(): void {
    this.loading = true;
    this.error = null;

    this.clustersService.getClusters(this.tournament).subscribe({
      next: (response) => {
        this.clusterPlayers = response.data;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: () => {
        this.error = 'No fue posible cargar los perfiles de jugadores.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }
}