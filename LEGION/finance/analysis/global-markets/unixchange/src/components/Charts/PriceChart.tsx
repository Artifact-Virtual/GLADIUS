import React, { useEffect, useRef, useState } from 'react'
import { createChart, IChartApi, ISeriesApi, CandlestickData, Time } from 'lightweight-charts'
import { useMarketData } from '../../contexts/MarketDataContext'
import { MarketDataService } from '../../services/MarketDataService'
import { BarChart3, TrendingUp, Calendar, Zap } from 'lucide-react'

export function PriceChart() {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<IChartApi | null>(null)
  const seriesRef = useRef<ISeriesApi<'Candlestick'> | null>(null)
  const { selectedSymbol, marketData } = useMarketData()
  const [interval, setInterval] = useState('1h')
  const [chartType, setChartType] = useState<'candlestick' | 'line'>('candlestick')
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Create chart
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#1e293b' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#334155' },
        horzLines: { color: '#334155' },
      },
      crosshair: {
        mode: 1,
      },
      rightPriceScale: {
        borderColor: '#475569',
      },
      timeScale: {
        borderColor: '#475569',
        timeVisible: true,
        secondsVisible: false,
      },
    })

    chartRef.current = chart

    // Create series
    const series = chart.addCandlestickSeries({
      upColor: '#10b981',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#10b981',
      wickDownColor: '#ef4444',
    })

    seriesRef.current = series

    // Handle resize
    const handleResize = () => {
      if (chartContainerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: chartContainerRef.current.clientWidth,
          height: chartContainerRef.current.clientHeight,
        })
      }
    }

    window.addEventListener('resize', handleResize)

    return () => {
      window.removeEventListener('resize', handleResize)
      if (chartRef.current) {
        chartRef.current.remove()
      }
    }
  }, [])

  useEffect(() => {
    loadChartData()
  }, [selectedSymbol, interval])

  const loadChartData = async () => {
    if (!seriesRef.current) return

    try {
      setIsLoading(true)
      const marketDataService = MarketDataService.getInstance()
      const candleData = await marketDataService.getCandleData(selectedSymbol, interval, 200)
      
      const formattedData: CandlestickData[] = candleData.map(candle => ({
        time: (candle.time / 1000) as Time,
        open: candle.open,
        high: candle.high,
        low: candle.low,
        close: candle.close,
      }))

      seriesRef.current.setData(formattedData)
    } catch (error) {
      console.error('Error loading chart data:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const intervals = [
    { value: '1m', label: '1m' },
    { value: '5m', label: '5m' },
    { value: '15m', label: '15m' },
    { value: '1h', label: '1h' },
    { value: '4h', label: '4h' },
    { value: '1d', label: '1D' },
    { value: '1w', label: '1W' },
  ]

  const currentMarket = marketData[selectedSymbol]

  return (
    <div className="h-full flex flex-col">
      {/* Chart Header */}
      <div className="p-3 border-b border-dark-600 bg-dark-700">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h3 className="text-lg font-semibold text-white">{selectedSymbol}</h3>
            {currentMarket && (
              <div className="flex items-center space-x-2 text-sm">
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
            )}
          </div>

          <div className="flex items-center space-x-2">
            {/* Chart Type Toggle */}
            <div className="flex bg-dark-600 rounded-lg p-1">
              <button
                onClick={() => setChartType('candlestick')}
                className={`p-1 rounded transition-colors ${
                  chartType === 'candlestick' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <BarChart3 className="h-4 w-4" />
              </button>
              <button
                onClick={() => setChartType('line')}
                className={`p-1 rounded transition-colors ${
                  chartType === 'line' ? 'bg-primary-500 text-white' : 'text-gray-400 hover:text-white'
                }`}
              >
                <TrendingUp className="h-4 w-4" />
              </button>
            </div>

            {/* Interval Selector */}
            <div className="flex bg-dark-600 rounded-lg p-1 space-x-1">
              {intervals.map((int) => (
                <button
                  key={int.value}
                  onClick={() => setInterval(int.value)}
                  className={`px-2 py-1 text-xs rounded transition-colors ${
                    interval === int.value
                      ? 'bg-primary-500 text-white'
                      : 'text-gray-400 hover:text-white hover:bg-dark-500'
                  }`}
                >
                  {int.label}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Chart Container */}
      <div className="flex-1 relative">
        {isLoading && (
          <div className="absolute inset-0 bg-dark-800/50 flex items-center justify-center z-10">
            <div className="flex items-center space-x-2 text-primary-500">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-500"></div>
              <span className="text-sm">Loading chart data...</span>
            </div>
          </div>
        )}
        <div ref={chartContainerRef} className="w-full h-full" />
      </div>

      {/* Chart Footer */}
      <div className="p-2 border-t border-dark-600 bg-dark-700">
        <div className="flex items-center justify-between text-xs text-gray-400">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-1">
              <Calendar className="h-3 w-3" />
              <span>Last update: {currentMarket?.lastUpdate.toLocaleTimeString()}</span>
            </div>
          </div>
          <div className="flex items-center space-x-1">
            <Zap className="h-3 w-3" />
            <span>Real-time data</span>
          </div>
        </div>
      </div>
    </div>
  )
}
