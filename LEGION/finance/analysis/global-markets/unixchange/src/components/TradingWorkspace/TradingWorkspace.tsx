import React, { useState } from 'react'
import { Responsive, WidthProvider, Layout } from 'react-grid-layout'
import { PriceChart } from '../Charts/PriceChart'
import { OrderBook } from '../Trading/OrderBook'
import { TradeHistory } from '../Trading/TradeHistory'
import { MarketOverview } from '../Trading/MarketOverview'
import { TechnicalIndicators } from '../Charts/TechnicalIndicators'
import { Settings, Maximize2, Minimize2, X } from 'lucide-react'

const ResponsiveGridLayout = WidthProvider(Responsive)

interface LayoutItem {
  i: string
  x: number
  y: number
  w: number
  h: number
  minW?: number
  minH?: number
}

export function TradingWorkspace() {
  const [layouts, setLayouts] = useState<{ [key: string]: LayoutItem[] }>({
    lg: [
      { i: 'chart', x: 0, y: 0, w: 8, h: 6, minW: 4, minH: 4 },
      { i: 'orderbook', x: 8, y: 0, w: 4, h: 6, minW: 3, minH: 4 },
      { i: 'trades', x: 8, y: 6, w: 4, h: 4, minW: 3, minH: 3 },
      { i: 'overview', x: 0, y: 6, w: 4, h: 4, minW: 3, minH: 3 },
      { i: 'indicators', x: 4, y: 6, w: 4, h: 4, minW: 3, minH: 3 },
    ],
  })

  const [isLayoutLocked, setIsLayoutLocked] = useState(false)

  const handleLayoutChange = (layout: Layout[], layouts: { [key: string]: Layout[] }) => {
    if (!isLayoutLocked) {
      setLayouts(layouts)
    }
  }

  const renderComponent = (key: string) => {
    const components: { [key: string]: React.ReactNode } = {
      chart: <PriceChart />,
      orderbook: <OrderBook />,
      trades: <TradeHistory />,
      overview: <MarketOverview />,
      indicators: <TechnicalIndicators />,
    }

    return (
      <div className="h-full bg-dark-800 border border-dark-600 rounded-lg overflow-hidden">
        <div className="h-8 bg-dark-700 border-b border-dark-600 flex items-center justify-between px-3">
          <span className="text-sm text-gray-300 capitalize">{key}</span>
          <div className="flex items-center space-x-1">
            <button className="p-1 hover:bg-dark-600 rounded">
              <Settings className="h-3 w-3 text-gray-400" />
            </button>
            <button className="p-1 hover:bg-dark-600 rounded">
              <Maximize2 className="h-3 w-3 text-gray-400" />
            </button>
            <button className="p-1 hover:bg-dark-600 rounded">
              <X className="h-3 w-3 text-gray-400" />
            </button>
          </div>
        </div>
        <div className="h-[calc(100%-2rem)] p-2">
          {components[key]}
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-dark-900 relative">
      {/* Workspace Controls */}
      <div className="absolute top-4 right-4 z-10 flex items-center space-x-2">
        <button
          onClick={() => setIsLayoutLocked(!isLayoutLocked)}
          className={`px-3 py-1 text-xs rounded-lg transition-colors ${
            isLayoutLocked
              ? 'bg-red-500/20 text-red-400 border border-red-500/30'
              : 'bg-dark-700 text-gray-400 border border-dark-600 hover:bg-dark-600'
          }`}
        >
          {isLayoutLocked ? 'Locked' : 'Unlocked'}
        </button>
        <button className="px-3 py-1 text-xs rounded-lg bg-dark-700 text-gray-400 border border-dark-600 hover:bg-dark-600 transition-colors">
          Save Layout
        </button>
        <button className="px-3 py-1 text-xs rounded-lg bg-dark-700 text-gray-400 border border-dark-600 hover:bg-dark-600 transition-colors">
          Reset
        </button>
      </div>

      {/* Grid Layout */}
      <div className="h-full p-4">
        <ResponsiveGridLayout
          className="layout"
          layouts={layouts}
          onLayoutChange={handleLayoutChange}
          breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
          cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
          rowHeight={60}
          isDraggable={!isLayoutLocked}
          isResizable={!isLayoutLocked}
          margin={[8, 8]}
          containerPadding={[0, 0]}
        >
          {layouts.lg?.map((item) => (
            <div key={item.i}>
              {renderComponent(item.i)}
            </div>
          ))}
        </ResponsiveGridLayout>
      </div>
    </div>
  )
}
