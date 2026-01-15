import { Component, OnInit, OnDestroy, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subject, takeUntil } from 'rxjs';
import { MarketDataService } from '../../services/market-data.service';

interface GridItem {
  id: string;
  x: number;
  y: number;
  w: number;
  h: number;
  component: string;
  title: string;
  resizable: boolean;
  draggable: boolean;
}

@Component({
  selector: 'app-trading-workspace',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="trading-workspace">
      <div class="workspace-toolbar">
        <div class="toolbar-left">
          <button class="toolbar-button" (click)="addWidget('chart')" title="Add Chart">
            <span class="button-icon">📊</span>
            Chart
          </button>
          <button class="toolbar-button" (click)="addWidget('orderbook')" title="Add Order Book">
            <span class="button-icon">📋</span>
            Order Book
          </button>
          <button class="toolbar-button" (click)="addWidget('trades')" title="Add Trade History">
            <span class="button-icon">📝</span>
            Trades
          </button>
          <button class="toolbar-button" (click)="addWidget('watchlist')" title="Add Watchlist">
            <span class="button-icon">👁</span>
            Watchlist
          </button>
        </div>
        
        <div class="toolbar-center">
          <div class="symbol-selector">
            <select class="symbol-select" [(ngModel)]="selectedSymbol" (change)="onSymbolChange()">
              <option *ngFor="let symbol of availableSymbols" [value]="symbol">{{ symbol }}</option>
            </select>
          </div>
        </div>
        
        <div class="toolbar-right">
          <button class="toolbar-button" (click)="resetLayout()" title="Reset Layout">
            <span class="button-icon">🔄</span>
            Reset
          </button>
          <button class="toolbar-button" (click)="saveLayout()" title="Save Layout">
            <span class="button-icon">💾</span>
            Save
          </button>
          <button class="toolbar-button" [class.active]="isFullscreen" (click)="toggleFullscreen()" title="Fullscreen">
            <span class="button-icon">{{ isFullscreen ? '🗗' : '🗖' }}</span>
            {{ isFullscreen ? 'Exit' : 'Full' }}
          </button>
        </div>
      </div>

      <div class="workspace-grid" #workspaceGrid>
        <div class="grid-container">
          <div 
            *ngFor="let item of gridItems; trackBy: trackByItemId"
            class="grid-item"
            [style.left.px]="item.x"
            [style.top.px]="item.y"
            [style.width.px]="item.w"
            [style.height.px]="item.h"
            [attr.data-id]="item.id"
            (mousedown)="onItemMouseDown($event, item)">
            
            <div class="grid-item-header">
              <span class="item-title">{{ item.title }}</span>
              <div class="item-controls">
                <button class="control-button" (click)="minimizeItem(item)" title="Minimize">−</button>
                <button class="control-button" (click)="maximizeItem(item)" title="Maximize">□</button>
                <button class="control-button danger" (click)="removeItem(item)" title="Close">×</button>
              </div>
            </div>
            
            <div class="grid-item-content">
              <div [ngSwitch]="item.component">
                <div *ngSwitchCase="'chart'" class="component-chart">
                  <div class="chart-placeholder">
                    <div class="chart-header">
                      <h4>{{ selectedSymbol }} - Live Chart</h4>
                      <div class="chart-controls">
                        <button class="chart-button" [class.active]="chartType === 'candlestick'" (click)="setChartType('candlestick')">Candles</button>
                        <button class="chart-button" [class.active]="chartType === 'line'" (click)="setChartType('line')">Line</button>
                        <button class="chart-button" [class.active]="chartType === 'area'" (click)="setChartType('area')">Area</button>
                      </div>
                    </div>
                    <div class="chart-canvas">
                      <canvas #chartCanvas width="100%" height="100%"></canvas>
                      <div class="chart-overlay">
                        <div class="price-line" *ngIf="currentPrice">
                          <span class="price-value">{{ currentPrice | currency:'USD':'symbol':'1.2-2' }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div *ngSwitchCase="'orderbook'" class="component-orderbook">
                  <div class="orderbook-header">
                    <h4>Order Book - {{ selectedSymbol }}</h4>
                    <div class="orderbook-controls">
                      <button class="depth-button" [class.active]="orderBookDepth === 10" (click)="setOrderBookDepth(10)">10</button>
                      <button class="depth-button" [class.active]="orderBookDepth === 25" (click)="setOrderBookDepth(25)">25</button>
                      <button class="depth-button" [class.active]="orderBookDepth === 50" (click)="setOrderBookDepth(50)">50</button>
                    </div>
                  </div>
                  <div class="orderbook-content">
                    <div class="orderbook-side asks">
                      <div class="side-header">
                        <span>Price (USD)</span>
                        <span>Size</span>
                        <span>Total</span>
                      </div>
                      <div class="orders-list">
                        <div class="order-row ask" *ngFor="let ask of mockAsks">
                          <span class="price">{{ ask[0] | number:'1.2-2' }}</span>
                          <span class="size">{{ ask[1] | number:'1.4-4' }}</span>
                          <span class="total">{{ ask[0] * ask[1] | number:'1.2-2' }}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="spread-indicator">
                      <span class="spread-value">Spread: {{ getSpread() | number:'1.2-2' }}</span>
                    </div>
                    
                    <div class="orderbook-side bids">
                      <div class="orders-list">
                        <div class="order-row bid" *ngFor="let bid of mockBids">
                          <span class="price">{{ bid[0] | number:'1.2-2' }}</span>
                          <span class="size">{{ bid[1] | number:'1.4-4' }}</span>
                          <span class="total">{{ bid[0] * bid[1] | number:'1.2-2' }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div *ngSwitchCase="'trades'" class="component-trades">
                  <div class="trades-header">
                    <h4>Recent Trades - {{ selectedSymbol }}</h4>
                    <div class="trades-controls">
                      <button class="filter-button" [class.active]="tradeFilter === 'all'" (click)="setTradeFilter('all')">All</button>
                      <button class="filter-button" [class.active]="tradeFilter === 'buy'" (click)="setTradeFilter('buy')">Buys</button>
                      <button class="filter-button" [class.active]="tradeFilter === 'sell'" (click)="setTradeFilter('sell')">Sells</button>
                    </div>
                  </div>
                  <div class="trades-content">
                    <div class="trades-header-row">
                      <span>Time</span>
                      <span>Price</span>
                      <span>Size</span>
                      <span>Side</span>
                    </div>
                    <div class="trades-list">
                      <div class="trade-row" *ngFor="let trade of mockTrades" [class.buy]="trade.side === 'buy'" [class.sell]="trade.side === 'sell'">
                        <span class="time">{{ formatTime(trade.timestamp) }}</span>
                        <span class="price">{{ trade.price | number:'1.2-2' }}</span>
                        <span class="size">{{ trade.quantity | number:'1.4-4' }}</span>
                        <span class="side" [class.buy]="trade.side === 'buy'" [class.sell]="trade.side === 'sell'">{{ trade.side }}</span>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div *ngSwitchCase="'watchlist'" class="component-watchlist">
                  <div class="watchlist-header">
                    <h4>Market Watchlist</h4>
                    <button class="add-button" (click)="addToWatchlist()">+ Add</button>
                  </div>
                  <div class="watchlist-content">
                    <div class="watchlist-header-row">
                      <span>Symbol</span>
                      <span>Price</span>
                      <span>Change</span>
                      <span>Volume</span>
                    </div>
                    <div class="watchlist-list">
                      <div class="watchlist-row" *ngFor="let item of marketData" (click)="selectSymbol(item.symbol)">
                        <span class="symbol">{{ item.symbol }}</span>
                        <span class="price">{{ item.price | currency:'USD':'symbol':'1.2-2' }}</span>
                        <span class="change" [class.positive]="item.changePercent > 0" [class.negative]="item.changePercent < 0">
                          {{ item.changePercent > 0 ? '+' : '' }}{{ item.changePercent | number:'1.2-2' }}%
                        </span>
                        <span class="volume">{{ formatVolume(item.volume) }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="resize-handle" 
                 *ngIf="item.resizable"
                 (mousedown)="onResizeStart($event, item)">
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .trading-workspace {
      height: 100%;
      display: flex;
      flex-direction: column;
      background: var(--primary-bg);
      overflow: hidden;
    }

    .workspace-toolbar {
      height: 50px;
      background: var(--tertiary-bg);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 1rem;
      gap: 1rem;
      flex-shrink: 0;
    }

    .toolbar-left,
    .toolbar-right {
      display: flex;
      gap: 0.5rem;
    }

    .toolbar-center {
      flex: 1;
      display: flex;
      justify-content: center;
    }

    .toolbar-button {
      display: flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.5rem 0.75rem;
      background: var(--accent-bg);
      color: var(--text-secondary);
      border: 1px solid var(--border-color);
      border-radius: 0.25rem;
      cursor: pointer;
      font-size: 0.8rem;
      font-weight: 500;
      transition: all 0.2s ease;
    }

    .toolbar-button:hover {
      background: var(--secondary-bg);
      color: var(--text-primary);
    }

    .toolbar-button.active {
      background: var(--accent-blue);
      color: white;
      border-color: var(--accent-blue);
    }

    .button-icon {
      font-size: 0.9rem;
    }

    .symbol-selector {
      display: flex;
      align-items: center;
    }

    .symbol-select {
      background: var(--secondary-bg);
      color: var(--text-primary);
      border: 1px solid var(--border-color);
      border-radius: 0.25rem;
      padding: 0.5rem 1rem;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
    }

    .workspace-grid {
      flex: 1;
      position: relative;
      overflow: hidden;
    }

    .grid-container {
      position: relative;
      width: 100%;
      height: 100%;
      background-image: 
        linear-gradient(var(--chart-grid) 1px, transparent 1px),
        linear-gradient(90deg, var(--chart-grid) 1px, transparent 1px);
      background-size: 20px 20px;
    }

    .grid-item {
      position: absolute;
      background: var(--secondary-bg);
      border: 1px solid var(--border-color);
      border-radius: 0.25rem;
      cursor: move;
      user-select: none;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .grid-item:hover {
      border-color: var(--accent-blue);
    }

    .grid-item-header {
      height: 32px;
      background: var(--tertiary-bg);
      border-bottom: 1px solid var(--border-color);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 0.75rem;
      flex-shrink: 0;
    }

    .item-title {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .item-controls {
      display: flex;
      gap: 0.25rem;
    }

    .control-button {
      width: 20px;
      height: 20px;
      background: none;
      border: none;
      color: var(--text-muted);
      cursor: pointer;
      font-size: 0.8rem;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 0.15rem;
      transition: all 0.2s ease;
    }

    .control-button:hover {
      background: var(--accent-bg);
      color: var(--text-primary);
    }

    .control-button.danger:hover {
      background: var(--accent-red);
      color: white;
    }

    .grid-item-content {
      flex: 1;
      overflow: hidden;
      position: relative;
    }

    .resize-handle {
      position: absolute;
      bottom: 0;
      right: 0;
      width: 16px;
      height: 16px;
      cursor: se-resize;
      background: linear-gradient(-45deg, transparent 0%, transparent 30%, var(--border-color) 30%, var(--border-color) 40%, transparent 40%, transparent 60%, var(--border-color) 60%, var(--border-color) 70%, transparent 70%);
    }

    /* Component Styles */
    .component-chart,
    .component-orderbook,
    .component-trades,
    .component-watchlist {
      height: 100%;
      display: flex;
      flex-direction: column;
    }

    .chart-placeholder {
      height: 100%;
      display: flex;
      flex-direction: column;
      padding: 1rem;
    }

    .chart-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    .chart-header h4 {
      margin: 0;
      color: var(--text-primary);
      font-size: 1rem;
    }

    .chart-controls {
      display: flex;
      gap: 0.25rem;
    }

    .chart-button {
      padding: 0.25rem 0.5rem;
      background: var(--accent-bg);
      color: var(--text-secondary);
      border: 1px solid var(--border-color);
      border-radius: 0.2rem;
      cursor: pointer;
      font-size: 0.75rem;
      transition: all 0.2s ease;
    }

    .chart-button.active {
      background: var(--accent-blue);
      color: white;
    }

    .chart-canvas {
      flex: 1;
      position: relative;
      background: var(--primary-bg);
      border: 1px solid var(--border-color);
      border-radius: 0.25rem;
    }

    .orderbook-header,
    .trades-header,
    .watchlist-header {
      padding: 0.75rem;
      border-bottom: 1px solid var(--border-color);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .orderbook-content,
    .trades-content,
    .watchlist-content {
      flex: 1;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .orderbook-side {
      flex: 1;
    }

    .side-header,
    .trades-header-row,
    .watchlist-header-row {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      padding: 0.5rem 0.75rem;
      background: var(--tertiary-bg);
      border-bottom: 1px solid var(--border-color);
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-muted);
    }

    .orders-list,
    .trades-list,
    .watchlist-list {
      flex: 1;
      overflow-y: auto;
    }

    .order-row,
    .trade-row,
    .watchlist-row {
      display: grid;
      grid-template-columns: 1fr 1fr 1fr 1fr;
      padding: 0.25rem 0.75rem;
      font-size: 0.75rem;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      transition: background 0.1s ease;
    }

    .order-row:hover,
    .trade-row:hover,
    .watchlist-row:hover {
      background: var(--accent-bg);
    }

    .order-row.ask .price {
      color: var(--accent-red);
    }

    .order-row.bid .price {
      color: var(--accent-green);
    }

    .trade-row.buy,
    .side.buy {
      color: var(--accent-green);
    }

    .trade-row.sell,
    .side.sell {
      color: var(--accent-red);
    }

    .spread-indicator {
      padding: 0.5rem 0.75rem;
      text-align: center;
      font-size: 0.75rem;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border-color);
    }

    .positive {
      color: var(--accent-green);
    }

    .negative {
      color: var(--accent-red);
    }

    .add-button {
      padding: 0.25rem 0.5rem;
      background: var(--accent-blue);
      color: white;
      border: none;
      border-radius: 0.2rem;
      cursor: pointer;
      font-size: 0.75rem;
    }
  `]
})
export class TradingWorkspaceComponent implements OnInit, OnDestroy, AfterViewInit {
  gridItems: GridItem[] = [];
  selectedSymbol = 'BTCUSDT';
  availableSymbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'];
  isFullscreen = false;
  chartType = 'candlestick';
  orderBookDepth = 25;
  tradeFilter = 'all';
  currentPrice = 0;
  marketData: any[] = [];

  // Mock data
  mockBids: [number, number][] = [];
  mockAsks: [number, number][] = [];
  mockTrades: any[] = [];

  private destroy$ = new Subject<void>();
  private isDragging = false;
  private isResizing = false;
  private dragItem: GridItem | null = null;
  private dragOffset = { x: 0, y: 0 };

  constructor(private marketDataService: MarketDataService) {
    this.initializeDefaultLayout();
    this.generateMockData();
  }

  ngOnInit(): void {
    this.marketDataService.marketData$
      .pipe(takeUntil(this.destroy$))
      .subscribe(data => {
        this.marketData = data;
        if (data.length > 0) {
          const selectedData = data.find(item => item.symbol === this.selectedSymbol);
          if (selectedData) {
            this.currentPrice = selectedData.price;
          }
        }
      });
  }

  ngAfterViewInit(): void {
    this.setupEventListeners();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  private initializeDefaultLayout(): void {
    this.gridItems = [
      {
        id: 'chart-1',
        x: 10,
        y: 10,
        w: 600,
        h: 400,
        component: 'chart',
        title: 'Price Chart',
        resizable: true,
        draggable: true
      },
      {
        id: 'orderbook-1',
        x: 630,
        y: 10,
        w: 300,
        h: 400,
        component: 'orderbook',
        title: 'Order Book',
        resizable: true,
        draggable: true
      },
      {
        id: 'trades-1',
        x: 950,
        y: 10,
        w: 300,
        h: 400,
        component: 'trades',
        title: 'Trade History',
        resizable: true,
        draggable: true
      },
      {
        id: 'watchlist-1',
        x: 10,
        y: 430,
        w: 920,
        h: 200,
        component: 'watchlist',
        title: 'Market Watchlist',
        resizable: true,
        draggable: true
      }
    ];
  }

  private generateMockData(): void {
    const basePrice = 50000;
    
    // Generate mock order book
    for (let i = 0; i < 20; i++) {
      this.mockBids.push([basePrice - (i + 1) * 10, Math.random() * 5]);
      this.mockAsks.push([basePrice + (i + 1) * 10, Math.random() * 5]);
    }

    // Generate mock trades
    for (let i = 0; i < 50; i++) {
      this.mockTrades.push({
        price: basePrice + (Math.random() - 0.5) * 100,
        quantity: Math.random() * 5,
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        timestamp: Date.now() - i * 1000
      });
    }
  }

  private setupEventListeners(): void {
    document.addEventListener('mousemove', this.onMouseMove.bind(this));
    document.addEventListener('mouseup', this.onMouseUp.bind(this));
  }

  trackByItemId(index: number, item: GridItem): string {
    return item.id;
  }

  addWidget(type: string): void {
    const newItem: GridItem = {
      id: `${type}-${Date.now()}`,
      x: Math.random() * 200 + 50,
      y: Math.random() * 200 + 50,
      w: 400,
      h: 300,
      component: type,
      title: this.getWidgetTitle(type),
      resizable: true,
      draggable: true
    };
    this.gridItems.push(newItem);
  }

  private getWidgetTitle(type: string): string {
    switch (type) {
      case 'chart': return 'Price Chart';
      case 'orderbook': return 'Order Book';
      case 'trades': return 'Trade History';
      case 'watchlist': return 'Watchlist';
      default: return 'Widget';
    }
  }

  onItemMouseDown(event: MouseEvent, item: GridItem): void {
    if (!item.draggable) return;
    
    this.isDragging = true;
    this.dragItem = item;
    this.dragOffset = {
      x: event.clientX - item.x,
      y: event.clientY - item.y
    };
    event.preventDefault();
  }

  onResizeStart(event: MouseEvent, item: GridItem): void {
    if (!item.resizable) return;
    
    this.isResizing = true;
    this.dragItem = item;
    event.stopPropagation();
    event.preventDefault();
  }

  onMouseMove(event: MouseEvent): void {
    if (this.isDragging && this.dragItem) {
      this.dragItem.x = event.clientX - this.dragOffset.x;
      this.dragItem.y = event.clientY - this.dragOffset.y;
    } else if (this.isResizing && this.dragItem) {
      const rect = event.target as HTMLElement;
      this.dragItem.w = Math.max(200, event.clientX - this.dragItem.x);
      this.dragItem.h = Math.max(150, event.clientY - this.dragItem.y);
    }
  }

  onMouseUp(): void {
    this.isDragging = false;
    this.isResizing = false;
    this.dragItem = null;
  }

  removeItem(item: GridItem): void {
    this.gridItems = this.gridItems.filter(i => i.id !== item.id);
  }

  minimizeItem(item: GridItem): void {
    item.h = 32; // Just header height
  }

  maximizeItem(item: GridItem): void {
    item.x = 10;
    item.y = 10;
    item.w = window.innerWidth - 320; // Account for sidebar
    item.h = window.innerHeight - 120; // Account for header/toolbar
  }

  resetLayout(): void {
    this.initializeDefaultLayout();
  }

  saveLayout(): void {
    localStorage.setItem('trading-layout', JSON.stringify(this.gridItems));
    console.log('Layout saved');
  }

  toggleFullscreen(): void {
    this.isFullscreen = !this.isFullscreen;
    if (this.isFullscreen) {
      document.documentElement.requestFullscreen();
    } else {
      document.exitFullscreen();
    }
  }

  onSymbolChange(): void {
    this.marketDataService.setSelectedSymbol(this.selectedSymbol);
  }

  setChartType(type: string): void {
    this.chartType = type;
  }

  setOrderBookDepth(depth: number): void {
    this.orderBookDepth = depth;
  }

  setTradeFilter(filter: string): void {
    this.tradeFilter = filter;
  }

  selectSymbol(symbol: string): void {
    this.selectedSymbol = symbol;
    this.onSymbolChange();
  }

  addToWatchlist(): void {
    console.log('Add to watchlist');
  }

  getSpread(): number {
    if (this.mockAsks.length > 0 && this.mockBids.length > 0) {
      return this.mockAsks[0][0] - this.mockBids[0][0];
    }
    return 0;
  }

  formatTime(timestamp: number): string {
    return new Date(timestamp).toLocaleTimeString();
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
}
