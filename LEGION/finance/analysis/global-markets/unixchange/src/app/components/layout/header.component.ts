import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { Subject, takeUntil } from 'rxjs';
import { MarketDataService } from '../../services/market-data.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <header class="header">
      <div class="header-left">
        <div class="logo">
          <h1 class="logo-text">UniXchange</h1>
          <span class="logo-badge">PRO</span>
        </div>
        
        <nav class="main-nav">
          <a routerLink="/trading" routerLinkActive="active" class="nav-item">Trading</a>
          <a routerLink="/markets" routerLinkActive="active" class="nav-item">Markets</a>
          <a routerLink="/analytics" routerLinkActive="active" class="nav-item">Analytics</a>
          <a routerLink="/data-capture" routerLinkActive="active" class="nav-item">Data Capture</a>
        </nav>
      </div>

      <div class="header-center">
        <div class="market-ticker" *ngIf="marketData.length > 0">
          <div class="ticker-item" *ngFor="let item of marketData.slice(0, 5)">
            <span class="symbol">{{ item.symbol }}</span>
            <span class="price" [class.price-up]="item.change > 0" [class.price-down]="item.change < 0">
              {{ item.price | currency:'USD':'symbol':'1.2-2' }}
            </span>
            <span class="change" [class.price-up]="item.change > 0" [class.price-down]="item.change < 0">
              {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent | number:'1.2-2' }}%
            </span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <div class="connection-status">
          <div class="status-indicator" [class.connected]="isConnected" [class.disconnected]="!isConnected"></div>
          <span class="status-text">{{ isConnected ? 'Live' : 'Disconnected' }}</span>
        </div>
        
        <div class="user-menu">
          <button class="user-button">
            <div class="user-avatar"></div>
            <span class="user-name">Trader</span>
          </button>
        </div>
      </div>
    </header>
  `,
  styles: [`
    .header {
      height: 60px;
      background: var(--secondary-bg);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1.5rem;
      position: relative;
      z-index: 100;
    }

    .header-left {
      display: flex;
      align-items: center;
      gap: 2rem;
    }

    .logo {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .logo-text {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--accent-blue);
      margin: 0;
      letter-spacing: -0.02em;
    }

    .logo-badge {
      background: var(--accent-blue);
      color: white;
      font-size: 0.7rem;
      font-weight: 600;
      padding: 0.1rem 0.4rem;
      border-radius: 0.2rem;
      text-transform: uppercase;
    }

    .main-nav {
      display: flex;
      gap: 1.5rem;
    }

    .nav-item {
      color: var(--text-secondary);
      text-decoration: none;
      font-weight: 500;
      padding: 0.5rem 1rem;
      border-radius: 0.25rem;
      transition: all 0.2s ease;
    }

    .nav-item:hover {
      color: var(--text-primary);
      background: var(--accent-bg);
    }

    .nav-item.active {
      color: var(--accent-blue);
      background: rgba(41, 98, 255, 0.1);
    }

    .header-center {
      flex: 1;
      display: flex;
      justify-content: center;
      max-width: 600px;
    }

    .market-ticker {
      display: flex;
      gap: 1.5rem;
      overflow: hidden;
    }

    .ticker-item {
      display: flex;
      flex-direction: column;
      align-items: center;
      min-width: 80px;
    }

    .symbol {
      font-size: 0.7rem;
      color: var(--text-muted);
      font-weight: 600;
      text-transform: uppercase;
    }

    .price {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .change {
      font-size: 0.7rem;
      font-weight: 500;
    }

    .price-up {
      color: var(--accent-green) !important;
    }

    .price-down {
      color: var(--accent-red) !important;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .connection-status {
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      transition: all 0.3s ease;
    }

    .status-indicator.connected {
      background: var(--accent-green);
      box-shadow: 0 0 8px rgba(0, 200, 83, 0.5);
    }

    .status-indicator.disconnected {
      background: var(--accent-red);
      box-shadow: 0 0 8px rgba(255, 23, 68, 0.5);
    }

    .status-text {
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .user-menu {
      position: relative;
    }

    .user-button {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      background: none;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 0.5rem;
      border-radius: 0.25rem;
      transition: all 0.2s ease;
    }

    .user-button:hover {
      background: var(--accent-bg);
      color: var(--text-primary);
    }

    .user-avatar {
      width: 24px;
      height: 24px;
      border-radius: 50%;
      background: linear-gradient(135deg, var(--accent-blue), var(--accent-green));
    }

    .user-name {
      font-size: 0.9rem;
      font-weight: 500;
    }

    @media (max-width: 1200px) {
      .market-ticker {
        gap: 1rem;
      }
      
      .ticker-item {
        min-width: 60px;
      }
    }

    @media (max-width: 768px) {
      .header-center {
        display: none;
      }
      
      .main-nav {
        gap: 1rem;
      }
      
      .nav-item {
        padding: 0.25rem 0.5rem;
        font-size: 0.9rem;
      }
    }
  `]
})
export class HeaderComponent implements OnInit, OnDestroy {
  marketData: any[] = [];
  isConnected = false;
  private destroy$ = new Subject<void>();

  constructor(private marketDataService: MarketDataService) {}

  ngOnInit(): void {
    this.marketDataService.marketData$
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => {
        this.marketData = data;
      });

    this.marketDataService.connectionStatus$
      .pipe(takeUntil(this.destroy$))
      .subscribe(status => {
        this.isConnected = status;
      });
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }
}
