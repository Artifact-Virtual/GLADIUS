import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Activity, Zap, Cpu, HardDrive, Wifi } from 'lucide-react';
import { MetricChart } from '../charts/MetricChart';

interface SystemMetrics {
  cpu: number;
  memory: number;
  disk: number;
  network: number;
  latency: number;
  requests: number;
}

export const TelemetryDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<SystemMetrics>({
    cpu: 24,
    memory: 68,
    disk: 45,
    network: 12,
    latency: 2.1,
    requests: 1247,
  });

  const [cpuHistory, setCpuHistory] = useState<number[]>(
    Array.from({ length: 20 }, () => Math.random() * 50 + 10)
  );

  const [networkHistory, setNetworkHistory] = useState<number[]>(
    Array.from({ length: 20 }, () => Math.random() * 20 + 5)
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setMetrics(prev => ({
        cpu: Math.max(5, Math.min(95, prev.cpu + (Math.random() - 0.5) * 10)),
        memory: Math.max(30, Math.min(90, prev.memory + (Math.random() - 0.5) * 5)),
        disk: prev.disk,
        network: Math.max(1, Math.min(100, prev.network + (Math.random() - 0.5) * 15)),
        latency: Math.max(0.5, prev.latency + (Math.random() - 0.5) * 0.5),
        requests: prev.requests + Math.floor(Math.random() * 5),
      }));

      setCpuHistory(prev => [...prev.slice(-19), metrics.cpu]);
      setNetworkHistory(prev => [...prev.slice(-19), metrics.network]);
    }, 1000);

    return () => clearInterval(interval);
  }, [metrics]);

  const cpuData = {
    labels: cpuHistory.map((_, i) => `${i}s`),
    datasets: [{
      label: 'CPU Usage (%)',
      data: cpuHistory,
      borderColor: '#3B82F6',
      backgroundColor: '#3B82F680',
      fill: true,
      tension: 0.4,
    }],
  };

  const networkData = {
    labels: networkHistory.map((_, i) => `${i}s`),
    datasets: [{
      label: 'Network (MB/s)',
      data: networkHistory,
      borderColor: '#10B981',
      backgroundColor: '#10B98180',
      fill: true,
      tension: 0.4,
    }],
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center space-x-3">
        <Activity className="w-6 h-6 text-status-online" />
        <h2 className="text-2xl font-bold">System Telemetry</h2>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          icon={<Cpu className="w-5 h-5" />}
          label="CPU Usage"
          value={`${metrics.cpu.toFixed(1)}%`}
          percentage={metrics.cpu}
          color="blue"
        />
        <MetricCard
          icon={<Activity className="w-5 h-5" />}
          label="Memory"
          value={`${metrics.memory.toFixed(1)}%`}
          percentage={metrics.memory}
          color="purple"
        />
        <MetricCard
          icon={<HardDrive className="w-5 h-5" />}
          label="Disk"
          value={`${metrics.disk}%`}
          percentage={metrics.disk}
          color="amber"
        />
        <MetricCard
          icon={<Wifi className="w-5 h-5" />}
          label="Network"
          value={`${metrics.network.toFixed(1)} MB/s`}
          percentage={(metrics.network / 100) * 100}
          color="green"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <h3 className="text-lg font-semibold mb-3">CPU Usage Over Time</h3>
          <MetricChart type="area" data={cpuData} height={250} />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <h3 className="text-lg font-semibold mb-3">Network Throughput</h3>
          <MetricChart type="area" data={networkData} height={250} />
        </motion.div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-3 gap-4">
        <StatCard label="Avg Latency" value={`${metrics.latency.toFixed(2)}ms`} trend="+0.3ms" />
        <StatCard label="Total Requests" value={metrics.requests.toLocaleString()} trend="+247 today" />
        <StatCard label="Uptime" value="3d 14h 23m" trend="99.9%" />
      </div>
    </div>
  );
};

interface MetricCardProps {
  icon: React.ReactNode;
  label: string;
  value: string;
  percentage: number;
  color: 'blue' | 'purple' | 'amber' | 'green';
}

const MetricCard: React.FC<MetricCardProps> = ({ icon, label, value, percentage, color }) => {
  const colors = {
    blue: 'from-blue-500 to-blue-600',
    purple: 'from-purple-500 to-purple-600',
    amber: 'from-amber-500 to-amber-600',
    green: 'from-green-500 to-green-600',
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
    >
      <div className="flex items-center justify-between mb-2">
        <div className={`p-2 bg-gradient-to-br ${colors[color]} rounded-lg`}>
          {icon}
        </div>
        <span className="text-2xl font-bold font-mono">{value}</span>
      </div>
      <div className="text-sm text-text-secondary mb-2">{label}</div>
      <div className="w-full bg-bg-primary rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5 }}
          className={`h-full bg-gradient-to-r ${colors[color]}`}
        />
      </div>
    </motion.div>
  );
};

interface StatCardProps {
  label: string;
  value: string;
  trend: string;
}

const StatCard: React.FC<StatCardProps> = ({ label, value, trend }) => (
  <div className="bg-bg-secondary rounded-lg p-4 border border-bg-accent">
    <div className="text-sm text-text-secondary mb-1">{label}</div>
    <div className="text-2xl font-bold mb-1">{value}</div>
    <div className="text-xs text-status-online">↗ {trend}</div>
  </div>
);
