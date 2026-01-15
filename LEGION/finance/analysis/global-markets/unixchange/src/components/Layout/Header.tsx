import React, { useState } from 'react'
import { 
  TrendingUp, 
  Search, 
  Settings, 
  Bell, 
  User, 
  Wifi,
  WifiOff,
  Globe
} from 'lucide-react'
import { useMarketData } from '../../contexts/MarketDataContext'

export function Header() {
  const { isConnected, selectedSymbol, marketData } = useMarketData()
  const [searchQuery, setSearchQuery] = useState('')

  const currentMarket = marketData[selectedSymbol]

  return (
    <header className="h-14 bg-dark-800 border-b border-dark-600 flex items-center justify-between px-4">
      {/* Logo and Brand */}
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <TrendingUp className="h-8 w-8 text-primary-500" />
          <h1 className="text-xl font-bold text-white">UniXchange</h1>
        </div>
        
        {/* Connection Status */}
        <div className="flex items-center space-x-2">
          {isConnected ? (
            <div className="flex items-center space-x-1 text-green-500">
              <Wifi className="h-4 w-4" />
              <span className="text-xs">Live</span>
            </div>
          ) : (
            <div className="flex items-center space-x-1 text-red-500">
              <WifiOff className="h-4 w-4" />
              <span className="text-xs">Disconnected</span>
            </div>
          )}
        </div>
      </div>

      {/* Current Market Info */}
      {currentMarket && (
        <div className="flex items-center space-x-6 text-sm">
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">{selectedSymbol}</span>
            <span className="text-white font-mono">
              ${currentMarket.price.toLocaleString(undefined, { 
                minimumFractionDigits: 2, 
                maximumFractionDigits: 8 
              })}
            </span>
            <span className={`font-mono ${
              currentMarket.changePercent >= 0 ? 'text-green-500' : 'text-red-500'
            }`}>
              {currentMarket.changePercent >= 0 ? '+' : ''}
              {currentMarket.changePercent.toFixed(2)}%
            </span>
          </div>
        </div>
      )}

      {/* Search and Controls */}
      <div className="flex items-center space-x-4">
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search markets..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-64 pl-10 pr-4 py-2 bg-dark-700 border border-dark-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-primary-500"
          />
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
            <Globe className="h-5 w-5" />
          </button>
          <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
            <Bell className="h-5 w-5" />
          </button>
          <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
            <Settings className="h-5 w-5" />
          </button>
          <button className="p-2 text-gray-400 hover:text-white hover:bg-dark-700 rounded-lg transition-colors">
            <User className="h-5 w-5" />
          </button>
        </div>
      </div>
    </header>
  )
}
