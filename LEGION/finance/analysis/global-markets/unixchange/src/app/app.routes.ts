import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/trading',
    pathMatch: 'full'
  },
  {
    path: 'trading',
    loadComponent: () => import('./components/trading-workspace/trading-workspace.component').then(m => m.TradingWorkspaceComponent)
  },  {
    path: 'markets',
    loadComponent: () => import('./components/market-overview/market-overview.component').then(m => m.MarketOverviewComponent)
  },
  {
    path: 'analytics',
    loadComponent: () => import('./components/analytics/analytics-dashboard.component').then(m => m.AnalyticsDashboardComponent)
  },  {
    path: '**',
    redirectTo: '/trading'
  }
];
