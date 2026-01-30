import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  Activity, Wifi, WifiOff, Settings, TrendingUp, 
  Send, Clock, CheckCircle, AlertCircle, Terminal,
  MessageSquare, Briefcase, MessageCircle, FileText,
  Twitter, Mail, PlayCircle, PauseCircle, RefreshCw,
  Plus, Search, Calendar, BarChart, Database
} from 'lucide-react';

interface PlatformStatus {
  name: string;
  icon: React.ReactNode;
  status: 'online' | 'offline' | 'degraded';
  uptime: string;
  metrics: { label: string; value: string }[];
  color: string;
}

interface ActivityItem {
  timestamp: string;
  platform: string;
  message: string;
  type: 'info' | 'success' | 'warning';
}

interface ResearchTask {
  id: string;
  topic: string;
  progress: number;
  eta: string;
  status: 'active' | 'queued' | 'completed';
}

interface ScheduledPost {
  time: string;
  platform: string;
  content: string;
  status: 'scheduled' | 'published' | 'failed';
}

interface ERPSystem {
  name: string;
  status: 'online' | 'offline' | 'degraded';
  lastSync: string;
  records: number;
  uptime: string;
}

export const ArtyControlPanel: React.FC = () => {
  const [platforms, setPlatforms] = useState<PlatformStatus[]>([
    {
      name: 'Discord',
      icon: <MessageSquare className="w-6 h-6" />,
      status: 'online',
      uptime: '72h 14m',
      metrics: [
        { label: 'Servers', value: '12' },
        { label: 'Users', value: '2,847' },
        { label: 'Messages/hr', value: '247' },
        { label: 'Latency', value: '45ms' },
      ],
      color: '#5865F2',
    },
    {
      name: 'LinkedIn',
      icon: <Briefcase className="w-6 h-6" />,
      status: 'online',
      uptime: '48h 22m',
      metrics: [
        { label: 'Connections', value: '847' },
        { label: 'Posts/day', value: '12' },
        { label: 'Engagement', value: '8.4%' },
        { label: 'Reach', value: '124k' },
      ],
      color: '#0A66C2',
    },
    {
      name: 'Telegram',
      icon: <MessageCircle className="w-6 h-6" />,
      status: 'online',
      uptime: '168h 7m',
      metrics: [
        { label: 'Chats', value: '45' },
        { label: 'Members', value: '1,234' },
        { label: 'Messages/hr', value: '89' },
        { label: 'Response Rate', value: '94%' },
      ],
      color: '#26A5E4',
    },
    {
      name: 'Notion',
      icon: <FileText className="w-6 h-6" />,
      status: 'online',
      uptime: '240h 33m',
      metrics: [
        { label: 'Workspaces', value: '3' },
        { label: 'Pages', value: '2,847' },
        { label: 'Updates/day', value: '47' },
        { label: 'Sync Delay', value: '2m' },
      ],
      color: '#000000',
    },
    {
      name: 'Twitter/X',
      icon: <Twitter className="w-6 h-6" />,
      status: 'offline',
      uptime: '12h ago',
      metrics: [
        { label: 'Followers', value: '2,456' },
        { label: 'Tweets/day', value: '8' },
        { label: 'Engagement', value: '12.3%' },
        { label: 'Impressions', value: '847k' },
      ],
      color: '#1DA1F2',
    },
    {
      name: 'Email SMTP',
      icon: <Mail className="w-6 h-6" />,
      status: 'online',
      uptime: '336h 12m',
      metrics: [
        { label: 'Sent Today', value: '847' },
        { label: 'Queue', value: '23' },
        { label: 'Success Rate', value: '99%' },
        { label: 'Open Rate', value: '23.4%' },
      ],
      color: '#EA4335',
    },
  ]);

  const [activities, setActivities] = useState<ActivityItem[]>([
    { timestamp: '14:32:18', platform: 'Discord', message: 'User @mike asked about training status', type: 'info' },
    { timestamp: '14:30:05', platform: 'LinkedIn', message: 'Posted tech article - Reach: 12.4k', type: 'success' },
    { timestamp: '14:28:42', platform: 'Telegram', message: 'New message in #general', type: 'info' },
    { timestamp: '14:25:15', platform: 'Notion', message: 'Rate limit approaching', type: 'warning' },
    { timestamp: '14:20:33', platform: 'Discord', message: 'Command executed: /help', type: 'success' },
  ]);

  const [researchTasks, setResearchTasks] = useState<ResearchTask[]>([
    { id: '1', topic: 'Market Analysis', progress: 82, eta: '12m', status: 'active' },
    { id: '2', topic: 'Tech Trends', progress: 67, eta: '23m', status: 'active' },
    { id: '3', topic: 'Competitor Watch', progress: 74, eta: '18m', status: 'active' },
    { id: '4', topic: 'Content Ideas', progress: 45, eta: '34m', status: 'active' },
    { id: '5', topic: 'Industry News', progress: 89, eta: '8m', status: 'active' },
  ]);

  const [scheduledPosts, setScheduledPosts] = useState<ScheduledPost[]>([
    { time: '15:00', platform: 'LinkedIn', content: 'AI Market Analysis Q1 2024', status: 'scheduled' },
    { time: '16:30', platform: 'Discord', content: 'Weekly update announcement', status: 'scheduled' },
    { time: '18:00', platform: 'Telegram', content: 'Feature release notes', status: 'scheduled' },
    { time: '19:15', platform: 'LinkedIn', content: 'Tech trends: Multimodal AI', status: 'scheduled' },
    { time: '21:00', platform: 'Email', content: 'Monthly newsletter', status: 'scheduled' },
  ]);

  const [erpSystems, setErpSystems] = useState<ERPSystem[]>([
    { name: 'SAP ERP', status: 'online', lastSync: '2h ago', records: 12847, uptime: '72h' },
    { name: 'Salesforce CRM', status: 'online', lastSync: '1h ago', records: 8456, uptime: '168h' },
    { name: 'Microsoft Dynamics', status: 'online', lastSync: '3h ago', records: 5234, uptime: '240h' },
    { name: 'Oracle NetSuite', status: 'degraded', lastSync: '5h ago', records: 3892, uptime: '48h' },
    { name: 'Workday HCM', status: 'online', lastSync: '2h ago', records: 2147, uptime: '336h' },
  ]);

  const [commandInput, setCommandInput] = useState('');
  const [commandHistory, setCommandHistory] = useState<string[]>([
    '/discord status',
    '/linkedin post article',
    '/telegram broadcast',
    '/twitter post (FAILED)',
    '/notion sync',
  ]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'online': return '#00FF87';
      case 'offline': return '#FF3366';
      case 'degraded': return '#FFB800';
      default: return '#9CA3AF';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'online': return <Wifi className="w-4 h-4" />;
      case 'offline': return <WifiOff className="w-4 h-4" />;
      case 'degraded': return <AlertCircle className="w-4 h-4" />;
      default: return <Activity className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-bg-primary text-text-primary p-6 space-y-6 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="w-6 h-6 text-status-online" />
          <h2 className="text-2xl font-bold">ARTY Control Panel</h2>
          <span className="px-3 py-1 bg-status-online/20 text-status-online rounded-full text-sm font-mono">
            5/6 Platforms Active
          </span>
        </div>
        <div className="flex items-center space-x-2">
          <button className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors">
            <RefreshCw className="w-4 h-4" />
            <span>Refresh All</span>
          </button>
          <button className="px-4 py-2 bg-bg-accent hover:bg-bg-secondary rounded-lg flex items-center space-x-2 transition-colors">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Platform Status Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid grid-cols-3 gap-4"
      >
        {platforms.map((platform, index) => (
          <motion.div
            key={platform.name}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: index * 0.1 }}
            className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <div style={{ color: platform.color }}>{platform.icon}</div>
                <h3 className="font-semibold">{platform.name}</h3>
              </div>
              <div className="flex items-center space-x-1" style={{ color: getStatusColor(platform.status) }}>
                {getStatusIcon(platform.status)}
                <span className="text-xs font-mono uppercase">{platform.status}</span>
              </div>
            </div>
            
            <div className="text-sm text-text-secondary mb-3">
              Uptime: <span className="text-text-primary font-mono">{platform.uptime}</span>
            </div>

            <div className="grid grid-cols-2 gap-2 mb-3">
              {platform.metrics.map((metric) => (
                <div key={metric.label} className="text-xs">
                  <div className="text-text-secondary">{metric.label}</div>
                  <div className="text-text-primary font-mono">{metric.value}</div>
                </div>
              ))}
            </div>

            <div className="flex space-x-2">
              <button className="flex-1 px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors">
                Configure
              </button>
              <button className="flex-1 px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors">
                {platform.status === 'online' ? 'Disconnect' : 'Connect'}
              </button>
              <button className="flex-1 px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors">
                Analytics
              </button>
            </div>
          </motion.div>
        ))}
      </motion.div>

      {/* Command & Activity Section */}
      <div className="grid grid-cols-2 gap-6">
        {/* Command Interface */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <div className="flex items-center space-x-2 mb-3">
            <Terminal className="w-5 h-5 text-status-online" />
            <h3 className="text-lg font-semibold">Command Console</h3>
          </div>

          {/* Command Input */}
          <div className="bg-black/40 rounded p-3 mb-3">
            <div className="flex items-center space-x-2">
              <span className="text-status-online font-mono">{'>'}</span>
              <input
                type="text"
                value={commandInput}
                onChange={(e) => setCommandInput(e.target.value)}
                placeholder="Enter command..."
                className="flex-1 bg-transparent border-none outline-none text-text-primary font-mono text-sm"
              />
              <button className="px-3 py-1 bg-status-online/20 hover:bg-status-online/30 text-status-online rounded text-xs transition-colors">
                <Send className="w-3 h-3" />
              </button>
            </div>
          </div>

          {/* Quick Commands */}
          <div className="mb-3">
            <div className="text-xs text-text-secondary mb-2">Quick Commands:</div>
            <div className="grid grid-cols-2 gap-2">
              <button className="px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors text-left">
                📢 Discord Broadcast
              </button>
              <button className="px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors text-left">
                📝 LinkedIn Post
              </button>
              <button className="px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors text-left">
                📨 Telegram Announce
              </button>
              <button className="px-2 py-1 bg-bg-accent hover:bg-bg-primary rounded text-xs transition-colors text-left">
                🔄 Sync All Platforms
              </button>
            </div>
          </div>

          {/* Command History */}
          <div>
            <div className="text-xs text-text-secondary mb-2">Command History:</div>
            <div className="bg-black/40 rounded p-2 h-32 overflow-y-auto font-mono text-xs space-y-1">
              {commandHistory.map((cmd, i) => (
                <div key={i} className="text-text-secondary">
                  <span className="text-status-online">{'>'}</span> {cmd}
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Activity Feed */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <Activity className="w-5 h-5 text-status-online" />
              <h3 className="text-lg font-semibold">Live Activity Feed</h3>
            </div>
            <div className="w-2 h-2 bg-status-online rounded-full animate-pulse" />
          </div>

          <div className="space-y-2 h-80 overflow-y-auto">
            {activities.map((activity, i) => (
              <div key={i} className="bg-bg-accent rounded p-2 text-sm">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-text-secondary font-mono text-xs">{activity.timestamp}</span>
                  <span className="text-xs font-semibold">{activity.platform}</span>
                </div>
                <div className="text-text-primary">{activity.message}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Research Engine */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
      >
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Search className="w-5 h-5 text-status-online" />
            <h3 className="text-lg font-semibold">Research Engine</h3>
            <span className="px-2 py-1 bg-status-online/20 text-status-online rounded text-xs font-mono">
              {researchTasks.length} Active
            </span>
          </div>
          <button className="px-3 py-1 bg-status-online/20 hover:bg-status-online/30 text-status-online rounded text-sm transition-colors flex items-center space-x-1">
            <Plus className="w-4 h-4" />
            <span>New Research</span>
          </button>
        </div>

        <div className="grid grid-cols-5 gap-3">
          {researchTasks.map((task) => (
            <div key={task.id} className="bg-bg-accent rounded p-3">
              <div className="text-sm font-semibold mb-2">{task.topic}</div>
              <div className="w-full bg-bg-primary rounded-full h-2 mb-2 overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${task.progress}%` }}
                  transition={{ duration: 0.5 }}
                  className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                />
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-text-secondary">{task.progress}%</span>
                <span className="text-text-secondary">ETA: {task.eta}</span>
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Publishing Queue & ERP */}
      <div className="grid grid-cols-2 gap-6">
        {/* Publishing Queue */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-5 h-5 text-status-online" />
              <h3 className="text-lg font-semibold">Publishing Queue</h3>
              <span className="px-2 py-1 bg-status-online/20 text-status-online rounded text-xs font-mono">
                {scheduledPosts.length} Scheduled
              </span>
            </div>
            <button className="px-3 py-1 bg-status-online/20 hover:bg-status-online/30 text-status-online rounded text-sm transition-colors flex items-center space-x-1">
              <Plus className="w-4 h-4" />
              <span>New Post</span>
            </button>
          </div>

          <div className="space-y-2 h-48 overflow-y-auto">
            {scheduledPosts.map((post, i) => (
              <div key={i} className="bg-bg-accent rounded p-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-mono">{post.time}</span>
                  <span className="text-xs text-text-secondary">{post.platform}</span>
                </div>
                <div className="text-sm text-text-primary truncate mb-1">{post.content}</div>
                <div className="flex items-center space-x-2">
                  <button className="px-2 py-0.5 bg-bg-secondary hover:bg-bg-primary rounded text-xs transition-colors">
                    Edit
                  </button>
                  <button className="px-2 py-0.5 bg-bg-secondary hover:bg-bg-primary rounded text-xs transition-colors">
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* ERP Systems */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-bg-secondary rounded-lg p-4 border border-bg-accent"
        >
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-status-online" />
              <h3 className="text-lg font-semibold">ERP Integrations</h3>
              <span className="px-2 py-1 bg-status-online/20 text-status-online rounded text-xs font-mono">
                {erpSystems.filter(s => s.status === 'online').length}/{erpSystems.length} Active
              </span>
            </div>
          </div>

          <div className="space-y-2 h-48 overflow-y-auto">
            {erpSystems.map((system, i) => (
              <div key={i} className="bg-bg-accent rounded p-2">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm font-semibold">{system.name}</span>
                  <div className="flex items-center space-x-1" style={{ color: getStatusColor(system.status) }}>
                    {getStatusIcon(system.status)}
                    <span className="text-xs font-mono uppercase">{system.status}</span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div>
                    <div className="text-text-secondary">Sync</div>
                    <div className="font-mono">{system.lastSync}</div>
                  </div>
                  <div>
                    <div className="text-text-secondary">Records</div>
                    <div className="font-mono">{system.records.toLocaleString()}</div>
                  </div>
                  <div>
                    <div className="text-text-secondary">Uptime</div>
                    <div className="font-mono">{system.uptime}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};
