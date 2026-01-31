import { useState, useEffect } from 'react';
import { Brain, Play, Square, MessageSquare, Zap, Activity, Settings, Send, RefreshCw, Terminal } from 'lucide-react';

interface GladiusStatus {
  status: 'running' | 'stopped' | 'loading';
  model?: string;
  memory?: number;
  uptime?: number;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const GladiusPage = () => {
  const [status, setStatus] = useState<GladiusStatus>({ status: 'loading' });
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [benchmarkRunning, setBenchmarkRunning] = useState(false);
  const [benchmarkResults, setBenchmarkResults] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<'chat' | 'benchmark' | 'config'>('chat');

  useEffect(() => {
    checkStatus();
    const interval = setInterval(checkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const checkStatus = async () => {
    try {
      const result = await (window as any).electronAPI?.gladius?.status?.();
      if (result?.success) {
        setStatus({
          status: result.data?.status === 'ready' ? 'running' : 'stopped',
          model: 'gladius1.1:71M-native',
          memory: result.data?.memory || 0,
          uptime: result.data?.uptime || 0
        });
      } else {
        setStatus({ status: 'stopped' });
      }
    } catch (error) {
      console.error('Status check failed:', error);
      setStatus({ status: 'stopped' });
    }
  };

  const sendMessage = async () => {
    if (!chatInput.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: chatInput,
      timestamp: new Date()
    };
    setChatMessages(prev => [...prev, userMessage]);
    setChatInput('');
    setIsLoading(true);

    try {
      const result = await (window as any).electronAPI?.gladius?.interact?.(chatInput);
      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: result?.data?.response || result?.data?.output || 'No response received',
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Error: ${(error as Error).message}`,
        timestamp: new Date()
      };
      setChatMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const runBenchmark = async () => {
    setBenchmarkRunning(true);
    setBenchmarkResults(null);
    try {
      const result = await (window as any).electronAPI?.gladius?.benchmark?.({
        dataset: 'default',
        metric: 'all'
      });
      setBenchmarkResults(result?.data || { error: 'No results' });
    } catch (error) {
      setBenchmarkResults({ error: (error as Error).message });
    } finally {
      setBenchmarkRunning(false);
    }
  };

  const startTraining = async () => {
    try {
      await (window as any).electronAPI?.gladius?.train?.({
        epochs: 10,
        batchSize: 32
      });
    } catch (error) {
      console.error('Training failed:', error);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Brain className="text-accent" size={36} />
            GLADIUS
          </h1>
          <p className="text-text-dim mt-2">Native AI Engine - gladius1.1:71M</p>
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
            {status.status === 'running' ? 'Online' : status.status === 'loading' ? 'Checking...' : 'Offline'}
          </span>
          <button
            onClick={checkStatus}
            className="p-2 bg-primary/50 hover:bg-primary rounded-lg transition-colors"
            title="Refresh Status"
          >
            <RefreshCw size={20} />
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card bg-gradient-to-br from-purple-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Brain className="text-purple-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Model</p>
              <p className="text-lg font-semibold">71M params</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-blue-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Zap className="text-blue-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Architecture</p>
              <p className="text-lg font-semibold">Native GGUF</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-green-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Activity className="text-green-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Inference</p>
              <p className="text-lg font-semibold">llama.cpp</p>
            </div>
          </div>
        </div>
        <div className="card bg-gradient-to-br from-orange-500/10 to-transparent">
          <div className="flex items-center gap-3">
            <Terminal className="text-orange-400" size={24} />
            <div>
              <p className="text-text-dim text-sm">Tools</p>
              <p className="text-lg font-semibold">100+ routed</p>
            </div>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="flex gap-2 border-b border-primary/30 pb-2">
        <button
          onClick={() => setActiveTab('chat')}
          className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
            activeTab === 'chat' ? 'bg-accent/20 text-accent border-b-2 border-accent' : 'text-text-dim hover:text-text'
          }`}
        >
          <MessageSquare size={18} />
          Chat
        </button>
        <button
          onClick={() => setActiveTab('benchmark')}
          className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
            activeTab === 'benchmark' ? 'bg-accent/20 text-accent border-b-2 border-accent' : 'text-text-dim hover:text-text'
          }`}
        >
          <Activity size={18} />
          Benchmark
        </button>
        <button
          onClick={() => setActiveTab('config')}
          className={`px-4 py-2 rounded-t-lg transition-colors flex items-center gap-2 ${
            activeTab === 'config' ? 'bg-accent/20 text-accent border-b-2 border-accent' : 'text-text-dim hover:text-text'
          }`}
        >
          <Settings size={18} />
          Configuration
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'chat' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <MessageSquare className="text-accent" size={20} />
            Interactive Chat
          </h3>
          
          {/* Chat Messages */}
          <div className="h-80 overflow-y-auto mb-4 space-y-3 p-4 bg-primary/30 rounded-lg">
            {chatMessages.length === 0 ? (
              <div className="text-center text-text-dim py-10">
                <Brain className="mx-auto mb-3 opacity-50" size={48} />
                <p>Start a conversation with GLADIUS</p>
                <p className="text-sm mt-2">Test its intelligence and contextual understanding</p>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] px-4 py-2 rounded-lg ${
                      msg.role === 'user'
                        ? 'bg-accent/30 text-text'
                        : 'bg-primary text-text'
                    }`}
                  >
                    <p className="text-sm">{msg.content}</p>
                    <p className="text-xs text-text-dim mt-1">
                      {msg.timestamp.toLocaleTimeString()}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-primary px-4 py-2 rounded-lg">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 bg-accent rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Chat Input */}
          <div className="flex gap-2">
            <input
              type="text"
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask GLADIUS anything..."
              className="flex-1 px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent transition-colors"
              disabled={isLoading}
            />
            <button
              onClick={sendMessage}
              disabled={isLoading || !chatInput.trim()}
              className="px-4 py-2 bg-accent hover:bg-accent/80 disabled:bg-primary disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
            >
              <Send size={18} />
              Send
            </button>
          </div>
        </div>
      )}

      {activeTab === 'benchmark' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Activity className="text-accent" size={20} />
            Performance Benchmark
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-text-dim mb-4">
                Run comprehensive benchmarks to measure GLADIUS performance metrics including
                inference speed, memory usage, and accuracy.
              </p>
              <button
                onClick={runBenchmark}
                disabled={benchmarkRunning}
                className="px-6 py-3 bg-accent hover:bg-accent/80 disabled:bg-primary disabled:cursor-not-allowed rounded-lg transition-colors flex items-center gap-2"
              >
                {benchmarkRunning ? (
                  <>
                    <RefreshCw className="animate-spin" size={18} />
                    Running Benchmark...
                  </>
                ) : (
                  <>
                    <Play size={18} />
                    Run Benchmark
                  </>
                )}
              </button>
            </div>

            <div className="bg-primary/30 rounded-lg p-4">
              <h4 className="font-semibold mb-3">Results</h4>
              {benchmarkResults ? (
                <pre className="text-sm text-text-dim overflow-auto max-h-40">
                  {JSON.stringify(benchmarkResults, null, 2)}
                </pre>
              ) : (
                <p className="text-text-dim text-sm">No benchmark results yet. Run a benchmark to see metrics.</p>
              )}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'config' && (
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Settings className="text-accent" size={20} />
            Model Configuration
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-text-dim mb-2">Model Path</label>
                <input
                  type="text"
                  value="GLADIUS/models/native/gladius1.1-71M.gguf"
                  readOnly
                  className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-text-dim mb-2">Inference Backend</label>
                <select className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg">
                  <option value="llamacpp">llama.cpp (Native)</option>
                  <option value="cpu">CPU Only</option>
                  <option value="gpu">GPU Accelerated</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-text-dim mb-2">Temperature</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  defaultValue="0.7"
                  className="w-full"
                />
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-text-dim mb-2">Max Tokens</label>
                <input
                  type="number"
                  defaultValue="2048"
                  className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm text-text-dim mb-2">Context Length</label>
                <input
                  type="number"
                  defaultValue="4096"
                  className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg"
                />
              </div>
              <button
                onClick={startTraining}
                className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-lg transition-colors flex items-center justify-center gap-2"
              >
                <Zap size={18} />
                Start Training Pipeline
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default GladiusPage;
