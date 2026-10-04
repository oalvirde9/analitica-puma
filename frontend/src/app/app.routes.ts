import { Routes } from '@angular/router';

import { DashboardPage } from './pages/dashboard/dashboard';
import { JugadoresPage } from './pages/jugadores/jugadores';
import { PartidosPage } from './pages/partidos/partidos';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'dashboard'
  },
  {
    path: 'dashboard',
    component: DashboardPage,
    title: 'Dashboard · Analítica Puma'
  },
  {
    path: 'partidos',
    component: PartidosPage,
    title: 'Partidos · Analítica Puma'
  },
  {
    path: 'jugadores',
    component: JugadoresPage,
    title: 'Jugadores · Analítica Puma'
  },
  {
    path: '**',
    redirectTo: 'dashboard'
  }
];
