import React, { useEffect, useState } from 'react'
import { useMarketData } from '../../contexts/MarketDataContext'
import { MarketDataService } from '../../services/MarketDataService'
import { BookOpen, TrendingDown, TrendingUp } from 'lucide-react'

interface OrderBookEntry {
  price: number
  size: number
  total: number
}

export function OrderBook() {
  const { selectedSymbol } = useMarketData()
  const [orderBook, setOrderBook] = useState<{
    bids: OrderBookEntry[]
    asks: OrderBookEntry[]
  } | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [spread, setSpread] = useState(0)

  useEffect(() => {
    loadOrderBook()
  }, [selectedSymbol])

  const loadOrderBook = async () => {
    try {
      setIsLoading(true)
      const marketDataService = MarketDataService.getInstance()
      const data = await marketDataService.getOrderBook(selectedSymbol, 15)
      setOrderBook(data)
      
      if (data.asks.length > 0 && data.bids.length > 0) {
        setSpread(data.asks[0].price - data.bids[0].price)
      }
    } catch (error) {
      console.error('Error loading order book:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const formatPrice = (price: number) => {
    return price.toLocaleString(undefined, { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 8 
    })
  }

  const formatSize = (size: number) => {
    return size.toFixed(6)
  }

  const getMaxTotal = () => {
    if (!orderBook) return 0
    const maxBid = Math.max(...orderBook.bids.map(b => b.total))
    const maxAsk = Math.max(...orderBook.asks.map(a => a.total))
    return Math.max(maxBid, maxAsk)
  }

  const maxTotal = getMaxTotal()

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-3 border-b border-dark-600 bg-dark-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <BookOpen className="h-4 w-4 text-gray-400" />
            <h3 className="text-sm font-medium text-white">Order Book</h3>
          </div>
          {spread > 0 && (
            <div className="text-xs text-gray-400">
              Spread: ${spread.toFixed(2)}
            </div>
          )}
        </div>
      </div>

      {/* Column Headers */}
      <div className="p-2 border-b border-dark-600 bg-dark-800">
        <div className="grid grid-cols-3 gap-2 text-xs text-gray-400">
          <span>Price (USD)</span>
          <span className="text-right">Size</span>
          <span className="text-right">Total</span>
        </div>
      </div>

      {isLoading ? (
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mx-auto mb-2"></div>
            <div className="text-xs text-gray-400">Loading order book...</div>
          </div>
        </div>
      ) : (
        <div className="flex-1 overflow-hidden">
          {/* Asks (Sell Orders) */}
          <div className="h-1/2 overflow-y-auto scrollbar-thin">
            <div className="space-y-px">
              {orderBook?.asks.slice().reverse().map((ask, index) => (
                <div key={index} className="relative">
                  {/* Background bar showing size */}
                  <div 
                    className="absolute right-0 top-0 h-full bg-red-500/10"
                    style={{ width: `${(ask.total / maxTotal) * 100}%` }}
                  />
                  <div className="relative grid grid-cols-3 gap-2 px-2 py-1 hover:bg-dark-700 transition-colors">
                    <span className="text-xs font-mono text-red-400 flex items-center">
                      <TrendingDown className="h-3 w-3 mr-1" />
                      {formatPrice(ask.price)}
                    </span>
                    <span className="text-xs font-mono text-right text-white">
                      {formatSize(ask.size)}
                    </span>
                    <span className="text-xs font-mono text-right text-gray-400">
                      {formatSize(ask.total)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Current Price */}
          <div className="border-y border-dark-600 bg-dark-700 p-2">
            <div className="text-center">
              <div className="text-lg font-mono text-white">
                ${orderBook?.asks[0]?.price ? formatPrice(orderBook.asks[0].price) : '---'}
              </div>
              <div className="text-xs text-gray-400">Current Price</div>
            </div>
          </div>

          {/* Bids (Buy Orders) */}
          <div className="h-1/2 overflow-y-auto scrollbar-thin">
            <div className="space-y-px">
              {orderBook?.bids.map((bid, index) => (
                <div key={index} className="relative">
                  {/* Background bar showing size */}
                  <div 
                    className="absolute right-0 top-0 h-full bg-green-500/10"
                    style={{ width: `${(bid.total / maxTotal) * 100}%` }}
                  />
                  <div className="relative grid grid-cols-3 gap-2 px-2 py-1 hover:bg-dark-700 transition-colors">
                    <span className="text-xs font-mono text-green-400 flex items-center">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      {formatPrice(bid.price)}
                    </span>
                    <span className="text-xs font-mono text-right text-white">
                      {formatSize(bid.size)}
                    </span>
                    <span className="text-xs font-mono text-right text-gray-400">
                      {formatSize(bid.total)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
