import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs/operators';

import {
  Fixture,
  MatchesService,
  Standing
} from './services/matches.service';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html'
})
export class App implements OnInit {
  private readonly matchesService = inject(MatchesService);
  private readonly cdr = inject(ChangeDetectorRef);
  private readonly router = inject(Router);

  currentPage: 'dashboard' | 'partidos' | 'jugadores' = 'dashboard';

  latestMatch: Fixture | null = null;
  upcomingMatches: Fixture[] = [];
  pumasStanding: Standing | null = null;

  tournamentFixtures: Fixture[] = [];
  tournamentStandings: Standing[] = [];

  loading = true;
  error: string | null = null;

  ngOnInit(): void {
    this.updateCurrentPage(this.router.url);

    this.router.events
      .pipe(
        filter(
          (event): event is NavigationEnd =>
            event instanceof NavigationEnd
        )
      )
      .subscribe((event) => {
        this.updateCurrentPage(event.urlAfterRedirects);
        this.cdr.markForCheck();
      });

    this.loadMatches();
    this.loadPumasStanding();
    this.loadTournament();
  }

  navigateTo(
    page: 'dashboard' | 'partidos' | 'jugadores'
  ): void {
    void this.router.navigate([page]);
  }

  private updateCurrentPage(url: string): void {
    if (url.startsWith('/partidos')) {
      this.currentPage = 'partidos';
      return;
    }

    if (url.startsWith('/jugadores')) {
      this.currentPage = 'jugadores';
      return;
    }

    this.currentPage = 'dashboard';
  }


  formatMatchDate(value: string): string {
    const date = new Date(value.replace(' ', 'T') + 'Z');

    return new Intl.DateTimeFormat('es-MX', {
      timeZone: 'America/Mexico_City',
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    }).format(date);
  }

  formatMatchTime(value: string): string {
    const date = new Date(value.replace(' ', 'T') + 'Z');

    return new Intl.DateTimeFormat('es-MX', {
      timeZone: 'America/Mexico_City',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false
    }).format(date);
  }

  private loadTournament(): void {
    this.matchesService.getCurrentFixtures().subscribe({
      next: (response) => {
        this.tournamentFixtures = response.data;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error(
          'Error al cargar el calendario completo:',
          error
        );
        this.cdr.markForCheck();
      }
    });

    this.matchesService.getCurrentStandings().subscribe({
      next: (response) => {
        this.tournamentStandings = response.data;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error(
          'Error al cargar la clasificación completa:',
          error
        );
        this.cdr.markForCheck();
      }
    });
  }

  private loadPumasStanding(): void {
    this.matchesService.getPumasStanding().subscribe({
      next: (response) => {
        this.pumasStanding = response.data;

        console.log(
          'Clasificación Pumas:',
          this.pumasStanding
        );

        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error(
          'Error al cargar la clasificación de Pumas:',
          error
        );
        this.cdr.markForCheck();
      }
    });
  }

  private loadMatches(): void {
    this.matchesService.getLatest().subscribe({
      next: (match) => {
        this.latestMatch = match;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error al cargar el último partido:', error);
        this.error = 'No fue posible cargar los partidos.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });

    this.matchesService.getUpcoming().subscribe({
      next: (response) => {
        this.upcomingMatches = response.data;
        this.loading = false;
        this.cdr.markForCheck();
      },
      error: (error) => {
        console.error('Error al cargar los próximos partidos:', error);
        this.error = 'No fue posible cargar los partidos.';
        this.loading = false;
        this.cdr.markForCheck();
      }
    });
  }
}
