import React from 'react'
import { TrendingUp, TrendingDown, Activity, BarChart } from 'lucide-react'

export function TechnicalIndicators() {
  // Mock technical indicators data
  const indicators = [
    {
      name: 'RSI (14)',
      value: 65.4,
      signal: 'neutral',
      description: 'Relative Strength Index',
    },
    {
      name: 'MACD',
      value: 0.82,
      signal: 'bullish',
      description: 'Moving Average Convergence Divergence',
    },
    {
      name: 'BB Upper',
      value: 45678.32,
      signal: 'resistance',
      description: 'Bollinger Bands Upper',
    },
    {
      name: 'BB Lower',
      value: 42156.78,
      signal: 'support',
      description: 'Bollinger Bands Lower',
    },
    {
      name: 'EMA 20',
      value: 44234.56,
      signal: 'bullish',
      description: 'Exponential Moving Average',
    },
    {
      name: 'SMA 50',
      value: 43876.32,
      signal: 'bullish',
      description: 'Simple Moving Average',
    },
  ]

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'bullish':
        return 'text-green-500'
      case 'bearish':
        return 'text-red-500'
      case 'resistance':
        return 'text-red-400'
      case 'support':
        return 'text-green-400'
      default:
        return 'text-gray-400'
    }
  }

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'bullish':
        return <TrendingUp className="h-3 w-3" />
      case 'bearish':
        return <TrendingDown className="h-3 w-3" />
      case 'resistance':
      case 'support':
        return <Activity className="h-3 w-3" />
      default:
        return <BarChart className="h-3 w-3" />
    }
  }

  return (
    <div className="h-full">
      <div className="p-3 border-b border-dark-600">
        <h3 className="text-sm font-medium text-white">Technical Indicators</h3>
      </div>
      
      <div className="p-3 space-y-3 h-[calc(100%-3rem)] overflow-y-auto scrollbar-thin">
        {indicators.map((indicator, index) => (
          <div key={index} className="bg-dark-700 rounded-lg p-3">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <span className={`${getSignalColor(indicator.signal)}`}>
                  {getSignalIcon(indicator.signal)}
                </span>
                <span className="text-sm font-medium text-white">{indicator.name}</span>
              </div>
              <span className={`text-xs uppercase px-2 py-1 rounded ${getSignalColor(indicator.signal)} bg-opacity-20`}>
                {indicator.signal}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-xs text-gray-400">{indicator.description}</span>
              <span className="text-sm font-mono text-white">
                {typeof indicator.value === 'number' 
                  ? indicator.value > 1000 
                    ? indicator.value.toLocaleString(undefined, { maximumFractionDigits: 2 })
                    : indicator.value.toFixed(2)
                  : indicator.value
                }
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
