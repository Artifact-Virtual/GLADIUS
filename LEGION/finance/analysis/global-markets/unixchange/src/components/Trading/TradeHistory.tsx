import React from 'react'
import { useMarketData } from '../../contexts/MarketDataContext'
import { Clock, TrendingUp, TrendingDown } from 'lucide-react'

export function TradeHistory() {
  const { recentTrades, selectedSymbol } = useMarketData()
  
  // Mock trades for demonstration
  const mockTrades = [
    { id: '1', price: 43567.89, size: 0.125, side: 'buy' as const, timestamp: new Date() },
    { id: '2', price: 43565.12, size: 0.089, side: 'sell' as const, timestamp: new Date(Date.now() - 1000) },
    { id: '3', price: 43568.45, size: 0.234, side: 'buy' as const, timestamp: new Date(Date.now() - 2000) },
    { id: '4', price: 43562.78, size: 0.156, side: 'sell' as const, timestamp: new Date(Date.now() - 3000) },
    { id: '5', price: 43570.23, size: 0.078, side: 'buy' as const, timestamp: new Date(Date.now() - 4000) },
    { id: '6', price: 43558.91, size: 0.298, side: 'sell' as const, timestamp: new Date(Date.now() - 5000) },
    { id: '7', price: 43572.44, size: 0.187, side: 'buy' as const, timestamp: new Date(Date.now() - 6000) },
    { id: '8', price: 43555.67, size: 0.145, side: 'sell' as const, timestamp: new Date(Date.now() - 7000) },
  ]

  const trades = recentTrades[selectedSymbol] || mockTrades

  const formatPrice = (price: number) => {
    return price.toLocaleString(undefined, { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 8 
    })
  }

  const formatSize = (size: number) => {
    return size.toFixed(6)
  }

  const formatTime = (timestamp: Date) => {
    return timestamp.toLocaleTimeString([], { 
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  }

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-dark-600 bg-dark-700">
        <div className="flex items-center space-x-2">
          <Clock className="h-4 w-4 text-gray-400" />
          <h3 className="text-sm font-medium text-white">Recent Trades</h3>
        </div>
      </div>

      {/* Column Headers */}
      <div className="p-2 border-b border-dark-600 bg-dark-800">
        <div className="grid grid-cols-4 gap-2 text-xs text-gray-400">
          <span>Time</span>
          <span className="text-right">Price (USD)</span>
          <span className="text-right">Size</span>
          <span className="text-center">Side</span>
        </div>
      </div>

      {/* Trades List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="space-y-px">
          {trades.map((trade, index) => (
            <div key={trade.id || index} className="grid grid-cols-4 gap-2 px-2 py-1 hover:bg-dark-700 transition-colors">
              <span className="text-xs font-mono text-gray-400">
                {formatTime(trade.timestamp)}
              </span>
              <span className={`text-xs font-mono text-right ${
                trade.side === 'buy' ? 'text-green-400' : 'text-red-400'
              }`}>
                {formatPrice(trade.price)}
              </span>
              <span className="text-xs font-mono text-right text-white">
                {formatSize(trade.size)}
              </span>
              <div className="flex items-center justify-center">
                {trade.side === 'buy' ? (
                  <div className="flex items-center space-x-1 text-green-400">
                    <TrendingUp className="h-3 w-3" />
                    <span className="text-xs">BUY</span>
                  </div>
                ) : (
                  <div className="flex items-center space-x-1 text-red-400">
                    <TrendingDown className="h-3 w-3" />
                    <span className="text-xs">SELL</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="p-2 border-t border-dark-600 bg-dark-700">
        <div className="text-xs text-gray-400 text-center">
          Showing last {trades.length} trades
        </div>
      </div>
    </div>
  )
}
