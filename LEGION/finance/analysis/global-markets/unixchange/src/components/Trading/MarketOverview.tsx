import React from 'react'
import { useMarketData } from '../../contexts/MarketDataContext'
import { TrendingUp, TrendingDown, Activity, DollarSign } from 'lucide-react'

export function MarketOverview() {
  const { marketData, selectedSymbol } = useMarketData()
  const currentMarket = marketData[selectedSymbol]

  if (!currentMarket) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-gray-400">
          <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
          <p className="text-sm">No market data available</p>
        </div>
      </div>
    )
  }

  const formatPrice = (price: number) => {
    return price.toLocaleString(undefined, { 
      minimumFractionDigits: 2, 
      maximumFractionDigits: 8 
    })
  }

  const formatVolume = (volume: number) => {
    if (volume >= 1000000) {
      return `${(volume / 1000000).toFixed(2)}M`
    } else if (volume >= 1000) {
      return `${(volume / 1000).toFixed(2)}K`
    }
    return volume.toFixed(2)
  }

  const stats = [
    {
      label: 'Current Price',
      value: `$${formatPrice(currentMarket.price)}`,
      icon: DollarSign,
      color: 'text-white',
    },
    {
      label: '24h Change',
      value: `${currentMarket.changePercent >= 0 ? '+' : ''}${currentMarket.changePercent.toFixed(2)}%`,
      icon: currentMarket.changePercent >= 0 ? TrendingUp : TrendingDown,
      color: currentMarket.changePercent >= 0 ? 'text-green-500' : 'text-red-500',
    },
    {
      label: '24h High',
      value: `$${formatPrice(currentMarket.high24h)}`,
      icon: TrendingUp,
      color: 'text-green-400',
    },
    {
      label: '24h Low',
      value: `$${formatPrice(currentMarket.low24h)}`,
      icon: TrendingDown,
      color: 'text-red-400',
    },
    {
      label: '24h Volume',
      value: formatVolume(currentMarket.volume),
      icon: Activity,
      color: 'text-blue-400',
    },
  ]

  const priceChangeAmount = currentMarket.change
  const volumeUSD = currentMarket.volume * currentMarket.price

  return (
    <div className="h-full">
      {/* Header */}
      <div className="p-3 border-b border-dark-600 bg-dark-700">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-medium text-white">Market Overview</h3>
          <span className="text-xs text-gray-400">{selectedSymbol}</span>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="p-3 space-y-3">
        {stats.map((stat, index) => (
          <div key={index} className="bg-dark-700 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <stat.icon className={`h-4 w-4 ${stat.color}`} />
                <span className="text-sm text-gray-400">{stat.label}</span>
              </div>
              <span className={`text-sm font-mono ${stat.color}`}>
                {stat.value}
              </span>
            </div>
          </div>
        ))}

        {/* Additional Stats */}
        <div className="bg-dark-700 rounded-lg p-3">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">24h Change ($)</span>
              <span className={`text-sm font-mono ${
                priceChangeAmount >= 0 ? 'text-green-500' : 'text-red-500'
              }`}>
                {priceChangeAmount >= 0 ? '+' : ''}${Math.abs(priceChangeAmount).toFixed(2)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-400">Volume (USD)</span>
              <span className="text-sm font-mono text-white">
                ${formatVolume(volumeUSD)}
              </span>
            </div>
          </div>
        </div>

        {/* Price Range Bar */}
        <div className="bg-dark-700 rounded-lg p-3">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm text-gray-400">24h Range</span>
          </div>
          <div className="relative">
            <div className="h-2 bg-dark-600 rounded-full">
              <div 
                className="h-2 bg-gradient-to-r from-red-500 to-green-500 rounded-full"
                style={{
                  width: `${((currentMarket.price - currentMarket.low24h) / (currentMarket.high24h - currentMarket.low24h)) * 100}%`
                }}
              />
            </div>
            <div className="flex justify-between mt-1 text-xs text-gray-400">
              <span>${formatPrice(currentMarket.low24h)}</span>
              <span>${formatPrice(currentMarket.high24h)}</span>
            </div>
          </div>
        </div>

        {/* Last Update */}
        <div className="text-xs text-gray-400 text-center">
          Last updated: {currentMarket.lastUpdate.toLocaleTimeString()}
        </div>
      </div>
    </div>
  )
}
