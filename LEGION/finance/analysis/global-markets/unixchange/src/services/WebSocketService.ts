import { WebSocketMessage } from '../types'

export class WebSocketService {
  private static instance: WebSocketService
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private subscriptions = new Set<string>()
  
  public onMessage: ((message: WebSocketMessage) => void) | null = null
  public onConnectionChange: ((connected: boolean) => void) | null = null

  private constructor() {}

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService()
    }
    return WebSocketService.instance
  }

  connect(): void {
    try {
      // Using Binance WebSocket for demo (in production, use your own WebSocket server)
      this.ws = new WebSocket('wss://stream.binance.com:9443/ws/!ticker@arr')
      
      this.ws.onopen = () => {
        console.log('WebSocket connected')
        this.reconnectAttempts = 0
        this.onConnectionChange?.(true)
        
        // Resubscribe to all symbols
        this.subscriptions.forEach(symbol => {
          this.subscribeToSymbol(symbol)
        })
      }

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          this.handleMessage(data)
        } catch (error) {
          console.error('Error parsing WebSocket message:', error)
        }
      }

      this.ws.onclose = () => {
        console.log('WebSocket disconnected')
        this.onConnectionChange?.(false)
        this.reconnect()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
      }
    } catch (error) {
      console.error('Error connecting to WebSocket:', error)
      this.reconnect()
    }
  }

  private handleMessage(data: any): void {
    // Handle Binance WebSocket format
    if (Array.isArray(data)) {
      // Handle ticker array from !ticker@arr stream
      data.forEach(ticker => {
        const message: WebSocketMessage = {
          type: 'ticker',
          symbol: ticker.s,
          data: {
            symbol: ticker.s,
            price: parseFloat(ticker.c),
            change: parseFloat(ticker.P),
            changePercent: parseFloat(ticker.P),
            volume: parseFloat(ticker.v),
            high24h: parseFloat(ticker.h),
            low24h: parseFloat(ticker.l),
            lastUpdate: new Date(),
          },
          timestamp: Date.now(),
        }
        this.onMessage?.(message)
      })
    } else if (data.e === '24hrTicker') {
      // Handle individual ticker
      const message: WebSocketMessage = {
        type: 'ticker',
        symbol: data.s,
        data: {
          symbol: data.s,
          price: parseFloat(data.c),
          change: parseFloat(data.P),
          changePercent: parseFloat(data.P),
          volume: parseFloat(data.v),
          high24h: parseFloat(data.h),
          low24h: parseFloat(data.l),
          lastUpdate: new Date(),
        },
        timestamp: Date.now(),
      }
      this.onMessage?.(message)
    }
  }

  private reconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`)
      
      setTimeout(() => {
        this.connect()
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  subscribe(symbol: string): void {
    this.subscriptions.add(symbol)
    this.subscribeToSymbol(symbol)
  }

  unsubscribe(symbol: string): void {
    this.subscriptions.delete(symbol)
    this.unsubscribeFromSymbol(symbol)
  }

  private subscribeToSymbol(symbol: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      // For demo purposes, we're using the all-tickers stream
      // In production, you'd subscribe to specific symbol streams
      console.log(`Subscribed to ${symbol}`)
    }
  }

  private unsubscribeFromSymbol(symbol: string): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      console.log(`Unsubscribed from ${symbol}`)
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }
}
