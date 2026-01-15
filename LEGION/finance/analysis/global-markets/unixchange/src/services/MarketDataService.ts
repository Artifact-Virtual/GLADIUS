import axios from 'axios'
import { MarketData, CandleData, OrderBook } from '../types'

export class MarketDataService {
  private static instance: MarketDataService
  private baseURL = 'https://api.binance.com/api/v3'

  private constructor() {}

  static getInstance(): MarketDataService {
    if (!MarketDataService.instance) {
      MarketDataService.instance = new MarketDataService()
    }
    return MarketDataService.instance
  }

  async getMarketData(symbol: string): Promise<MarketData> {
    try {
      const response = await axios.get(`${this.baseURL}/ticker/24hr`, {
        params: { symbol }
      })

      const data = response.data
      return {
        symbol: data.symbol,
        price: parseFloat(data.lastPrice),
        change: parseFloat(data.priceChange),
        changePercent: parseFloat(data.priceChangePercent),
        volume: parseFloat(data.volume),
        high24h: parseFloat(data.highPrice),
        low24h: parseFloat(data.lowPrice),
        lastUpdate: new Date(),
      }
    } catch (error) {
      console.error(`Error fetching market data for ${symbol}:`, error)
      throw error
    }
  }

  async getCandleData(symbol: string, interval: string, limit: number = 100): Promise<CandleData[]> {
    try {
      const response = await axios.get(`${this.baseURL}/klines`, {
        params: {
          symbol,
          interval,
          limit
        }
      })

      return response.data.map((candle: any[]) => ({
        time: candle[0],
        open: parseFloat(candle[1]),
        high: parseFloat(candle[2]),
        low: parseFloat(candle[3]),
        close: parseFloat(candle[4]),
        volume: parseFloat(candle[5]),
      }))
    } catch (error) {
      console.error(`Error fetching candle data for ${symbol}:`, error)
      throw error
    }
  }

  async getOrderBook(symbol: string, limit: number = 20): Promise<OrderBook> {
    try {
      const response = await axios.get(`${this.baseURL}/depth`, {
        params: {
          symbol,
          limit
        }
      })

      const data = response.data
      
      const bids = data.bids.map((bid: string[]) => ({
        price: parseFloat(bid[0]),
        size: parseFloat(bid[1]),
        total: 0, // Will be calculated
      }))

      const asks = data.asks.map((ask: string[]) => ({
        price: parseFloat(ask[0]),
        size: parseFloat(ask[1]),
        total: 0, // Will be calculated
      }))

      // Calculate running totals
      let bidTotal = 0
      bids.forEach(bid => {
        bidTotal += bid.size
        bid.total = bidTotal
      })

      let askTotal = 0
      asks.forEach(ask => {
        askTotal += ask.size
        ask.total = askTotal
      })

      return {
        bids,
        asks,
        lastUpdate: new Date(),
      }
    } catch (error) {
      console.error(`Error fetching order book for ${symbol}:`, error)
      throw error
    }
  }

  async getTopMarkets(): Promise<MarketData[]> {
    try {
      const response = await axios.get(`${this.baseURL}/ticker/24hr`)
      
      return response.data
        .filter((ticker: any) => ticker.symbol.endsWith('USDT'))
        .sort((a: any, b: any) => parseFloat(b.quoteVolume) - parseFloat(a.quoteVolume))
        .slice(0, 50)
        .map((ticker: any) => ({
          symbol: ticker.symbol,
          price: parseFloat(ticker.lastPrice),
          change: parseFloat(ticker.priceChange),
          changePercent: parseFloat(ticker.priceChangePercent),
          volume: parseFloat(ticker.volume),
          high24h: parseFloat(ticker.highPrice),
          low24h: parseFloat(ticker.lowPrice),
          lastUpdate: new Date(),
        }))
    } catch (error) {
      console.error('Error fetching top markets:', error)
      throw error
    }
  }

  async searchSymbols(query: string): Promise<string[]> {
    try {
      const response = await axios.get(`${this.baseURL}/exchangeInfo`)
      const symbols = response.data.symbols
        .filter((symbol: any) => 
          symbol.status === 'TRADING' && 
          symbol.symbol.toLowerCase().includes(query.toLowerCase())
        )
        .map((symbol: any) => symbol.symbol)
        .slice(0, 20)

      return symbols
    } catch (error) {
      console.error('Error searching symbols:', error)
      throw error
    }
  }
}
