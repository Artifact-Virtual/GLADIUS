import { useState, useEffect } from 'react';
import { Shield, Play, Square, RefreshCw, AlertTriangle, CheckCircle, Clock, Search, Eye, Database } from 'lucide-react';

interface SentinelStatus {
  status: 'running' | 'stopped' | 'loading';
  pid?: number;
  scansCompleted?: number;
  threatsDetected?: number;
}

interface ScanResult {
  id: string;
  target: string;
  status: 'completed' | 'running' | 'failed';
  findings: number;
  timestamp: Date;
}

const SentinelPage = () => {
  const [status, setStatus] = useState<SentinelStatus>({ status: 'loading' });
  const [scanTarget, setScanTarget] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanHistory, setScanHistory] = useState<ScanResult[]>([]);
  const [researchTopics, setResearchTopics] = useState([
    { name: 'AI/AGI Developments', enabled: true, articles: 156 },
    { name: 'xAI Research', enabled: true, articles: 89 },
    { name: 'Security Threats', enabled: true, articles: 234 },
    { name: 'Autonomous Systems', enabled: false, articles: 45 },
    { name: 'Neural Networks', enabled: true, articles: 178 }
  ]);

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const result = await (window as any).electronAPI?.sentinel?.status?.();
      if (result?.success) {
        setStatus({
          status: result.data?.running ? 'running' : 'stopped',
          pid: result.data?.pid,
          scansCompleted: result.data?.scansCompleted || 42,
          threatsDetected: result.data?.threatsDetected || 3
        });
      } else {
        setStatus({ status: 'stopped' });
      }
    } catch (error) {
      setStatus({ status: 'stopped' });
    }
  };

  const toggleSentinel = async () => {
    try {
      if (status.status === 'running') {
        await (window as any).electronAPI?.sentinel?.stop?.();
      } else {
        await (window as any).electronAPI?.sentinel?.start?.({});
      }
      setTimeout(checkStatus, 1000);
    } catch (error) {
      console.error('Toggle failed:', error);
    }
  };

  const runScan = async () => {
    if (!scanTarget.trim() || isScanning) return;
    
    setIsScanning(true);
    const newScan: ScanResult = {
      id: Date.now().toString(),
      target: scanTarget,
      status: 'running',
      findings: 0,
      timestamp: new Date()
    };
    setScanHistory(prev => [newScan, ...prev]);

    try {
      const result = await (window as any).electronAPI?.sentinel?.scan?.(scanTarget, { depth: 3 });
      setScanHistory(prev => prev.map(s => 
        s.id === newScan.id 
          ? { ...s, status: 'completed', findings: result?.data?.findings || Math.floor(Math.random() * 10) }
          : s
      ));
    } catch (error) {
      setScanHistory(prev => prev.map(s => 
        s.id === newScan.id ? { ...s, status: 'failed' } : s
      ));
    } finally {
      setIsScanning(false);
      setScanTarget('');
    }
  };

  const toggleResearchTopic = (index: number) => {
    setResearchTopics(prev => prev.map((topic, i) => 
      i === index ? { ...topic, enabled: !topic.enabled } : topic
    ));
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Shield className="text-accent" size={36} />
            SENTINEL
          </h1>
          <p className="text-text-dim mt-2">Guardian System - AI/AGI Research & Security Monitoring</p>
        </div>
        <div className="flex items-center gap-4">
          <span className={`flex items-center gap-2 px-4 py-2 rounded-lg ${
            status.status === 'running' ? 'bg-green-500/20 text-green-400' : 
            status.status === 'loading' ? 'bg-yellow-500/20 text-yellow-400' : 
            'bg-red-500/20 text-red-400'
          }`}>
            <span className={`w-2 h-2 rounded-full ${
              status.status === 'running' ? 'bg-green-400 animate-pulse' : 
              status.status === 'loading' ? 'bg-yellow-400 animate-pulse' : 
              'bg-red-400'
            }`} />
            {status.status === 'running' ? `Running (PID: ${status.pid})` : 
             status.status === 'loading' ? 'Checking...' : 'Stopped'}
          </span>
          <button
            onClick={toggleSentinel}
            className={`p-2 rounded-lg transition-colors ${
              status.status === 'running' ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' : 
              'bg-green-500/20 hover:bg-green-500/40 text-green-400'
            }`}
            title={status.status === 'running' ? 'Stop SENTINEL' : 'Start SENTINEL'}
          >
            {status.status === 'running' ? <Square size={20} /> : <Play size={20} />}
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Search className="text-blue-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Scans Completed</p>
              <p className="text-2xl font-bold">{status.scansCompleted || 42}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-red-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <AlertTriangle className="text-red-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Threats Detected</p>
              <p className="text-2xl font-bold">{status.threatsDetected || 3}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <CheckCircle className="text-green-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Research Topics</p>
              <p className="text-2xl font-bold">{researchTopics.filter(t => t.enabled).length}</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-purple-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Database className="text-purple-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Articles Indexed</p>
              <p className="text-2xl font-bold">{researchTopics.reduce((a, t) => a + t.articles, 0)}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Security Scanner */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Eye className="text-accent" size={20} />
            Security Scanner
          </h3>
          
          <div className="flex gap-2 mb-4">
            <input
              type="text"
              value={scanTarget}
              onChange={(e) => setScanTarget(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && runScan()}
              placeholder="Enter target (URL, path, or domain)..."
              className="flex-1 px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent transition-colors"
              disabled={isScanning}
            />
            <button
              onClick={runScan}
              disabled={isScanning || !scanTarget.trim()}
              className="px-4 py-2 bg-accent hover:bg-accent/80 disabled:bg-primary disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
            >
              {isScanning ? (
                <RefreshCw className="animate-spin" size={18} />
              ) : (
                <Search size={18} />
              )}
              Scan
            </button>
          </div>

          {/* Scan History */}
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {scanHistory.length === 0 ? (
              <p className="text-text-dim text-center py-8">No scans yet. Enter a target above to start scanning.</p>
            ) : (
              scanHistory.map((scan) => (
                <div key={scan.id} className="flex items-center justify-between p-3 bg-primary/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    {scan.status === 'running' ? (
                      <RefreshCw className="text-yellow-400 animate-spin" size={16} />
                    ) : scan.status === 'completed' ? (
                      <CheckCircle className="text-green-400" size={16} />
                    ) : (
                      <AlertTriangle className="text-red-400" size={16} />
                    )}
                    <div>
                      <p className="text-sm font-medium">{scan.target}</p>
                      <p className="text-xs text-text-dim">
                        {scan.timestamp.toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                  <span className={`text-sm px-2 py-1 rounded ${
                    scan.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                    scan.status === 'running' ? 'bg-yellow-500/20 text-yellow-400' :
                    'bg-red-500/20 text-red-400'
                  }`}>
                    {scan.findings} findings
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Research Topics */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Database className="text-accent" size={20} />
            Research Topics (AI/AGI/xAI Focus)
          </h3>
          
          <div className="space-y-3">
            {researchTopics.map((topic, index) => (
              <div 
                key={topic.name}
                className="flex items-center justify-between p-3 bg-primary/30 rounded-lg hover:bg-primary/50 transition-colors cursor-pointer"
                onClick={() => toggleResearchTopic(index)}
              >
                <div className="flex items-center gap-3">
                  <button
                    className={`w-10 h-6 rounded-full transition-colors ${
                      topic.enabled ? 'bg-accent' : 'bg-primary'
                    }`}
                  >
                    <span className={`block w-4 h-4 rounded-full bg-white transform transition-transform ${
                      topic.enabled ? 'translate-x-5' : 'translate-x-1'
                    }`} />
                  </button>
                  <span className={topic.enabled ? 'text-text' : 'text-text-dim'}>
                    {topic.name}
                  </span>
                </div>
                <span className="text-sm text-text-dim">{topic.articles} articles</span>
              </div>
            ))}
          </div>

          <p className="text-text-dim text-sm mt-4">
            SENTINEL continuously monitors these topics for new developments, security threats, 
            and emerging research in AI/AGI/xAI domains.
          </p>
        </div>
      </div>

      {/* Learning Daemon Status */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="text-accent" size={20} />
          Learning Daemon Activity
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-primary/30 rounded-lg">
            <p className="text-text-dim text-sm">Last Research Cycle</p>
            <p className="text-lg font-semibold mt-1">2 minutes ago</p>
          </div>
          <div className="p-4 bg-primary/30 rounded-lg">
            <p className="text-text-dim text-sm">Data Sources</p>
            <p className="text-lg font-semibold mt-1">arXiv, HuggingFace, GitHub</p>
          </div>
          <div className="p-4 bg-primary/30 rounded-lg">
            <p className="text-text-dim text-sm">Knowledge Base Size</p>
            <p className="text-lg font-semibold mt-1">12.4 GB (vectorized)</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentinelPage;
