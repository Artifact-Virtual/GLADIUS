// Market data types
export interface MarketData {
  symbol: string
  price: number
  change: number
  changePercent: number
  volume: number
  high24h: number
  low24h: number
  marketCap?: number
  lastUpdate: Date
}

export interface CandleData {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

export interface OrderBookEntry {
  price: number
  size: number
  total: number
}

export interface OrderBook {
  bids: OrderBookEntry[]
  asks: OrderBookEntry[]
  lastUpdate: Date
}

export interface Trade {
  id: string
  price: number
  size: number
  side: 'buy' | 'sell'
  timestamp: Date
}

// Chart types
export interface ChartConfig {
  symbol: string
  interval: string
  chartType: 'candlestick' | 'line' | 'area'
  indicators: string[]
  layout: {
    x: number
    y: number
    w: number
    h: number
  }
}

// WebSocket types
export interface WebSocketMessage {
  type: 'ticker' | 'trade' | 'orderbook' | 'kline'
  data: any
  symbol?: string
  timestamp: number
}

// UI types
export interface LayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  minW?: number
  minH?: number
  maxW?: number
  maxH?: number
}

export interface WorkspaceLayout {
  charts: LayoutItem[]
  panels: LayoutItem[]
}

// Market categories
export type MarketCategory = 'crypto' | 'forex' | 'stocks' | 'commodities'

export interface Market {
  symbol: string
  name: string
  category: MarketCategory
  baseAsset: string
  quoteAsset: string
  isActive: boolean
}
