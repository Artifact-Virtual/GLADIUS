import React from 'react'
import { Loader2 } from 'lucide-react'

export function LoadingScreen() {
  return (
    <div className="min-h-screen bg-dark-900 flex items-center justify-center">
      <div className="text-center">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">UniXchange</h1>
          <p className="text-gray-400">Professional Market Charts & Trading</p>
        </div>
        <div className="flex items-center justify-center space-x-2 text-primary-500">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Connecting to markets...</span>
        </div>
        <div className="mt-8 w-64 bg-dark-700 rounded-full h-2 mx-auto">
          <div className="bg-primary-500 h-2 rounded-full animate-pulse" style={{ width: '70%' }}></div>
        </div>
      </div>
    </div>
  )
}
