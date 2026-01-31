import { useEffect, useState } from 'react';
import { Activity, Zap, Shield, Users, Package, Play, Square, RefreshCw, Brain, Database, Terminal } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ServiceStatus {
  gladius: { status: string; model?: string };
  sentinel: { status: string; pid?: number };
  legion: { status: string; activeAgents: number };
  artifact: { status: string };
}

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<ServiceStatus>({
    gladius: { status: 'stopped' },
    sentinel: { status: 'stopped' },
    legion: { status: 'stopped', activeAgents: 0 },
    artifact: { status: 'stopped' }
  });
  const [stats, setStats] = useState({
    gladiusUptime: 0,
    sentinelScans: 42,
    legionAgents: 0,
    artifactCount: 156,
    toolCount: 100,
    memorySize: '12.4 GB'
  });
  const [activity, setActivity] = useState([
    { type: 'success', message: 'System initialized', time: 'Just now' },
    { type: 'success', message: 'GLADIUS model loaded', time: '1 minute ago' },
    { type: 'info', message: 'Hektor VDB connected', time: '2 minutes ago' }
  ]);

  useEffect(() => {
    checkAllStatus();
    const interval = setInterval(checkAllStatus, 15000);
    return () => clearInterval(interval);
  }, []);

  const checkAllStatus = async () => {
    setLoading(true);
    try {
      // Check GLADIUS
      const gladiusResult = await (window as any).electronAPI?.gladius?.status?.();
      // Check SENTINEL
      const sentinelResult = await (window as any).electronAPI?.sentinel?.status?.();
      // Check LEGION
      const legionResult = await (window as any).electronAPI?.legion?.status?.();

      setStatus({
        gladius: {
          status: gladiusResult?.success && gladiusResult?.data?.status === 'ready' ? 'running' : 'stopped',
          model: gladiusResult?.data?.version || 'gladius1.1:71M'
        },
        sentinel: {
          status: sentinelResult?.data?.running ? 'running' : 'stopped',
          pid: sentinelResult?.data?.pid
        },
        legion: {
          status: legionResult?.data?.running ? 'running' : 'stopped',
          activeAgents: legionResult?.data?.activeAgents || 0
        },
        artifact: { status: 'running' }
      });

      setStats(prev => ({
        ...prev,
        legionAgents: legionResult?.data?.activeAgents || 0
      }));
    } catch (error) {
      console.error('Status check failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleSentinel = async () => {
    try {
      if (status.sentinel.status === 'running') {
        await (window as any).electronAPI?.sentinel?.stop?.();
        addActivity('info', 'SENTINEL stopped');
      } else {
        await (window as any).electronAPI?.sentinel?.start?.({});
        addActivity('success', 'SENTINEL started');
      }
      setTimeout(checkAllStatus, 1000);
    } catch (error) {
      addActivity('error', `SENTINEL toggle failed: ${error}`);
    }
  };

  const toggleLegion = async () => {
    try {
      if (status.legion.status === 'running') {
        await (window as any).electronAPI?.legion?.stop?.();
        addActivity('info', 'LEGION stopped');
      } else {
        await (window as any).electronAPI?.legion?.start?.({});
        addActivity('success', 'LEGION started');
      }
      setTimeout(checkAllStatus, 1000);
    } catch (error) {
      addActivity('error', `LEGION toggle failed: ${error}`);
    }
  };

  const addActivity = (type: string, message: string) => {
    setActivity(prev => [
      { type, message, time: 'Just now' },
      ...prev.slice(0, 9)
    ]);
  };

  const formatUptime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    return `${hours}h ${minutes}m`;
  };

  const getStatusClass = (status: string) => {
    return status === 'running' ? 'status-running' : 'status-stopped';
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'success': return 'status-running';
      case 'error': return 'status-stopped';
      case 'info': return 'status-warning';
      default: return 'status-warning';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text">Artifact Virtual Enterprise</h1>
          <p className="text-text-dim mt-2">System Control Dashboard - GLADIUS gladius1.1:71M-native</p>
        </div>
        <button
          onClick={checkAllStatus}
          disabled={loading}
          className="p-2 bg-primary/50 hover:bg-primary rounded-lg transition-colors"
          title="Refresh Status"
        >
          <RefreshCw size={20} className={loading ? 'animate-spin' : ''} />
        </button>
      </div>

      {/* Quick Stats Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
        <div className="card bg-gradient-to-br from-purple-500/10 to-transparent p-4">
          <Brain className="text-purple-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Model</p>
          <p className="font-bold">71M params</p>
        </div>
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent p-4">
          <Terminal className="text-blue-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Tools</p>
          <p className="font-bold">{stats.toolCount}+ routed</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent p-4">
          <Database className="text-green-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Memory</p>
          <p className="font-bold">{stats.memorySize}</p>
        </div>
        <div className="card bg-gradient-to-br from-orange-500/10 to-transparent p-4">
          <Users className="text-orange-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Agents</p>
          <p className="font-bold">26 available</p>
        </div>
        <div className="card bg-gradient-to-br from-cyan-500/10 to-transparent p-4">
          <Shield className="text-cyan-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Scans</p>
          <p className="font-bold">{stats.sentinelScans}</p>
        </div>
        <div className="card bg-gradient-to-br from-pink-500/10 to-transparent p-4">
          <Package className="text-pink-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Artifacts</p>
          <p className="font-bold">{stats.artifactCount}</p>
        </div>
      </div>

      {/* Service Control Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* GLADIUS Card */}
        <div 
          className="card hover:glow-accent transition-all duration-300 cursor-pointer"
          onClick={() => navigate('/gladius')}
        >
          <div className="flex items-center justify-between mb-4">
            <Zap className="text-accent" size={32} />
            <span className={getStatusClass(status.gladius.status)} />
          </div>
          <h3 className="text-lg font-semibold text-text-dim">GLADIUS</h3>
          <p className="text-2xl font-bold text-text mt-2">
            {status.gladius.status === 'running' ? 'Online' : 'Offline'}
          </p>
          <p className="text-sm text-text-dim mt-2">
            {status.gladius.model}
          </p>
        </div>

        {/* SENTINEL Card */}
        <div className="card hover:glow-accent transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <Shield className="text-accent" size={32} />
            <div className="flex items-center gap-2">
              <span className={getStatusClass(status.sentinel.status)} />
              <button
                onClick={(e) => { e.stopPropagation(); toggleSentinel(); }}
                className={`p-1 rounded transition-colors ${
                  status.sentinel.status === 'running' 
                    ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' 
                    : 'bg-green-500/20 hover:bg-green-500/40 text-green-400'
                }`}
              >
                {status.sentinel.status === 'running' ? <Square size={14} /> : <Play size={14} />}
              </button>
            </div>
          </div>
          <h3 
            className="text-lg font-semibold text-text-dim cursor-pointer hover:text-accent"
            onClick={() => navigate('/sentinel')}
          >
            SENTINEL
          </h3>
          <p className="text-2xl font-bold text-text mt-2">
            {status.sentinel.status === 'running' ? 'Running' : 'Stopped'}
          </p>
          <p className="text-sm text-text-dim mt-2">
            {status.sentinel.pid ? `PID: ${status.sentinel.pid}` : 'Guardian System'}
          </p>
        </div>

        {/* LEGION Card */}
        <div className="card hover:glow-accent transition-all duration-300">
          <div className="flex items-center justify-between mb-4">
            <Users className="text-accent" size={32} />
            <div className="flex items-center gap-2">
              <span className={getStatusClass(status.legion.status)} />
              <button
                onClick={(e) => { e.stopPropagation(); toggleLegion(); }}
                className={`p-1 rounded transition-colors ${
                  status.legion.status === 'running' 
                    ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' 
                    : 'bg-green-500/20 hover:bg-green-500/40 text-green-400'
                }`}
              >
                {status.legion.status === 'running' ? <Square size={14} /> : <Play size={14} />}
              </button>
            </div>
          </div>
          <h3 
            className="text-lg font-semibold text-text-dim cursor-pointer hover:text-accent"
            onClick={() => navigate('/legion')}
          >
            LEGION
          </h3>
          <p className="text-2xl font-bold text-text mt-2">{status.legion.activeAgents}</p>
          <p className="text-sm text-text-dim mt-2">Active Agents</p>
        </div>

        {/* Artifact Card */}
        <div 
          className="card hover:glow-accent transition-all duration-300 cursor-pointer"
          onClick={() => navigate('/artifact')}
        >
          <div className="flex items-center justify-between mb-4">
            <Package className="text-accent" size={32} />
            <span className={getStatusClass(status.artifact.status)} />
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
        <div className="space-y-3 max-h-64 overflow-y-auto">
          {activity.map((item, idx) => (
            <div key={idx} className="flex items-start gap-3 p-3 bg-primary/50 rounded-lg">
              <span className={`${getActivityIcon(item.type)} mt-1`} />
              <div className="flex-1">
                <p className="text-sm text-text">{item.message}</p>
                <p className="text-xs text-text-dim mt-1">{item.time}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => navigate('/gladius')}
            className="p-4 bg-primary/50 hover:bg-accent/20 rounded-lg transition-colors text-center"
          >
            <Brain className="mx-auto mb-2 text-purple-400" size={24} />
            <p className="text-sm">Chat with GLADIUS</p>
          </button>
          <button 
            onClick={() => navigate('/training')}
            className="p-4 bg-primary/50 hover:bg-accent/20 rounded-lg transition-colors text-center"
          >
            <Zap className="mx-auto mb-2 text-yellow-400" size={24} />
            <p className="text-sm">Start Training</p>
          </button>
          <button 
            onClick={() => navigate('/sentinel')}
            className="p-4 bg-primary/50 hover:bg-accent/20 rounded-lg transition-colors text-center"
          >
            <Shield className="mx-auto mb-2 text-blue-400" size={24} />
            <p className="text-sm">Run Security Scan</p>
          </button>
          <button 
            onClick={() => navigate('/settings')}
            className="p-4 bg-primary/50 hover:bg-accent/20 rounded-lg transition-colors text-center"
          >
            <Terminal className="mx-auto mb-2 text-green-400" size={24} />
            <p className="text-sm">System Settings</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
