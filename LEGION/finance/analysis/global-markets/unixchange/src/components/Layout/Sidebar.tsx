import React, { useState, useEffect } from 'react'
import { ChevronDown, Star, TrendingUp, TrendingDown } from 'lucide-react'
import { useMarketData } from '../../contexts/MarketDataContext'
import { MarketDataService } from '../../services/MarketDataService'

export function Sidebar() {
  const { marketData, setSelectedSymbol, selectedSymbol } = useMarketData()
  const [activeTab, setActiveTab] = useState<'favorites' | 'crypto' | 'forex' | 'stocks'>('crypto')
  const [topMarkets, setTopMarkets] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadTopMarkets()
  }, [])

  const loadTopMarkets = async () => {
    try {
      setIsLoading(true)
      const markets = await MarketDataService.getInstance().getTopMarkets()
      setTopMarkets(markets.slice(0, 20))
    } catch (error) {
      console.error('Error loading top markets:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const renderMarketRow = (market: any) => {
    const isSelected = market.symbol === selectedSymbol
    const priceColor = market.changePercent >= 0 ? 'text-green-500' : 'text-red-500'
    
    return (
      <div
        key={market.symbol}
        onClick={() => setSelectedSymbol(market.symbol)}
        className={`p-3 cursor-pointer hover:bg-dark-700 border-b border-dark-700 transition-colors ${
          isSelected ? 'bg-dark-700 border-l-2 border-l-primary-500' : ''
        }`}
      >
        <div className="flex items-center justify-between">
          <div className="flex-1">
            <div className="flex items-center space-x-2">
              <span className="font-medium text-white text-sm">{market.symbol}</span>
              <Star className="h-3 w-3 text-gray-500 hover:text-yellow-500 cursor-pointer" />
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Vol: {(market.volume / 1000000).toFixed(1)}M
            </div>
          </div>
          <div className="text-right">
            <div className="text-white font-mono text-sm">
              ${market.price.toLocaleString(undefined, { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 6 
              })}
            </div>
            <div className={`text-xs font-mono ${priceColor} flex items-center`}>
              {market.changePercent >= 0 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {market.changePercent.toFixed(2)}%
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="w-80 bg-dark-800 border-r border-dark-600 flex flex-col">
      {/* Tabs */}
      <div className="p-4 border-b border-dark-600">
        <div className="flex space-x-1 bg-dark-700 rounded-lg p-1">
          {[
            { id: 'favorites', label: 'Favorites', icon: Star },
            { id: 'crypto', label: 'Crypto', icon: TrendingUp },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-1 py-2 px-3 rounded-md text-xs transition-colors ${
                activeTab === tab.id
                  ? 'bg-primary-500 text-white'
                  : 'text-gray-400 hover:text-white hover:bg-dark-600'
              }`}
            >
              <tab.icon className="h-3 w-3" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Market List */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        {activeTab === 'crypto' && (
          <div>
            <div className="p-3 border-b border-dark-700">
              <div className="flex items-center justify-between text-xs text-gray-400">
                <span>Market</span>
                <div className="flex space-x-4">
                  <span>Price</span>
                  <span>24h%</span>
                </div>
              </div>
            </div>
            
            {isLoading ? (
              <div className="p-4 text-center text-gray-400">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-500 mx-auto"></div>
                <div className="mt-2 text-sm">Loading markets...</div>
              </div>
            ) : (
              <div>
                {topMarkets.map(renderMarketRow)}
              </div>
            )}
          </div>
        )}

        {activeTab === 'favorites' && (
          <div className="p-4 text-center text-gray-400">
            <Star className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No favorites yet</p>
            <p className="text-xs mt-1">Click the star icon to add markets</p>
          </div>
        )}
      </div>

      {/* Market Summary */}
      <div className="p-4 border-t border-dark-600 bg-dark-900">
        <div className="text-xs text-gray-400 mb-2">Market Summary</div>
        <div className="grid grid-cols-2 gap-4 text-xs">
          <div>
            <div className="text-gray-400">Markets</div>
            <div className="text-white font-mono">{topMarkets.length}</div>
          </div>
          <div>
            <div className="text-gray-400">24h Vol</div>
            <div className="text-white font-mono">
              {topMarkets.length > 0 && 
                `$${(topMarkets.reduce((sum, m) => sum + (m.volume * m.price), 0) / 1000000000).toFixed(1)}B`
              }
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
