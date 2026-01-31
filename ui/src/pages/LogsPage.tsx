import { useState, useEffect, useRef } from 'react';
import { Terminal, Search, RefreshCw, Download, Trash2, Play, Square, Filter, FileText, AlertTriangle, Info, CheckCircle, XCircle } from 'lucide-react';

interface LogEntry {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'debug' | 'success';
  source: string;
  message: string;
}

interface LogFile {
  name: string;
  size: string;
  lines: number;
  modified: Date;
}

const LogsPage = () => {
  const [logFiles, setLogFiles] = useState<LogFile[]>([
    { name: 'gladius.log', size: '2.4 MB', lines: 45000, modified: new Date() },
    { name: 'sentinel.log', size: '1.1 MB', lines: 22000, modified: new Date() },
    { name: 'legion.log', size: '890 KB', lines: 15000, modified: new Date() },
    { name: 'training.log', size: '5.2 MB', lines: 98000, modified: new Date() },
    { name: 'syndicate.log', size: '456 KB', lines: 8500, modified: new Date() },
    { name: 'error.log', size: '234 KB', lines: 3200, modified: new Date() },
  ]);
  const [selectedLog, setSelectedLog] = useState<string>('gladius.log');
  const [logEntries, setLogEntries] = useState<LogEntry[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState<string>('all');
  const [autoScroll, setAutoScroll] = useState(true);
  const logContainerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadLogFiles();
    loadLogEntries(selectedLog);
  }, [selectedLog]);

  useEffect(() => {
    if (autoScroll && logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logEntries, autoScroll]);

  useEffect(() => {
    if (isStreaming) {
      const interval = setInterval(() => {
        const levels: LogEntry['level'][] = ['info', 'warning', 'error', 'debug', 'success'];
        const sources = ['GLADIUS', 'SENTINEL', 'LEGION', 'TRAINING', 'SYNDICATE'];
        const messages = [
          'Processing batch 1234/5000',
          'Model checkpoint saved',
          'Memory usage: 8.2 GB / 16 GB',
          'API request received',
          'Vectorization complete',
          'Agent task dispatched',
          'Market data updated',
          'Security scan initiated',
        ];
        
        const newEntry: LogEntry = {
          timestamp: new Date().toISOString(),
          level: levels[Math.floor(Math.random() * levels.length)],
          source: sources[Math.floor(Math.random() * sources.length)],
          message: messages[Math.floor(Math.random() * messages.length)],
        };
        
        setLogEntries(prev => [...prev.slice(-199), newEntry]);
      }, 1000);
      
      return () => clearInterval(interval);
    }
  }, [isStreaming]);

  const loadLogFiles = async () => {
    try {
      const result = await (window as any).electronAPI?.logs?.list?.();
      if (result?.success && result?.data?.logs) {
        setLogFiles(result.data.logs);
      }
    } catch (error) {
      console.error('Failed to load log files:', error);
    }
  };

  const loadLogEntries = async (logName: string) => {
    try {
      const result = await (window as any).electronAPI?.logs?.read?.(logName, 200);
      if (result?.success && result?.data?.entries) {
        setLogEntries(result.data.entries);
      } else {
        // Generate mock entries
        const levels: LogEntry['level'][] = ['info', 'warning', 'error', 'debug', 'success'];
        const mockEntries: LogEntry[] = Array.from({ length: 50 }, (_, i) => ({
          timestamp: new Date(Date.now() - i * 60000).toISOString(),
          level: levels[Math.floor(Math.random() * levels.length)],
          source: logName.replace('.log', '').toUpperCase(),
          message: `Log entry ${50 - i}: System operation completed successfully`,
        }));
        setLogEntries(mockEntries);
      }
    } catch (error) {
      console.error('Failed to load log entries:', error);
    }
  };

  const toggleStreaming = async () => {
    if (isStreaming) {
      await (window as any).electronAPI?.logs?.streamStop?.(selectedLog);
      setIsStreaming(false);
    } else {
      await (window as any).electronAPI?.logs?.streamStart?.(selectedLog);
      setIsStreaming(true);
    }
  };

  const clearLog = async (logName: string) => {
    try {
      await (window as any).electronAPI?.logs?.clear?.(logName);
      if (logName === selectedLog) {
        setLogEntries([]);
      }
    } catch (error) {
      console.error('Failed to clear log:', error);
    }
  };

  const downloadLog = (logName: string) => {
    const content = logEntries.map(e => 
      `[${e.timestamp}] [${e.level.toUpperCase()}] [${e.source}] ${e.message}`
    ).join('\n');
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = logName;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getLevelIcon = (level: string) => {
    switch (level) {
      case 'info': return <Info className="text-blue-400" size={14} />;
      case 'warning': return <AlertTriangle className="text-yellow-400" size={14} />;
      case 'error': return <XCircle className="text-red-400" size={14} />;
      case 'success': return <CheckCircle className="text-green-400" size={14} />;
      case 'debug': return <Terminal className="text-gray-400" size={14} />;
      default: return <Info className="text-gray-400" size={14} />;
    }
  };

  const getLevelClass = (level: string) => {
    switch (level) {
      case 'info': return 'text-blue-400';
      case 'warning': return 'text-yellow-400';
      case 'error': return 'text-red-400';
      case 'success': return 'text-green-400';
      case 'debug': return 'text-gray-500';
      default: return 'text-gray-400';
    }
  };

  const filteredEntries = logEntries.filter(entry => {
    const matchesSearch = entry.message.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          entry.source.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesLevel = levelFilter === 'all' || entry.level === levelFilter;
    return matchesSearch && matchesLevel;
  });

  return (
    <div className="space-y-6 animate-fade-in h-full flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Terminal className="text-accent" size={36} />
            System Logs
          </h1>
          <p className="text-text-dim mt-2">Real-time Log Monitoring and Analysis</p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={toggleStreaming}
            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition-colors ${
              isStreaming 
                ? 'bg-red-500/20 hover:bg-red-500/40 text-red-400' 
                : 'bg-green-500/20 hover:bg-green-500/40 text-green-400'
            }`}
          >
            {isStreaming ? <Square size={18} /> : <Play size={18} />}
            {isStreaming ? 'Stop Stream' : 'Live Stream'}
          </button>
          <button
            onClick={() => loadLogEntries(selectedLog)}
            className="p-2 bg-primary/50 hover:bg-primary rounded-lg transition-colors"
            title="Refresh"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent p-4">
          <Info className="text-blue-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Info Logs</p>
          <p className="font-bold">{logEntries.filter(e => e.level === 'info').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-yellow-500/10 to-transparent p-4">
          <AlertTriangle className="text-yellow-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Warnings</p>
          <p className="font-bold">{logEntries.filter(e => e.level === 'warning').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-red-500/10 to-transparent p-4">
          <XCircle className="text-red-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Errors</p>
          <p className="font-bold">{logEntries.filter(e => e.level === 'error').length}</p>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent p-4">
          <CheckCircle className="text-green-400 mb-2" size={20} />
          <p className="text-text-dim text-xs">Success</p>
          <p className="font-bold">{logEntries.filter(e => e.level === 'success').length}</p>
        </div>
      </div>

      <div className="flex gap-6 flex-1 min-h-0">
        {/* Log Files Sidebar */}
        <div className="w-64 card flex flex-col">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <FileText className="text-accent" size={20} />
            Log Files
          </h3>
          
          <div className="space-y-2 flex-1 overflow-y-auto">
            {logFiles.map((file) => (
              <div 
                key={file.name}
                onClick={() => setSelectedLog(file.name)}
                className={`p-3 rounded-lg cursor-pointer transition-all ${
                  selectedLog === file.name 
                    ? 'bg-accent/20 border border-accent/50' 
                    : 'bg-primary/30 hover:bg-primary/50'
                }`}
              >
                <p className="font-medium text-sm">{file.name}</p>
                <div className="flex justify-between text-xs text-text-dim mt-1">
                  <span>{file.size}</span>
                  <span>{file.lines.toLocaleString()} lines</span>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-4 pt-4 border-t border-primary/30 space-y-2">
            <button 
              onClick={() => downloadLog(selectedLog)}
              className="w-full py-2 bg-primary/50 hover:bg-primary rounded-lg flex items-center justify-center gap-2 text-sm"
            >
              <Download size={16} />
              Download
            </button>
            <button 
              onClick={() => clearLog(selectedLog)}
              className="w-full py-2 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded-lg flex items-center justify-center gap-2 text-sm"
            >
              <Trash2 size={16} />
              Clear Log
            </button>
          </div>
        </div>

        {/* Log Viewer */}
        <div className="flex-1 card flex flex-col">
          {/* Filters */}
          <div className="flex gap-4 mb-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-dim" size={18} />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search logs..."
                className="w-full pl-10 pr-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent transition-colors text-sm"
              />
            </div>
            <select
              value={levelFilter}
              onChange={(e) => setLevelFilter(e.target.value)}
              className="px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent text-sm"
            >
              <option value="all">All Levels</option>
              <option value="info">Info</option>
              <option value="warning">Warning</option>
              <option value="error">Error</option>
              <option value="success">Success</option>
              <option value="debug">Debug</option>
            </select>
            <label className="flex items-center gap-2 text-sm text-text-dim cursor-pointer">
              <input
                type="checkbox"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="w-4 h-4 rounded"
              />
              Auto-scroll
            </label>
          </div>

          {/* Log Content */}
          <div 
            ref={logContainerRef}
            className="flex-1 bg-black/40 rounded-lg p-4 font-mono text-xs overflow-y-auto"
          >
            {filteredEntries.length === 0 ? (
              <div className="text-center text-text-dim py-10">
                <Terminal className="mx-auto mb-3 opacity-50" size={48} />
                <p>No log entries found</p>
              </div>
            ) : (
              filteredEntries.map((entry, idx) => (
                <div key={idx} className="flex items-start gap-2 py-1 hover:bg-white/5 px-2 rounded">
                  <span className="text-text-dim whitespace-nowrap">
                    {new Date(entry.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="flex items-center gap-1">
                    {getLevelIcon(entry.level)}
                  </span>
                  <span className="text-accent whitespace-nowrap">[{entry.source}]</span>
                  <span className={getLevelClass(entry.level)}>{entry.message}</span>
                </div>
              ))
            )}
          </div>

          {/* Status Bar */}
          <div className="flex justify-between text-xs text-text-dim mt-2 pt-2 border-t border-primary/30">
            <span>Showing {filteredEntries.length} of {logEntries.length} entries</span>
            <span className="flex items-center gap-2">
              {isStreaming && (
                <>
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  Live streaming...
                </>
              )}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LogsPage;
