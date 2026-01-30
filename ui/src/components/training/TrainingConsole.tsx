import React, { useState, useEffect } from 'react';
import { MetricChart } from '../charts/MetricChart';
import { Activity, Pause, Play, Save, Download } from 'lucide-react';
import { motion } from 'framer-motion';

interface TrainingMetrics {
  epoch: number;
  totalEpochs: number;
  step: number;
  totalSteps: number;
  loss: number;
  learningRate: number;
  throughput: number;
  expertCoverage: number[];
  memoryUsage: number;
  gradientNorm: number;
}

export const TrainingConsole: React.FC = () => {
  const [isTraining, setIsTraining] = useState(true);
  const [logs, setLogs] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<TrainingMetrics>({
    epoch: 42,
    totalEpochs: 100,
    step: 15420,
    totalSteps: 25000,
    loss: 0.3247,
    learningRate: 2.5e-5,
    throughput: 1240,
    expertCoverage: [0.24, 0.31, 0.28, 0.17],
    memoryUsage: 8.2,
    gradientNorm: 0.847,
  });

  const [lossHistory, setLossHistory] = useState<number[]>([
    0.80, 0.75, 0.68, 0.62, 0.58, 0.54, 0.50, 0.47, 0.44, 0.41, 
    0.39, 0.37, 0.35, 0.34, 0.32,
  ]);

  useEffect(() => {
    if (!isTraining) return;

    const interval = setInterval(() => {
      const timestamp = new Date().toLocaleTimeString();
      const newLogs = [
        `[${timestamp}] Epoch ${metrics.epoch}/${metrics.totalEpochs} | Step ${metrics.step}/${metrics.totalSteps}`,
        `[${timestamp}] Loss: ${metrics.loss.toFixed(4)} | LR: ${metrics.learningRate.toExponential(1)} | Throughput: ${metrics.throughput} tokens/s`,
        `[${timestamp}] Expert Coverage: MoE [${metrics.expertCoverage.map(v => v.toFixed(2)).join(', ')}]`,
        `[${timestamp}] Memory: ${metrics.memoryUsage} GB / 16 GB | GPU: N/A (CPU training)`,
        ...logs,
      ];

      setLogs(newLogs.slice(0, 50));

      // Simulate metrics update
      setMetrics(prev => ({
        ...prev,
        step: prev.step + 1,
        loss: Math.max(0.1, prev.loss - 0.0001 + (Math.random() - 0.5) * 0.01),
      }));

      setLossHistory(prev => [...prev.slice(-14), metrics.loss]);
    }, 2000);

    return () => clearInterval(interval);
  }, [isTraining, metrics]);

  const lossData = {
    labels: Array.from({ length: lossHistory.length }, (_, i) => (i * 5).toString()),
    datasets: [{
      label: 'Training Loss',
      data: lossHistory,
      borderColor: '#3B82F6',
      borderWidth: 2,
      tension: 0.4,
      pointRadius: 3,
      pointBackgroundColor: '#3B82F6',
    }],
  };

  const expertData = {
    labels: ['Expert 0', 'Expert 1', 'Expert 2', 'Expert 3'],
    datasets: [{
      label: 'Coverage',
      data: metrics.expertCoverage.map(v => v * 100),
      backgroundColor: ['#3B82F6', '#8B5CF6', '#10B981', '#F59E0B'],
      borderColor: '#1E2749',
      borderWidth: 2,
    }],
  };

  const throughputData = {
    labels: Array.from({ length: 10 }, (_, i) => `${i * 2}s`),
    datasets: [{
      label: 'Throughput (tokens/s)',
      data: Array.from({ length: 10 }, () => 1200 + Math.random() * 100),
      backgroundColor: '#3B82F680',
      borderColor: '#3B82F6',
      borderWidth: 2,
    }],
  };

  return (
    <div className="flex flex-col h-full bg-bg-primary text-text-primary p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-status-online" />
          <h2 className="text-2xl font-bold">Training Console</h2>
          <span className="px-3 py-1 bg-status-online/20 text-status-online rounded-full text-sm font-mono">
            Model: GLADIUS 1B v0.75
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsTraining(!isTraining)}
            className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors"
          >
            {isTraining ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
            <span>{isTraining ? 'Pause' : 'Resume'}</span>
          </button>
          <button className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors">
            <Save className="w-4 h-4" />
            <span>Save</span>
          </button>
          <button className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Live Stream */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold flex items-center space-x-2">
            <div className="w-2 h-2 bg-status-online rounded-full animate-pulse" />
            <span>Live Training Stream</span>
          </h3>
          <div className="flex items-center space-x-4 text-sm text-text-secondary">
            <span>Epoch {metrics.epoch}/{metrics.totalEpochs}</span>
            <span>•</span>
            <span>ETA: 4h 23m</span>
          </div>
        </div>
        <div className="bg-black/40 rounded p-3 font-mono text-xs h-48 overflow-y-auto">
          {logs.map((log, i) => (
            <div key={i} className="text-text-secondary mb-1">{log}</div>
          ))}
        </div>
      </motion.div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-2 gap-6 flex-1">
        {/* Loss Chart */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.1 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <h3 className="text-lg font-semibold mb-3">Training Loss</h3>
          <MetricChart type="area" data={lossData} height={250} />
        </motion.div>

        {/* Expert Coverage */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.2 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <h3 className="text-lg font-semibold mb-3">Expert Coverage (MoE)</h3>
          <MetricChart type="doughnut" data={expertData} height={250} />
        </motion.div>

        {/* Throughput */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <h3 className="text-lg font-semibold mb-3">Throughput</h3>
          <MetricChart type="bar" data={throughputData} height={250} />
        </motion.div>

        {/* Memory Usage */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent flex flex-col justify-between"
        >
          <h3 className="text-lg font-semibold mb-3">Memory Usage</h3>
          <div className="flex-1 flex flex-col justify-center space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-text-secondary">Used</span>
                <span className="font-mono">{metrics.memoryUsage} GB / 16 GB</span>
              </div>
              <div className="w-full bg-bg-primary rounded-full h-3 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${(metrics.memoryUsage / 16) * 100}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="bg-bg-primary p-3 rounded">
                <div className="text-text-secondary">Gradient Norm</div>
                <div className="text-xl font-mono">{metrics.gradientNorm.toFixed(3)}</div>
              </div>
              <div className="bg-bg-primary p-3 rounded">
                <div className="text-text-secondary">Learning Rate</div>
                <div className="text-xl font-mono">{metrics.learningRate.toExponential(1)}</div>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};
