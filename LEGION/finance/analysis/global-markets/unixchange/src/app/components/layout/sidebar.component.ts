import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { MarketDataService } from '../../services/market-data.service';

@Component({
  selector: 'app-sidebar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <aside class="sidebar">
      <div class="sidebar-section">
        <h3 class="section-title">Market Watch</h3>
        <div class="watchlist">
          <div class="watchlist-item" 
               *ngFor="let item of marketData" 
               [class.selected]="item.symbol === selectedSymbol"
               (click)="selectSymbol(item.symbol)">
            <div class="item-header">
              <span class="symbol">{{ item.symbol }}</span>
              <span class="change-percent" 
                    [class.positive]="item.changePercent > 0" 
                    [class.negative]="item.changePercent < 0">
                {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent | number:'1.2-2' }}%
              </span>
            </div>
            <div class="item-details">
              <span class="price">{{ item.price | currency:'USD':'symbol':'1.2-2' }}</span>
              <span class="volume">Vol: {{ formatVolume(item.volume) }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="sidebar-section">
        <h3 class="section-title">Quick Actions</h3>
        <div class="quick-actions">
          <button class="action-button primary" (click)="addToWatchlist()">
            <span class="button-icon">+</span>
            Add Symbol
          </button>
          <button class="action-button secondary" (click)="exportData()">
            <span class="button-icon">↓</span>
            Export Data
          </button>
          <button class="action-button secondary" (click)="toggleDataCapture()">
            <span class="button-icon">{{ isCapturing ? '⏸' : '▶' }}</span>
            {{ isCapturing ? 'Stop' : 'Start' }} Capture
          </button>
        </div>
      </div>

      <div class="sidebar-section">
        <h3 class="section-title">Network Status</h3>
        <div class="network-status">
          <div class="status-item">
            <span class="status-label">Connection</span>
            <span class="status-value" [class.connected]="isConnected">
              {{ isConnected ? 'Active' : 'Disconnected' }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">Latency</span>
            <span class="status-value">{{ latency }}ms</span>
          </div>
          <div class="status-item">
            <span class="status-label">Updates/sec</span>
            <span class="status-value">{{ updatesPerSecond }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">Data Source</span>
            <span class="status-value">{{ dataSource }}</span>
          </div>
        </div>
      </div>

      <div class="sidebar-section">
        <h3 class="section-title">Capture Statistics</h3>
        <div class="capture-stats">
          <div class="stat-item">
            <span class="stat-value">{{ packetCount }}</span>
            <span class="stat-label">Packets Captured</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ formatBytes(dataTransferred) }}</span>
            <span class="stat-label">Data Transferred</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ activeConnections }}</span>
            <span class="stat-label">Active Connections</span>
          </div>
        </div>
      </div>
    </aside>
  `,
  styles: [`
    .sidebar {
      width: 280px;
      background: var(--secondary-bg);
      border-right: 1px solid var(--border-color);
      height: 100%;
      overflow-y: auto;
      padding: 1rem;
      display: flex;
      flex-direction: column;
      gap: 1.5rem;
    }

    .sidebar-section {
      background: var(--tertiary-bg);
      border-radius: 0.5rem;
      padding: 1rem;
      border: 1px solid var(--border-color);
    }

    .section-title {
      font-size: 0.9rem;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0 0 1rem 0;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .watchlist {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .watchlist-item {
      padding: 0.75rem;
      background: var(--accent-bg);
      border-radius: 0.25rem;
      cursor: pointer;
      transition: all 0.2s ease;
      border: 1px solid transparent;
    }

    .watchlist-item:hover {
      background: var(--primary-bg);
      border-color: var(--accent-blue);
    }

    .watchlist-item.selected {
      background: rgba(41, 98, 255, 0.1);
      border-color: var(--accent-blue);
    }

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.25rem;
    }

    .symbol {
      font-weight: 600;
      color: var(--text-primary);
      font-size: 0.9rem;
    }

    .change-percent {
      font-size: 0.8rem;
      font-weight: 500;
    }

    .change-percent.positive {
      color: var(--accent-green);
    }

    .change-percent.negative {
      color: var(--accent-red);
    }

    .item-details {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .price {
      font-size: 0.85rem;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .volume {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .quick-actions {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .action-button {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 0.75rem;
      border-radius: 0.25rem;
      border: none;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .action-button.primary {
      background: var(--accent-blue);
      color: white;
    }

    .action-button.primary:hover {
      background: #1e4ee6;
    }

    .action-button.secondary {
      background: var(--accent-bg);
      color: var(--text-secondary);
      border: 1px solid var(--border-color);
    }

    .action-button.secondary:hover {
      background: var(--primary-bg);
      color: var(--text-primary);
    }

    .button-icon {
      font-size: 1rem;
      line-height: 1;
    }

    .network-status {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .status-label {
      font-size: 0.8rem;
      color: var(--text-muted);
    }

    .status-value {
      font-size: 0.8rem;
      color: var(--text-secondary);
      font-weight: 500;
    }

    .status-value.connected {
      color: var(--accent-green);
    }

    .capture-stats {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1rem;
    }

    .stat-item {
      text-align: center;
      padding: 0.75rem;
      background: var(--accent-bg);
      border-radius: 0.25rem;
    }

    .stat-value {
      display: block;
      font-size: 1.1rem;
      font-weight: 600;
      color: var(--text-primary);
      margin-bottom: 0.25rem;
    }

    .stat-label {
      font-size: 0.7rem;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    @media (max-width: 1024px) {
      .sidebar {
        width: 240px;
      }
    }

    @media (max-width: 768px) {
      .sidebar {
        position: fixed;
        left: -280px;
        top: 60px;
        z-index: 50;
        transition: left 0.3s ease;
      }

      .sidebar.open {
        left: 0;
      }
    }
  `]
})
export class SidebarComponent implements OnInit, OnDestroy {
  marketData: any[] = [];
  selectedSymbol = 'BTCUSDT';
  isConnected = false;
  isCapturing = false;
  latency = 12;
  updatesPerSecond = 45;
  dataSource = 'Programmatic';
  packetCount = 15420;
  dataTransferred = 2456789;
  activeConnections = 3;

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

    // Simulate real-time updates
    setInterval(() => {
      this.latency = 8 + Math.floor(Math.random() * 20);
      this.updatesPerSecond = 40 + Math.floor(Math.random() * 20);
      this.packetCount += Math.floor(Math.random() * 10);
      this.dataTransferred += Math.floor(Math.random() * 1000);
    }, 2000);
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  selectSymbol(symbol: string): void {
    this.selectedSymbol = symbol;
    this.marketDataService.setSelectedSymbol(symbol);
  }

  addToWatchlist(): void {
    // Implement add to watchlist functionality
    console.log('Add to watchlist');
  }

  exportData(): void {
    // Implement data export functionality
    const dataStr = JSON.stringify(this.marketData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `market-data-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }

  toggleDataCapture(): void {
    this.isCapturing = !this.isCapturing;
    // Implement data capture toggle
    console.log(`Data capture ${this.isCapturing ? 'started' : 'stopped'}`);
  }

  formatVolume(volume: number): string {
    if (volume >= 1e9) {
      return (volume / 1e9).toFixed(1) + 'B';
    } else if (volume >= 1e6) {
      return (volume / 1e6).toFixed(1) + 'M';
    } else if (volume >= 1e3) {
      return (volume / 1e3).toFixed(1) + 'K';
    }
    return volume.toFixed(0);
  }

  formatBytes(bytes: number): string {
    if (bytes >= 1e9) {
      return (bytes / 1e9).toFixed(1) + 'GB';
    } else if (bytes >= 1e6) {
      return (bytes / 1e6).toFixed(1) + 'MB';
    } else if (bytes >= 1e3) {
      return (bytes / 1e3).toFixed(1) + 'KB';
    }
    return bytes + 'B';
  }
}
