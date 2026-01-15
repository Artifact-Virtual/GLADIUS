import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, interval, fromEvent } from 'rxjs';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { map, filter, catchError, retry, share } from 'rxjs/operators';

export interface MarketData {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  high24h: number;
  low24h: number;
  timestamp: number;
}

export interface OrderBookData {
  symbol: string;
  bids: [number, number][];
  asks: [number, number][];
  timestamp: number;
}

export interface TradeData {
  symbol: string;
  price: number;
  quantity: number;
  side: 'buy' | 'sell';
  timestamp: number;
}

@Injectable({
  providedIn: 'root'
})
export class MarketDataService {
  private marketDataSubject = new BehaviorSubject<MarketData[]>([]);
  private orderBookSubject = new BehaviorSubject<OrderBookData | null>(null);
  private tradesSubject = new BehaviorSubject<TradeData[]>([]);
  private connectionStatusSubject = new BehaviorSubject<boolean>(false);
  
  private websocketConnections: Map<string, WebSocketSubject<any>> = new Map();
  private selectedSymbol = 'BTCUSDT';
  private symbols = ['BTCUSDT', 'ETHUSDT', 'ADAUSDT', 'DOTUSDT', 'LINKUSDT'];

  public marketData$ = this.marketDataSubject.asObservable();
  public orderBook$ = this.orderBookSubject.asObservable();
  public trades$ = this.tradesSubject.asObservable();
  public connectionStatus$ = this.connectionStatusSubject.asObservable();

  constructor() {}

  async initialize(): Promise<void> {
    try {
      // Initialize programmatic data capture
      await this.initializeProgrammaticCapture();
      
      // Fallback to WebSocket connections if programmatic capture is not available
      this.initializeWebSocketConnections();
      
      console.log('Market data service initialized');
    } catch (error) {
      console.error('Failed to initialize market data service:', error);
      throw error;
    }
  }

  private async initializeProgrammaticCapture(): Promise<void> {
    // This method will implement programmatic data capture using tools like Wireshark
    // For now, we'll simulate the data capture process
    
    // Check if we're in a Node.js environment (for server-side data capture)
    if (typeof window === 'undefined') {
      try {
        // Import Node.js modules for data capture
        const { spawn } = await import('child_process');
        const fs = await import('fs');
        
        // Start network packet capture for market data
        this.startNetworkCapture();
        
        console.log('Programmatic data capture initialized');
      } catch (error) {
        console.warn('Node.js environment not available, falling back to WebSocket');
      }
    } else {
      // Browser environment - use WebRTC data channels for peer-to-peer data
      this.initializeWebRTCDataChannels();
    }
  }

  private startNetworkCapture(): void {
    // Simulate network packet capture for market data
    // In a real implementation, this would use tools like:
    // - Wireshark/tshark for network capture
    // - Raw socket connections
    // - Direct API polling with custom headers
    
    console.log('Starting network capture for market data...');
    
    // Simulate captured market data
    interval(1000).subscribe(() => {
      const simulatedData = this.generateSimulatedMarketData();
      this.marketDataSubject.next(simulatedData);
    });

    // Simulate order book updates
    interval(500).subscribe(() => {
      const orderBook = this.generateSimulatedOrderBook();
      this.orderBookSubject.next(orderBook);
    });

    // Simulate trade data
    interval(2000).subscribe(() => {
      const trades = this.generateSimulatedTrades();
      this.tradesSubject.next(trades);
    });

    this.connectionStatusSubject.next(true);
  }

  private initializeWebRTCDataChannels(): void {
    // Initialize WebRTC data channels for real-time data sharing
    // This allows for peer-to-peer market data distribution
    
    console.log('Initializing WebRTC data channels...');
    
    // Create RTCPeerConnection for data sharing
    const peerConnection = new RTCPeerConnection({
      iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
    });

    // Create data channel for market data
    const marketDataChannel = peerConnection.createDataChannel('marketData', {
      ordered: true
    });

    marketDataChannel.onopen = () => {
      console.log('Market data channel opened');
      this.connectionStatusSubject.next(true);
    };

    marketDataChannel.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.processReceivedData(data);
      } catch (error) {
        console.error('Failed to process received data:', error);
      }
    };
  }

  private initializeWebSocketConnections(): void {
    // Fallback WebSocket connections to public APIs
    const binanceWS = webSocket('wss://stream.binance.com:9443/ws/!ticker@arr');
    
    binanceWS.pipe(
      retry(3),
      catchError(error => {
        console.error('WebSocket error:', error);
        return [];
      })
    ).subscribe(data => {
      if (Array.isArray(data)) {
        const marketData = this.transformBinanceData(data);
        this.marketDataSubject.next(marketData);
      }
    });

    // Order book WebSocket
    const orderBookWS = webSocket(`wss://stream.binance.com:9443/ws/${this.selectedSymbol.toLowerCase()}@depth20@100ms`);
    
    orderBookWS.pipe(
      retry(3),
      catchError(error => {
        console.error('Order book WebSocket error:', error);
        return [];
      })
    ).subscribe(data => {
      const orderBook = this.transformOrderBookData(data);
      this.orderBookSubject.next(orderBook);
    });

    this.connectionStatusSubject.next(true);
  }

  private generateSimulatedMarketData(): MarketData[] {
    return this.symbols.map(symbol => ({
      symbol,
      price: 50000 + Math.random() * 10000,
      change: (Math.random() - 0.5) * 1000,
      changePercent: (Math.random() - 0.5) * 10,
      volume: Math.random() * 1000000,
      high24h: 55000 + Math.random() * 5000,
      low24h: 45000 + Math.random() * 5000,
      timestamp: Date.now()
    }));
  }

  private generateSimulatedOrderBook(): OrderBookData {
    const basePrice = 50000;
    const bids: [number, number][] = [];
    const asks: [number, number][] = [];

    for (let i = 0; i < 20; i++) {
      bids.push([basePrice - (i + 1) * 10, Math.random() * 10]);
      asks.push([basePrice + (i + 1) * 10, Math.random() * 10]);
    }

    return {
      symbol: this.selectedSymbol,
      bids,
      asks,
      timestamp: Date.now()
    };
  }

  private generateSimulatedTrades(): TradeData[] {
    const trades: TradeData[] = [];
    const basePrice = 50000;

    for (let i = 0; i < 10; i++) {
      trades.push({
        symbol: this.selectedSymbol,
        price: basePrice + (Math.random() - 0.5) * 100,
        quantity: Math.random() * 5,
        side: Math.random() > 0.5 ? 'buy' : 'sell',
        timestamp: Date.now() - i * 1000
      });
    }

    return trades;
  }

  private transformBinanceData(data: any[]): MarketData[] {
    return data.filter(item => this.symbols.includes(item.s)).map(item => ({
      symbol: item.s,
      price: parseFloat(item.c),
      change: parseFloat(item.P),
      changePercent: parseFloat(item.P),
      volume: parseFloat(item.v),
      high24h: parseFloat(item.h),
      low24h: parseFloat(item.l),
      timestamp: Date.now()
    }));
  }

  private transformOrderBookData(data: any): OrderBookData {
    return {
      symbol: data.s || this.selectedSymbol,
      bids: data.bids?.map((bid: string[]) => [parseFloat(bid[0]), parseFloat(bid[1])]) || [],
      asks: data.asks?.map((ask: string[]) => [parseFloat(ask[0]), parseFloat(ask[1])]) || [],
      timestamp: Date.now()
    };
  }

  private processReceivedData(data: any): void {
    switch (data.type) {
      case 'marketData':
        this.marketDataSubject.next(data.payload);
        break;
      case 'orderBook':
        this.orderBookSubject.next(data.payload);
        break;
      case 'trades':
        this.tradesSubject.next(data.payload);
        break;
      default:
        console.warn('Unknown data type received:', data.type);
    }
  }

  setSelectedSymbol(symbol: string): void {
    this.selectedSymbol = symbol;
    // Reinitialize connections for new symbol
    this.initializeWebSocketConnections();
  }

  getSelectedSymbol(): string {
    return this.selectedSymbol;
  }

  getAvailableSymbols(): string[] {
    return [...this.symbols];
  }

  disconnect(): void {
    this.websocketConnections.forEach(ws => ws.complete());
    this.websocketConnections.clear();
    this.connectionStatusSubject.next(false);
  }
}
