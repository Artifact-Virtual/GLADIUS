import { useEffect, useState } from 'react';
import { Activity, Zap, Shield, Users, Package } from 'lucide-react';
import { useSystemStore } from '../stores/systemStore';

const Dashboard = () => {
  const systemStatus = useSystemStore((state) => state.systemStatus);
  const [stats, setStats] = useState({
    gladiusUptime: 0,
    sentinelScans: 0,
    legionAgents: 0,
    artifactCount: 0,
  });

  useEffect(() => {
    // Simulated stats - would be fetched from actual system
    setStats({
      gladiusUptime: 3600,
      sentinelScans: 42,
      legionAgents: systemStatus.legion.activeAgents || 0,
      artifactCount: 156,
    });
  }, [systemStatus]);

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold gradient-text">System Dashboard</h1>
        <p className="text-text-dim mt-2">Overview of all GLADIUS systems</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* GLADIUS Card */}
        <div className="card hover:glow-accent transition-all duration-300 cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <Zap className="text-accent" size={32} />
            <span className={`status-${systemStatus.gladius.status === 'running' ? 'running' : 'stopped'}`} />
          </div>
          <h3 className="text-lg font-semibold text-text-dim">GLADIUS</h3>
          <p className="text-2xl font-bold text-text mt-2">
            {systemStatus.gladius.status === 'running' ? 'Active' : 'Inactive'}
          </p>
          <p className="text-sm text-text-dim mt-2">
            Uptime: {formatUptime(stats.gladiusUptime)}
          </p>
        </div>

        {/* SENTINEL Card */}
        <div className="card hover:glow-accent transition-all duration-300 cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <Shield className="text-accent" size={32} />
            <span className={`status-${systemStatus.sentinel.status === 'running' ? 'running' : 'stopped'}`} />
          </div>
          <h3 className="text-lg font-semibold text-text-dim">SENTINEL</h3>
          <p className="text-2xl font-bold text-text mt-2">
            {systemStatus.sentinel.status === 'running' ? 'Running' : 'Stopped'}
          </p>
          <p className="text-sm text-text-dim mt-2">
            Total Scans: {stats.sentinelScans}
          </p>
        </div>

        {/* LEGION Card */}
        <div className="card hover:glow-accent transition-all duration-300 cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <Users className="text-accent" size={32} />
            <span className={`status-${systemStatus.legion.activeAgents && systemStatus.legion.activeAgents > 0 ? 'running' : 'stopped'}`} />
          </div>
          <h3 className="text-lg font-semibold text-text-dim">LEGION</h3>
          <p className="text-2xl font-bold text-text mt-2">{stats.legionAgents}</p>
          <p className="text-sm text-text-dim mt-2">Active Agents</p>
        </div>

        {/* Artifact Card */}
        <div className="card hover:glow-accent transition-all duration-300 cursor-pointer">
          <div className="flex items-center justify-between mb-4">
            <Package className="text-accent" size={32} />
            <span className={`status-${systemStatus.artifact.status === 'running' ? 'running' : 'stopped'}`} />
          </div>
          <h3 className="text-lg font-semibold text-text-dim">Artifact</h3>
          <p className="text-2xl font-bold text-text mt-2">{stats.artifactCount}</p>
          <p className="text-sm text-text-dim mt-2">Total Artifacts</p>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="card">
        <div className="flex items-center gap-3 mb-6">
          <Activity className="text-accent" size={24} />
          <h2 className="text-xl font-bold">Recent Activity</h2>
        </div>
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-primary/50 rounded-lg">
            <span className="status-running mt-1" />
            <div className="flex-1">
              <p className="text-sm text-text">GLADIUS benchmark completed</p>
              <p className="text-xs text-text-dim mt-1">2 minutes ago</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-primary/50 rounded-lg">
            <span className="status-running mt-1" />
            <div className="flex-1">
              <p className="text-sm text-text">SENTINEL scan completed successfully</p>
              <p className="text-xs text-text-dim mt-1">15 minutes ago</p>
            </div>
          </div>
          <div className="flex items-start gap-3 p-3 bg-primary/50 rounded-lg">
            <span className="status-warning mt-1" />
            <div className="flex-1">
              <p className="text-sm text-text">LEGION agent deployed to production</p>
              <p className="text-xs text-text-dim mt-1">1 hour ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
