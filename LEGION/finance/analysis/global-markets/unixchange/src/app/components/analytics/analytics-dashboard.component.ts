import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DataCaptureService } from '../../services/data-capture.service';

interface AnalyticsData {
  captureStats: {
    totalPackets: number;
    dataVolume: string;
    activeConnections: number;
    captureRate: number;
  };
  networkMetrics: {
    latency: number;
    throughput: number;
    errorRate: number;
    uptime: number;
  };
  tradingMetrics: {
    totalTrades: number;
    volumeUSD: number;
    avgTradeSize: number;
    topPairs: Array<{pair: string, volume: number}>;
  };
}

@Component({
  selector: 'app-analytics-dashboard',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="analytics-dashboard">
      <div class="dashboard-header">
        <h2>Analytics Dashboard</h2>
        <div class="time-controls">
          <button class="btn" [class.active]="selectedTimeframe === '1h'" (click)="setTimeframe('1h')">1H</button>
          <button class="btn" [class.active]="selectedTimeframe === '24h'" (click)="setTimeframe('24h')">24H</button>
          <button class="btn" [class.active]="selectedTimeframe === '7d'" (click)="setTimeframe('7d')">7D</button>
          <button class="btn" [class.active]="selectedTimeframe === '30d'" (click)="setTimeframe('30d')">30D</button>
        </div>
      </div>

      <div class="analytics-grid">
        <!-- Data Capture Section -->
        <div class="analytics-section">
          <h3>Data Capture Statistics</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-icon">📊</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.captureStats.totalPackets | number }}</div>
                <div class="metric-label">Total Packets</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">💾</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.captureStats.dataVolume }}</div>
                <div class="metric-label">Data Volume</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">🔗</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.captureStats.activeConnections }}</div>
                <div class="metric-label">Active Connections</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">⚡</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.captureStats.captureRate.toFixed(1) }}%</div>
                <div class="metric-label">Capture Rate</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Network Metrics Section -->
        <div class="analytics-section">
          <h3>Network Performance</h3>
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-icon">⏱️</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.networkMetrics.latency }}ms</div>
                <div class="metric-label">Avg Latency</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">🚀</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.networkMetrics.throughput }} Mbps</div>
                <div class="metric-label">Throughput</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">❌</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.networkMetrics.errorRate.toFixed(2) }}%</div>
                <div class="metric-label">Error Rate</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon">✅</div>
              <div class="metric-content">
                <div class="metric-value">{{ analytics.networkMetrics.uptime.toFixed(1) }}%</div>
                <div class="metric-label">Uptime</div>
              </div>
            </div>
          </div>
        </div>

        <!-- Trading Metrics Section -->
        <div class="analytics-section full-width">
          <h3>Trading Activity</h3>
          <div class="trading-overview">
            <div class="trading-stats">
              <div class="stat-item">
                <div class="stat-value">{{ analytics.tradingMetrics.totalTrades | number }}</div>
                <div class="stat-label">Total Trades</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">\${{ formatNumber(analytics.tradingMetrics.volumeUSD) }}</div>
                <div class="stat-label">Volume (USD)</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">\${{ analytics.tradingMetrics.avgTradeSize.toFixed(2) }}</div>
                <div class="stat-label">Avg Trade Size</div>
              </div>
            </div>
            
            <div class="top-pairs">
              <h4>Top Trading Pairs</h4>
              <div class="pair-list">
                <div class="pair-item" *ngFor="let pair of analytics.tradingMetrics.topPairs">
                  <span class="pair-name">{{ pair.pair }}</span>
                  <span class="pair-volume">\${{ formatNumber(pair.volume) }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Real-time Activity Feed -->
        <div class="analytics-section full-width">
          <h3>Real-time Activity</h3>
          <div class="activity-feed">
            <div class="activity-item" *ngFor="let activity of activityFeed">
              <div class="activity-timestamp">{{ activity.timestamp | date:'short' }}</div>
              <div class="activity-message">{{ activity.message }}</div>
              <div class="activity-status" [ngClass]="activity.type">{{ activity.type }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .analytics-dashboard {
      padding: 1.5rem;
      background: var(--background-color);
      min-height: 100vh;
    }

    .dashboard-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
    }

    .dashboard-header h2 {
      color: var(--text-primary);
      font-size: 1.8rem;
      font-weight: 600;
      margin: 0;
    }

    .time-controls {
      display: flex;
      gap: 0.5rem;
    }

    .time-controls .btn {
      background: rgba(255, 255, 255, 0.1);
      color: var(--text-secondary);
      border: 1px solid var(--border-color);
      padding: 0.5rem 1rem;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }

    .time-controls .btn.active,
    .time-controls .btn:hover {
      background: var(--primary-color);
      color: white;
      border-color: var(--primary-color);
    }

    .analytics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
      gap: 2rem;
    }

    .analytics-section {
      background: var(--surface-color);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
    }

    .analytics-section.full-width {
      grid-column: 1 / -1;
    }

    .analytics-section h3 {
      color: var(--text-primary);
      font-size: 1.2rem;
      font-weight: 600;
      margin: 0 0 1.5rem 0;
    }

    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 1rem;
    }

    .metric-card {
      background: rgba(255, 255, 255, 0.02);
      border: 1px solid var(--border-color);
      border-radius: 6px;
      padding: 1rem;
      display: flex;
      align-items: center;
      gap: 1rem;
    }

    .metric-icon {
      font-size: 2rem;
    }

    .metric-content {
      flex: 1;
    }

    .metric-value {
      color: var(--text-primary);
      font-size: 1.5rem;
      font-weight: 600;
      line-height: 1;
    }

    .metric-label {
      color: var(--text-secondary);
      font-size: 0.875rem;
      margin-top: 0.25rem;
    }

    .trading-overview {
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 2rem;
    }

    .trading-stats {
      display: flex;
      gap: 2rem;
    }

    .stat-item {
      text-align: center;
    }

    .stat-value {
      color: var(--text-primary);
      font-size: 1.8rem;
      font-weight: 600;
      line-height: 1;
    }

    .stat-label {
      color: var(--text-secondary);
      font-size: 0.875rem;
      margin-top: 0.5rem;
    }

    .top-pairs h4 {
      color: var(--text-primary);
      font-size: 1rem;
      margin: 0 0 1rem 0;
    }

    .pair-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .pair-item {
      display: flex;
      justify-content: space-between;
      padding: 0.75rem;
      background: rgba(255, 255, 255, 0.02);
      border-radius: 4px;
      border: 1px solid var(--border-color);
    }

    .pair-name {
      color: var(--text-primary);
      font-weight: 600;
    }

    .pair-volume {
      color: var(--text-secondary);
    }

    .activity-feed {
      max-height: 300px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }

    .activity-item {
      display: grid;
      grid-template-columns: auto 1fr auto;
      gap: 1rem;
      padding: 1rem;
      background: rgba(255, 255, 255, 0.02);
      border-radius: 4px;
      border: 1px solid var(--border-color);
    }

    .activity-timestamp {
      color: var(--text-secondary);
      font-size: 0.875rem;
      white-space: nowrap;
    }

    .activity-message {
      color: var(--text-primary);
    }

    .activity-status {
      padding: 0.25rem 0.75rem;
      border-radius: 12px;
      font-size: 0.75rem;
      text-transform: uppercase;
      font-weight: 600;
    }

    .activity-status.success {
      background: rgba(76, 175, 80, 0.2);
      color: #4CAF50;
    }

    .activity-status.warning {
      background: rgba(255, 193, 7, 0.2);
      color: #FFC107;
    }

    .activity-status.error {
      background: rgba(244, 67, 54, 0.2);
      color: #F44336;
    }

    .activity-status.info {
      background: rgba(33, 150, 243, 0.2);
      color: #2196F3;
    }

    @media (max-width: 768px) {
      .analytics-grid {
        grid-template-columns: 1fr;
      }
      
      .trading-overview {
        grid-template-columns: 1fr;
      }
      
      .trading-stats {
        justify-content: space-around;
      }
    }
  `]
})
export class AnalyticsDashboardComponent implements OnInit {
  selectedTimeframe: string = '24h';
  
  analytics: AnalyticsData = {
    captureStats: {
      totalPackets: 2547893,
      dataVolume: '156.7 GB',
      activeConnections: 342,
      captureRate: 98.7
    },
    networkMetrics: {
      latency: 23,
      throughput: 847.2,
      errorRate: 0.15,
      uptime: 99.8
    },
    tradingMetrics: {
      totalTrades: 18745,
      volumeUSD: 47856234.78,
      avgTradeSize: 2553.45,
      topPairs: [
        { pair: 'BTC/USDT', volume: 12456789.34 },
        { pair: 'ETH/USDT', volume: 8934567.12 },
        { pair: 'BNB/USDT', volume: 5678234.56 },
        { pair: 'ADA/USDT', volume: 3456789.23 },
        { pair: 'SOL/USDT', volume: 2345678.90 }
      ]
    }
  };

  activityFeed = [
    { timestamp: new Date(), message: 'Data capture rate increased to 98.7%', type: 'success' },
    { timestamp: new Date(Date.now() - 120000), message: 'New trading pair detected: ATOM/USDT', type: 'info' },
    { timestamp: new Date(Date.now() - 240000), message: 'Network latency spike detected', type: 'warning' },
    { timestamp: new Date(Date.now() - 360000), message: 'Connection timeout on exchange API', type: 'error' },
    { timestamp: new Date(Date.now() - 480000), message: 'Data volume threshold reached', type: 'info' },
    { timestamp: new Date(Date.now() - 600000), message: 'Backup capture system activated', type: 'success' }
  ];

  constructor(private dataCaptureService: DataCaptureService) {}

  ngOnInit() {
    this.startRealTimeUpdates();
  }

  setTimeframe(timeframe: string) {
    this.selectedTimeframe = timeframe;
    this.updateAnalytics();
  }

  startRealTimeUpdates() {
    setInterval(() => {
      this.updateRealTimeData();
    }, 5000); // Update every 5 seconds
  }

  updateRealTimeData() {
    // Simulate real-time data updates
    this.analytics.captureStats.totalPackets += Math.floor(Math.random() * 1000);
    this.analytics.captureStats.activeConnections += Math.floor((Math.random() - 0.5) * 10);
    this.analytics.captureStats.captureRate = 95 + Math.random() * 5;
    
    this.analytics.networkMetrics.latency = 15 + Math.random() * 20;
    this.analytics.networkMetrics.throughput = 800 + Math.random() * 100;
    this.analytics.networkMetrics.errorRate = Math.random() * 0.5;
    
    this.analytics.tradingMetrics.totalTrades += Math.floor(Math.random() * 50);
    this.analytics.tradingMetrics.volumeUSD += Math.random() * 100000;
  }

  updateAnalytics() {
    // In a real implementation, this would fetch data based on the selected timeframe
    console.log(`Updating analytics for timeframe: ${this.selectedTimeframe}`);
  }

  formatNumber(num: number): string {
    if (num >= 1e9) {
      return (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
      return (num / 1e6).toFixed(2) + 'M';
    } else if (num >= 1e3) {
      return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
  }
}
