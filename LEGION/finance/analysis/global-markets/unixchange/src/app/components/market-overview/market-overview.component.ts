import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MarketDataService } from '../../services/market-data.service';

interface MarketOverview {
  totalMarketCap: number;
  volume24h: number;
  activeExchanges: number;
  gainers: Array<{symbol: string, price: number, change: number}>;
  losers: Array<{symbol: string, price: number, change: number}>;
}

@Component({
  selector: 'app-market-overview',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="market-overview">
      <div class="overview-header">
        <h2>Market Overview</h2>
        <div class="refresh-controls">
          <button class="btn btn-secondary" (click)="refreshData()">
            <i class="icon-refresh"></i> Refresh
          </button>
        </div>
      </div>

      <div class="overview-stats">
        <div class="stat-card">
          <div class="stat-label">Total Market Cap</div>
          <div class="stat-value">\${{ formatNumber(overview.totalMarketCap) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">24h Volume</div>
          <div class="stat-value">\${{ formatNumber(overview.volume24h) }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Active Exchanges</div>
          <div class="stat-value">{{ overview.activeExchanges }}</div>
        </div>
      </div>

      <div class="movers-section">
        <div class="gainers">
          <h3>Top Gainers</h3>
          <div class="mover-list">
            <div class="mover-item" *ngFor="let gainer of overview.gainers">
              <span class="symbol">{{ gainer.symbol }}</span>
              <span class="price">\${{ gainer.price.toFixed(2) }}</span>
              <span class="change positive">+{{ gainer.change.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
        
        <div class="losers">
          <h3>Top Losers</h3>
          <div class="mover-list">
            <div class="mover-item" *ngFor="let loser of overview.losers">
              <span class="symbol">{{ loser.symbol }}</span>
              <span class="price">\${{ loser.price.toFixed(2) }}</span>
              <span class="change negative">{{ loser.change.toFixed(2) }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .market-overview {
      padding: 1.5rem;
      background: var(--surface-color);
      border-radius: 8px;
      border: 1px solid var(--border-color);
    }

    .overview-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.5rem;
    }

    .overview-header h2 {
      color: var(--text-primary);
      font-size: 1.5rem;
      font-weight: 600;
      margin: 0;
    }

    .overview-stats {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .stat-card {
      background: rgba(255, 255, 255, 0.02);
      padding: 1rem;
      border-radius: 6px;
      border: 1px solid var(--border-color);
    }

    .stat-label {
      color: var(--text-secondary);
      font-size: 0.875rem;
      margin-bottom: 0.5rem;
    }

    .stat-value {
      color: var(--text-primary);
      font-size: 1.5rem;
      font-weight: 600;
    }

    .movers-section {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 2rem;
    }

    .gainers h3, .losers h3 {
      color: var(--text-primary);
      font-size: 1.1rem;
      margin-bottom: 1rem;
    }

    .mover-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .mover-item {
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 1rem;
      padding: 0.75rem;
      background: rgba(255, 255, 255, 0.02);
      border-radius: 4px;
      border: 1px solid var(--border-color);
    }

    .symbol {
      color: var(--text-primary);
      font-weight: 600;
    }

    .price {
      color: var(--text-secondary);
    }

    .change.positive {
      color: var(--success-color);
    }

    .change.negative {
      color: var(--error-color);
    }

    .btn {
      background: var(--primary-color);
      color: white;
      border: none;
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      font-size: 0.875rem;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }

    .btn:hover {
      background: var(--primary-hover);
    }

    .btn-secondary {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-primary);
    }

    .btn-secondary:hover {
      background: rgba(255, 255, 255, 0.15);
    }

    @media (max-width: 768px) {
      .movers-section {
        grid-template-columns: 1fr;
      }
      
      .overview-stats {
        grid-template-columns: 1fr;
      }
    }
  `]
})
export class MarketOverviewComponent implements OnInit {
  overview: MarketOverview = {
    totalMarketCap: 2.3e12,
    volume24h: 86.7e9,
    activeExchanges: 487,
    gainers: [
      { symbol: 'ETH', price: 3456.78, change: 8.23 },
      { symbol: 'BTC', price: 67891.23, change: 5.67 },
      { symbol: 'ADA', price: 0.89, change: 12.45 },
      { symbol: 'SOL', price: 234.56, change: 9.87 },
      { symbol: 'DOT', price: 45.67, change: 7.23 }
    ],
    losers: [
      { symbol: 'LUNA', price: 0.0001, change: -23.45 },
      { symbol: 'AVAX', price: 78.90, change: -8.76 },
      { symbol: 'MATIC', price: 1.23, change: -5.43 },
      { symbol: 'ATOM', price: 12.34, change: -6.78 },
      { symbol: 'NEAR', price: 5.67, change: -4.32 }
    ]
  };

  constructor(private marketData: MarketDataService) {}

  ngOnInit() {
    this.loadMarketOverview();
  }

  loadMarketOverview() {
    // In a real implementation, this would fetch from the market data service
    // For now, we'll use simulated data with periodic updates
    setInterval(() => {
      this.updateMarketData();
    }, 30000); // Update every 30 seconds
  }

  updateMarketData() {
    // Simulate market data changes
    this.overview.totalMarketCap *= (1 + (Math.random() - 0.5) * 0.02);
    this.overview.volume24h *= (1 + (Math.random() - 0.5) * 0.05);
    
    // Update gainers and losers with random fluctuations
    this.overview.gainers.forEach(item => {
      const change = (Math.random() - 0.5) * 0.1;
      item.price *= (1 + change);
      item.change += change * 100;
    });
    
    this.overview.losers.forEach(item => {
      const change = (Math.random() - 0.5) * 0.1;
      item.price *= (1 + change);
      item.change += change * 100;
    });
  }

  refreshData() {
    this.updateMarketData();
  }

  formatNumber(num: number): string {
    if (num >= 1e12) {
      return (num / 1e12).toFixed(2) + 'T';
    } else if (num >= 1e9) {
      return (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
      return (num / 1e6).toFixed(2) + 'M';
    } else if (num >= 1e3) {
      return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
  }
}
