import {
  ChangeDetectorRef,
  Component,
  OnInit,
  inject
} from '@angular/core';

import {
  Fixture,
  MatchesService,
  Standing
} from '../../services/matches.service';

@Component({
  selector: 'app-partidos-page',
  standalone: true,
  templateUrl: './partidos.html'
})
export class PartidosPage implements OnInit {
  private readonly matchesService = inject(MatchesService);
  private readonly cdr = inject(ChangeDetectorRef);

  tournamentFixtures: Fixture[] = [];
  tournamentStandings: Standing[] = [];

  ngOnInit(): void {
    this.loadTournament();
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
}
