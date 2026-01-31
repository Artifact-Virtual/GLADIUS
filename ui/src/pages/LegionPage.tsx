import { useState, useEffect } from 'react';
import { Users, Play, Square, RefreshCw, Bot, Activity, Zap, CheckCircle, XCircle, Clock } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'idle' | 'error';
  tasksCompleted: number;
  lastActivity: Date;
}

interface LegionStatus {
  running: boolean;
  totalAgents: number;
  activeAgents: number;
}

const LegionPage = () => {
  const [status, setStatus] = useState<LegionStatus>({ running: false, totalAgents: 26, activeAgents: 0 });
  const [agents, setAgents] = useState<Agent[]>([
    { id: '1', name: 'DataCollector', type: 'data', status: 'idle', tasksCompleted: 234, lastActivity: new Date() },
    { id: '2', name: 'Analyzer', type: 'analysis', status: 'idle', tasksCompleted: 156, lastActivity: new Date() },
    { id: '3', name: 'Reporter', type: 'reporting', status: 'idle', tasksCompleted: 89, lastActivity: new Date() },
    { id: '4', name: 'MarketWatch', type: 'market', status: 'idle', tasksCompleted: 445, lastActivity: new Date() },
    { id: '5', name: 'SocialMonitor', type: 'social', status: 'idle', tasksCompleted: 1023, lastActivity: new Date() },
    { id: '6', name: 'ContentGenerator', type: 'content', status: 'idle', tasksCompleted: 67, lastActivity: new Date() },
    { id: '7', name: 'SecurityAuditor', type: 'security', status: 'idle', tasksCompleted: 312, lastActivity: new Date() },
    { id: '8', name: 'ResearchAssistant', type: 'research', status: 'idle', tasksCompleted: 178, lastActivity: new Date() },
  ]);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const result = await (window as any).electronAPI?.legion?.status?.();
      if (result?.success) {
        setStatus({
          running: result.data?.running || false,
          totalAgents: result.data?.totalAgents || 26,
          activeAgents: result.data?.activeAgents || 0
        });
      }
    } catch (error) {
      console.error('Legion status check failed:', error);
    }
  };

  const toggleLegion = async () => {
    try {
      if (status.running) {
        await (window as any).electronAPI?.legion?.stop?.();
      } else {
        await (window as any).electronAPI?.legion?.start?.({});
      }
      setTimeout(checkStatus, 1000);
    } catch (error) {
      console.error('Toggle failed:', error);
    }
  };

  const toggleAgent = (agentId: string) => {
    setAgents(prev => prev.map(agent => 
      agent.id === agentId 
        ? { ...agent, status: agent.status === 'active' ? 'idle' : 'active' }
        : agent
    ));
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'text-green-400 bg-green-500/20';
      case 'idle': return 'text-yellow-400 bg-yellow-500/20';
      case 'error': return 'text-red-400 bg-red-500/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'data': return '📊';
      case 'analysis': return '🔍';
      case 'reporting': return '📋';
      case 'market': return '📈';
      case 'social': return '🐦';
      case 'content': return '✍️';
      case 'security': return '🛡️';
      case 'research': return '🔬';
      default: return '🤖';
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Users className="text-accent" size={36} />
            LEGION
          </h1>
          <p className="text-text-dim mt-2">Multi-Agent Orchestration System - 26 Specialized Agents</p>
        </div>
        <div className="flex items-center gap-4">
          <span className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            status.running ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              status.running ? 'bg-green-400 animate-pulse' : 'bg-red-400'
            }`} />
            {status.running ? `Running (${status.activeAgents} active)` : 'Stopped'}
          </span>
          <button
            onClick={toggleLegion}
            className={`p-2 rounded-lg transition-colors ${
              status.running ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' : 
              'bg-green-500/20 hover:bg-green-500/40 text-green-400'
            }`}
            title={status.running ? 'Stop LEGION' : 'Start LEGION'}
          >
            {status.running ? <Square size={20} /> : <Play size={20} />}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Bot className="text-blue-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Total Agents</p>
              <p className="text-2xl font-bold">{status.totalAgents}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Activity className="text-green-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Active Agents</p>
              <p className="text-2xl font-bold">{agents.filter(a => a.status === 'active').length}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-purple-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Zap className="text-purple-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Tasks Completed</p>
              <p className="text-2xl font-bold">{agents.reduce((a, b) => a + b.tasksCompleted, 0)}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-orange-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Clock className="text-orange-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Uptime</p>
              <p className="text-2xl font-bold">99.9%</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent List */}
        <div className="lg:col-span-2 card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Bot className="text-accent" size={20} />
            Agent Registry
          </h3>
          
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {agents.map((agent) => (
              <div 
                key={agent.id}
                onClick={() => setSelectedAgent(agent)}
                className={`flex items-center justify-between p-4 rounded-lg cursor-pointer transition-all ${
                  selectedAgent?.id === agent.id 
                    ? 'bg-accent/20 border border-accent/50' 
                    : 'bg-primary/30 hover:bg-primary/50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getTypeIcon(agent.type)}</span>
                  <div>
                    <p className="font-medium">{agent.name}</p>
                    <p className="text-sm text-text-dim">{agent.type}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm text-text-dim">
                    {agent.tasksCompleted} tasks
                  </span>
                  <span className={`px-2 py-1 rounded text-xs ${getStatusColor(agent.status)}`}>
                    {agent.status}
                  </span>
                  <button
                    onClick={(e) => { e.stopPropagation(); toggleAgent(agent.id); }}
                    className={`p-1 rounded transition-colors ${
                      agent.status === 'active' 
                        ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' 
                        : 'bg-green-500/20 hover:bg-green-500/40 text-green-400'
                    }`}
                  >
                    {agent.status === 'active' ? <Square size={14} /> : <Play size={14} />}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Agent Details */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="text-accent" size={20} />
            Agent Details
          </h3>
          
          {selectedAgent ? (
            <div className="space-y-4">
              <div className="text-center py-4">
                <span className="text-5xl">{getTypeIcon(selectedAgent.type)}</span>
                <h4 className="text-xl font-bold mt-3">{selectedAgent.name}</h4>
                <span className={`inline-block px-3 py-1 rounded mt-2 ${getStatusColor(selectedAgent.status)}`}>
                  {selectedAgent.status}
                </span>
              </div>

              <div className="space-y-3">
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Type</p>
                  <p className="font-medium capitalize">{selectedAgent.type}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Tasks Completed</p>
                  <p className="font-medium">{selectedAgent.tasksCompleted}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Last Activity</p>
                  <p className="font-medium">{selectedAgent.lastActivity.toLocaleString()}</p>
                </div>
              </div>

              <div className="flex gap-2 pt-4">
                <button 
                  onClick={() => toggleAgent(selectedAgent.id)}
                  className={`flex-1 py-2 rounded-lg flex items-center justify-center gap-2 ${
                    selectedAgent.status === 'active'
                      ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400'
                      : 'bg-green-500/20 hover:bg-green-500/40 text-green-400'
                  }`}
                >
                  {selectedAgent.status === 'active' ? <Square size={16} /> : <Play size={16} />}
                  {selectedAgent.status === 'active' ? 'Stop' : 'Start'}
                </button>
                <button className="flex-1 py-2 bg-primary hover:bg-primary/80 rounded-lg flex items-center justify-center gap-2">
                  <RefreshCw size={16} />
                  Restart
                </button>
              </div>
            </div>
          ) : (
            <div className="text-center py-10 text-text-dim">
              <Bot className="mx-auto mb-3 opacity-50" size={48} />
              <p>Select an agent to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default LegionPage;
