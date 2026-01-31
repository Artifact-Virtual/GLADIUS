import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Activity, TrendingUp, TrendingDown, AlertTriangle,
  Filter, Search, Plus, Download, Edit, Trash2,
  FileText, BarChart2, PieChart, Eye, X, Save,
  Clock, CheckCircle, Calendar, RefreshCw
} from 'lucide-react';
import { MetricChart } from '../charts/MetricChart';

interface Report {
  id: string;
  title: string;
  date: string;
  markets: string[];
  signals: number;
  confidence: number;
  status: 'ready' | 'warning' | 'error';
  size: string;
}

interface MarketAnalysis {
  asset: string;
  price: number;
  change: number;
  volume: string;
  signal: 'buy' | 'sell' | 'hold';
  confidence: number;
  entry: number;
  target: number;
  stopLoss: number;
  riskReward: number;
}

interface TradingSignal {
  rank: number;
  asset: string;
  signal: 'buy' | 'sell' | 'hold';
  entry: number;
  target: number;
  stopLoss: number;
  riskReward: number;
  confidence: number;
}

export const SyndicateReports: React.FC = () => {
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [isEditMode, setIsEditMode] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const [reports, setReports] = useState<Report[]>([
    {
      id: '1',
      title: 'Daily Market Analysis - 2024-01-30',
      date: '2024-01-30',
      markets: ['BTC', 'ETH', 'SPY', 'NASDAQ'],
      signals: 12,
      confidence: 87.4,
      status: 'ready',
      size: '847 KB',
    },
    {
      id: '2',
      title: 'Crypto Sentiment Analysis',
      date: '2024-01-30',
      markets: ['BTC', 'ETH', 'ADA', 'SOL'],
      signals: 8,
      confidence: 92.1,
      status: 'ready',
      size: '1.2 MB',
    },
    {
      id: '3',
      title: 'Risk Assessment Report',
      date: '2024-01-30',
      markets: ['SPY', 'QQQ', 'IWM', 'DIA'],
      signals: 4,
      confidence: 78.6,
      status: 'warning',
      size: '654 KB',
    },
    {
      id: '4',
      title: 'Technical Analysis - Forex',
      date: '2024-01-29',
      markets: ['EUR/USD', 'GBP/USD'],
      signals: 6,
      confidence: 84.2,
      status: 'ready',
      size: '456 KB',
    },
    {
      id: '5',
      title: 'Options Flow Analysis',
      date: '2024-01-29',
      markets: ['SPX', 'RUT', 'NDX'],
      signals: 15,
      confidence: 89.7,
      status: 'ready',
      size: '2.1 MB',
    },
  ]);

  const [marketAnalyses, setMarketAnalyses] = useState<MarketAnalysis[]>([
    {
      asset: 'BTC/USD',
      price: 45234.67,
      change: 4.2,
      volume: '$28.4B',
      signal: 'buy',
      confidence: 92.4,
      entry: 45000,
      target: 47500,
      stopLoss: 43200,
      riskReward: 1.63,
    },
    {
      asset: 'ETH/USD',
      price: 2487.34,
      change: 8.4,
      volume: '$12.7B',
      signal: 'buy',
      confidence: 87.1,
      entry: 2475,
      target: 2650,
      stopLoss: 2350,
      riskReward: 1.4,
    },
    {
      asset: 'SPY',
      price: 492.18,
      change: 0.8,
      volume: '68.4M',
      signal: 'hold',
      confidence: 82.7,
      entry: 490,
      target: 498,
      stopLoss: 485,
      riskReward: 1.6,
    },
    {
      asset: 'QQQ',
      price: 428.67,
      change: 2.1,
      volume: '42.3M',
      signal: 'buy',
      confidence: 88.3,
      entry: 426,
      target: 440,
      stopLoss: 418,
      riskReward: 1.75,
    },
  ]);

  const [signals, setSignals] = useState<TradingSignal[]>([
    { rank: 1, asset: 'BTC/USD', signal: 'buy', entry: 45000, target: 47500, stopLoss: 43200, riskReward: 1.63, confidence: 92.4 },
    { rank: 2, asset: 'QQQ', signal: 'buy', entry: 426, target: 440, stopLoss: 418, riskReward: 1.75, confidence: 88.3 },
    { rank: 3, asset: 'ETH/USD', signal: 'buy', entry: 2475, target: 2650, stopLoss: 2350, riskReward: 1.4, confidence: 87.1 },
    { rank: 4, asset: 'AAPL', signal: 'buy', entry: 185.5, target: 195, stopLoss: 180, riskReward: 1.73, confidence: 85.6 },
    { rank: 5, asset: 'NVDA', signal: 'buy', entry: 725, target: 765, stopLoss: 705, riskReward: 2.0, confidence: 84.2 },
    { rank: 6, asset: 'SPY', signal: 'hold', entry: 490, target: 498, stopLoss: 485, riskReward: 1.6, confidence: 82.7 },
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ready': return '#00FF87';
      case 'warning': return '#FFB800';
      case 'error': return '#FF3366';
      default: return '#9CA3AF';
    }
  };

  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'buy': return '#00FF87';
      case 'sell': return '#FF3366';
      case 'hold': return '#FFB800';
      default: return '#9CA3AF';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'buy': return '🟢';
      case 'sell': return '🔴';
      case 'hold': return '🟡';
      default: return '⚪';
    }
  };

  const accuracyData = {
    labels: ['30-Day', '7-Day', '1-Day'],
    datasets: [{
      label: 'Accuracy %',
      data: [87.4, 89.2, 92.1],
      backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981'],
      borderColor: '#1E2749',
      borderWidth: 2,
    }],
  };

  const riskData = {
    labels: ['Market', 'Liquidity', 'Volatility', 'Correlation', 'Leverage', 'Regulatory'],
    datasets: [{
      label: 'Risk Level',
      data: [60, 40, 70, 50, 20, 30],
      backgroundColor: '#3B82F680',
      borderColor: '#3B82F6',
      borderWidth: 2,
    }],
  };

  return (
    <div className="flex h-full bg-bg-primary text-text-primary">
      {/* Report Browser Sidebar */}
      <div className="w-1/4 bg-bg-secondary border-r border-bg-accent p-4 overflow-y-auto">
        <div className="mb-4">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-lg font-bold">Report Library</h3>
            <span className="text-sm text-text-secondary">{reports.length} total</span>
          </div>
          
          {/* Search */}
          <div className="relative mb-3">
            <Search className="absolute left-3 top-2.5 w-4 h-4 text-text-secondary" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search reports..."
              className="w-full pl-10 pr-3 py-2 bg-bg-accent rounded border border-bg-accent focus:border-accent outline-none text-sm"
            />
          </div>

          {/* Filters */}
          <div className="mb-4">
            <button className="w-full px-3 py-2 bg-bg-accent hover:bg-bg-primary rounded text-sm transition-colors flex items-center justify-between">
              <span className="flex items-center space-x-2">
                <Filter className="w-4 h-4" />
                <span>Filters</span>
              </span>
              <span className="text-xs text-text-secondary">All</span>
            </button>
          </div>
        </div>

        {/* Report List */}
        <div className="space-y-2">
          {reports.map((report) => (
            <motion.div
              key={report.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`bg-bg-accent rounded-lg p-3 cursor-pointer transition-all ${
                selectedReport?.id === report.id ? 'ring-2 ring-accent' : 'hover:bg-bg-primary'
              }`}
              onClick={() => setSelectedReport(report)}
            >
              <div className="flex items-start justify-between mb-2">
                <FileText className="w-4 h-4 text-accent" />
                <div className="flex items-center space-x-1" style={{ color: getStatusColor(report.status) }}>
                  <CheckCircle className="w-3 h-3" />
                  <span className="text-xs font-mono uppercase">{report.status}</span>
                </div>
              </div>
              
              <h4 className="text-sm font-semibold mb-1">{report.title}</h4>
              <div className="text-xs text-text-secondary mb-2">
                Markets: {report.markets.join(', ')}
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">Signals: {report.signals}</span>
                <span className="text-text-secondary">Conf: {report.confidence}%</span>
              </div>
              <div className="text-xs text-text-secondary mt-1">Size: {report.size}</div>
              
              <div className="flex space-x-1 mt-2">
                <button className="flex-1 px-2 py-1 bg-bg-secondary hover:bg-bg-primary rounded text-xs transition-colors">
                  View
                </button>
                <button className="flex-1 px-2 py-1 bg-bg-secondary hover:bg-bg-primary rounded text-xs transition-colors">
                  Export
                </button>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Actions */}
        <div className="mt-4 space-y-2">
          <button className="w-full px-3 py-2 bg-status-online/20 hover:bg-status-online/30 text-status-online rounded transition-colors flex items-center justify-center space-x-2">
            <Plus className="w-4 h-4" />
            <span>Generate Report</span>
          </button>
        </div>

        {/* Generation Queue */}
        <div className="mt-4 bg-bg-accent rounded-lg p-3">
          <div className="text-sm font-semibold mb-2">Generation Queue</div>
          <div className="space-y-2">
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Intraday Analysis</span>
                <span>82%</span>
              </div>
              <div className="w-full bg-bg-secondary rounded-full h-1.5">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full" style={{ width: '82%' }} />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span>Sector Rotation</span>
                <span>34%</span>
              </div>
              <div className="w-full bg-bg-secondary rounded-full h-1.5">
                <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-1.5 rounded-full" style={{ width: '34%' }} />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Report Viewer */}
      <div className="flex-1 overflow-y-auto">
        {selectedReport ? (
          <div className="p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <BarChart2 className="w-6 h-6 text-status-online" />
                <h2 className="text-2xl font-bold">{selectedReport.title}</h2>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setIsEditMode(!isEditMode)}
                  className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors"
                >
                  {isEditMode ? <Save className="w-4 h-4" /> : <Edit className="w-4 h-4" />}
                  <span>{isEditMode ? 'Save' : 'Edit'}</span>
                </button>
                <button className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors">
                  <Download className="w-4 h-4" />
                  <span>Export</span>
                </button>
                <button
                  onClick={() => setSelectedReport(null)}
                  className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Executive Summary */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
            >
              <h3 className="text-lg font-semibold mb-3">Executive Summary</h3>
              <div className="grid grid-cols-4 gap-4 mb-4">
                <div>
                  <div className="text-sm text-text-secondary">Market Condition</div>
                  <div className="text-lg font-bold text-status-online">BULLISH</div>
                </div>
                <div>
                  <div className="text-sm text-text-secondary">Volatility</div>
                  <div className="text-lg font-bold text-warning">MODERATE</div>
                </div>
                <div>
                  <div className="text-sm text-text-secondary">Risk Level</div>
                  <div className="text-lg font-bold text-warning">MEDIUM</div>
                </div>
                <div>
                  <div className="text-sm text-text-secondary">Confidence</div>
                  <div className="text-lg font-bold text-accent">{selectedReport.confidence}%</div>
                </div>
              </div>
              <div className="text-sm space-y-2">
                <p className="text-text-secondary">Key Insights:</p>
                <ul className="list-disc list-inside space-y-1 text-text-primary">
                  <li>BTC showing strong momentum with breakout above $45k resistance</li>
                  <li>ETH following BTC with 8.4% gain, testing key supply zone at $2.5k</li>
                  <li>SPY maintaining uptrend, approaching all-time highs</li>
                  <li>NASDAQ tech sector leading with 2.1% intraday gain</li>
                </ul>
              </div>
            </motion.div>

            {/* Market Analysis Grid */}
            <div className="grid grid-cols-2 gap-4">
              {marketAnalyses.map((market, index) => (
                <motion.div
                  key={market.asset}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
                >
                  <div className="flex items-center justify-between mb-3">
                    <h4 className="text-lg font-bold">{market.asset}</h4>
                    <div className="flex items-center space-x-2">
                      <span style={{ color: getSignalColor(market.signal) }}>
                        {getSignalIcon(market.signal)}
                      </span>
                      <span
                        className="text-sm font-bold uppercase"
                        style={{ color: getSignalColor(market.signal) }}
                      >
                        {market.signal}
                      </span>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 mb-3 text-sm">
                    <div>
                      <div className="text-text-secondary">Price</div>
                      <div className="font-mono font-bold">
                        ${market.price.toLocaleString()} ({market.change > 0 ? '+' : ''}{market.change}%)
                      </div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Volume</div>
                      <div className="font-mono">{market.volume}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Entry</div>
                      <div className="font-mono">${market.entry.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Target</div>
                      <div className="font-mono text-status-online">${market.target.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">Stop Loss</div>
                      <div className="font-mono text-error">${market.stopLoss.toLocaleString()}</div>
                    </div>
                    <div>
                      <div className="text-text-secondary">R/R</div>
                      <div className="font-mono">1:{market.riskReward.toFixed(2)}</div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="text-xs text-text-secondary">
                      Confidence: <span className="text-text-primary font-mono">{market.confidence}%</span>
                    </div>
                    <button className="px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors">
                      View Chart
                    </button>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Quantitative Metrics */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.3 }}
              className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
            >
              <h3 className="text-lg font-semibold mb-4">Quantitative Metrics</h3>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <h4 className="text-sm font-semibold mb-2">Prediction Accuracy</h4>
                  <MetricChart type="bar" data={accuracyData} height={200} />
                </div>
                <div>
                  <h4 className="text-sm font-semibold mb-2">Risk Factors</h4>
                  <MetricChart type="bar" data={riskData} height={200} />
                </div>
                <div className="space-y-3">
                  <div className="bg-bg-accent rounded p-3">
                    <div className="text-sm text-text-secondary">Sharpe Ratio</div>
                    <div className="text-2xl font-bold">2.34</div>
                  </div>
                  <div className="bg-bg-accent rounded p-3">
                    <div className="text-sm text-text-secondary">Win Rate</div>
                    <div className="text-2xl font-bold">67.8%</div>
                  </div>
                  <div className="bg-bg-accent rounded p-3">
                    <div className="text-sm text-text-secondary">Max Drawdown</div>
                    <div className="text-2xl font-bold text-warning">-8.7%</div>
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Trading Signals Table */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Trading Signals</h3>
                <span className="text-sm text-text-secondary">{signals.length} active signals</span>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-bg-accent">
                      <th className="text-left py-2 px-2">#</th>
                      <th className="text-left py-2 px-2">Asset</th>
                      <th className="text-left py-2 px-2">Signal</th>
                      <th className="text-right py-2 px-2">Entry</th>
                      <th className="text-right py-2 px-2">Target</th>
                      <th className="text-right py-2 px-2">Stop</th>
                      <th className="text-right py-2 px-2">R/R</th>
                      <th className="text-right py-2 px-2">Confidence</th>
                    </tr>
                  </thead>
                  <tbody>
                    {signals.map((signal) => (
                      <tr key={signal.rank} className="border-b border-bg-accent/50 hover:bg-bg-accent transition-colors">
                        <td className="py-2 px-2 font-mono">{signal.rank}</td>
                        <td className="py-2 px-2 font-semibold">{signal.asset}</td>
                        <td className="py-2 px-2">
                          <span
                            className="px-2 py-0.5 rounded text-xs font-bold uppercase"
                            style={{
                              backgroundColor: `${getSignalColor(signal.signal)}20`,
                              color: getSignalColor(signal.signal),
                            }}
                          >
                            {getSignalIcon(signal.signal)} {signal.signal}
                          </span>
                        </td>
                        <td className="py-2 px-2 text-right font-mono">${signal.entry.toLocaleString()}</td>
                        <td className="py-2 px-2 text-right font-mono text-status-online">${signal.target.toLocaleString()}</td>
                        <td className="py-2 px-2 text-right font-mono text-error">${signal.stopLoss.toLocaleString()}</td>
                        <td className="py-2 px-2 text-right font-mono">1:{signal.riskReward.toFixed(2)}</td>
                        <td className="py-2 px-2 text-right font-mono">{signal.confidence}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </motion.div>
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-text-secondary">
            <div className="text-center">
              <FileText className="w-16 h-16 mx-auto mb-4 opacity-50" />
              <p className="text-lg">Select a report to view</p>
              <p className="text-sm mt-2">Choose from the list on the left or generate a new report</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
