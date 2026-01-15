import React, { useState, useEffect } from 'react'
import { MarketDataProvider } from './contexts/MarketDataContext'
import { Layout } from './components/Layout/Layout'
import { TradingWorkspace } from './components/TradingWorkspace/TradingWorkspace'
import { LoadingScreen } from './components/UI/LoadingScreen'

function App() {
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 2000)

    return () => clearTimeout(timer)
  }, [])

  if (isLoading) {
    return <LoadingScreen />
  }

  return (
    <MarketDataProvider>
      <div className="min-h-screen bg-dark-900 text-white">
        <Layout>
          <TradingWorkspace />
        </Layout>
      </div>
    </MarketDataProvider>
  )
}

export default App
