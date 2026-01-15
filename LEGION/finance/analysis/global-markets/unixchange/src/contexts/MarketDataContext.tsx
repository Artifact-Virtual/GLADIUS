import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { MarketData, OrderBook, Trade, WebSocketMessage } from '../types'
import { WebSocketService } from '../services/WebSocketService'
import { MarketDataService } from '../services/MarketDataService'

interface MarketDataState {
  marketData: Record<string, MarketData>
  orderBooks: Record<string, OrderBook>
  recentTrades: Record<string, Trade[]>
  selectedSymbol: string
  isConnected: boolean
  isLoading: boolean
  error: string | null
}

type MarketDataAction =
  | { type: 'SET_MARKET_DATA'; payload: { symbol: string; data: MarketData } }
  | { type: 'SET_ORDER_BOOK'; payload: { symbol: string; orderBook: OrderBook } }
  | { type: 'ADD_TRADE'; payload: { symbol: string; trade: Trade } }
  | { type: 'SET_SELECTED_SYMBOL'; payload: string }
  | { type: 'SET_CONNECTION_STATUS'; payload: boolean }
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }

const initialState: MarketDataState = {
  marketData: {},
  orderBooks: {},
  recentTrades: {},
  selectedSymbol: 'BTCUSDT',
  isConnected: false,
  isLoading: true,
  error: null,
}

function marketDataReducer(state: MarketDataState, action: MarketDataAction): MarketDataState {
  switch (action.type) {
    case 'SET_MARKET_DATA':
      return {
        ...state,
        marketData: {
          ...state.marketData,
          [action.payload.symbol]: action.payload.data,
        },
      }
    case 'SET_ORDER_BOOK':
      return {
        ...state,
        orderBooks: {
          ...state.orderBooks,
          [action.payload.symbol]: action.payload.orderBook,
        },
      }
    case 'ADD_TRADE':
      const currentTrades = state.recentTrades[action.payload.symbol] || []
      return {
        ...state,
        recentTrades: {
          ...state.recentTrades,
          [action.payload.symbol]: [action.payload.trade, ...currentTrades.slice(0, 49)],
        },
      }
    case 'SET_SELECTED_SYMBOL':
      return {
        ...state,
        selectedSymbol: action.payload,
      }
    case 'SET_CONNECTION_STATUS':
      return {
        ...state,
        isConnected: action.payload,
      }
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
      }
    default:
      return state
  }
}

interface MarketDataContextType extends MarketDataState {
  dispatch: React.Dispatch<MarketDataAction>
  subscribeToSymbol: (symbol: string) => void
  unsubscribeFromSymbol: (symbol: string) => void
  setSelectedSymbol: (symbol: string) => void
}

const MarketDataContext = createContext<MarketDataContextType | undefined>(undefined)

interface MarketDataProviderProps {
  children: ReactNode
}

export function MarketDataProvider({ children }: MarketDataProviderProps) {
  const [state, dispatch] = useReducer(marketDataReducer, initialState)
  const wsService = WebSocketService.getInstance()
  const marketDataService = MarketDataService.getInstance()

  useEffect(() => {
    // Initialize services
    wsService.onMessage = (message: WebSocketMessage) => {
      switch (message.type) {
        case 'ticker':
          if (message.symbol) {
            dispatch({
              type: 'SET_MARKET_DATA',
              payload: { symbol: message.symbol, data: message.data },
            })
          }
          break
        case 'trade':
          if (message.symbol) {
            dispatch({
              type: 'ADD_TRADE',
              payload: { symbol: message.symbol, trade: message.data },
            })
          }
          break
        case 'orderbook':
          if (message.symbol) {
            dispatch({
              type: 'SET_ORDER_BOOK',
              payload: { symbol: message.symbol, orderBook: message.data },
            })
          }
          break
      }
    }

    wsService.onConnectionChange = (connected: boolean) => {
      dispatch({ type: 'SET_CONNECTION_STATUS', payload: connected })
    }

    // Connect to WebSocket
    wsService.connect()

    // Load initial data
    loadInitialData()

    return () => {
      wsService.disconnect()
    }
  }, [])

  const loadInitialData = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true })
      
      // Load popular symbols
      const symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
      
      for (const symbol of symbols) {
        try {
          const marketData = await marketDataService.getMarketData(symbol)
          dispatch({
            type: 'SET_MARKET_DATA',
            payload: { symbol, data: marketData },
          })
        } catch (error) {
          console.error(`Error loading data for ${symbol}:`, error)
        }
      }

      dispatch({ type: 'SET_ERROR', payload: null })
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: 'Failed to load market data' })
      console.error('Error loading initial data:', error)
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false })
    }
  }

  const subscribeToSymbol = (symbol: string) => {
    wsService.subscribe(symbol)
  }

  const unsubscribeFromSymbol = (symbol: string) => {
    wsService.unsubscribe(symbol)
  }

  const setSelectedSymbol = (symbol: string) => {
    dispatch({ type: 'SET_SELECTED_SYMBOL', payload: symbol })
    subscribeToSymbol(symbol)
  }

  const contextValue: MarketDataContextType = {
    ...state,
    dispatch,
    subscribeToSymbol,
    unsubscribeFromSymbol,
    setSelectedSymbol,
  }

  return (
    <MarketDataContext.Provider value={contextValue}>
      {children}
    </MarketDataContext.Provider>
  )
}

export function useMarketData() {
  const context = useContext(MarketDataContext)
  if (context === undefined) {
    throw new Error('useMarketData must be used within a MarketDataProvider')
  }
  return context
}
