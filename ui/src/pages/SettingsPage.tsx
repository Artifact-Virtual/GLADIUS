import { useState, useEffect } from 'react';
import { Settings, Save, RefreshCw, Server, Brain, Shield, Users, Database, Bell, Globe, Moon, Sun, Terminal, Power, Cpu, HardDrive } from 'lucide-react';

interface ModuleConfig {
  sentinel: boolean;
  legion: boolean;
  training: boolean;
  ui: boolean;
  twitter: boolean;
  syndicate: boolean;
}

interface SystemConfig {
  lightweightMode: boolean;
  autoStartTraining: boolean;
  preferGpu: boolean;
  fallbackToCpu: boolean;
}

interface GpuInfo {
  cuda_available: boolean;
  device_count: number;
  device_name: string | null;
  memory_total: number;
}

interface SystemStats {
  platform: string;
  cpus: number;
  totalMemory: number;
  freeMemory: number;
}

const SettingsPage = () => {
  const [isDarkMode, setIsDarkMode] = useState(true);
  const [gpuInfo, setGpuInfo] = useState<GpuInfo | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [modules, setModules] = useState<ModuleConfig>({
    sentinel: true,
    legion: false,
    training: false,
    ui: true,
    twitter: true,
    syndicate: true
  });
  const [systemConfig, setSystemConfig] = useState<SystemConfig>({
    lightweightMode: true,
    autoStartTraining: false,
    preferGpu: true,
    fallbackToCpu: true
  });
  const [llamaConfig, setLlamaConfig] = useState({
    serverUrl: 'http://localhost:8080',
    maxTokens: 2048,
    temperature: 0.7,
    contextLength: 4096
  });
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSettings();
    checkGpu();
    getSystemStats();
  }, []);

  const loadSettings = async () => {
    try {
      const result = await (window as any).electronAPI?.system?.getConfig?.();
      if (result?.success && result?.data) {
        if (result.data.modules) setModules(result.data.modules);
        if (result.data.system) setSystemConfig(result.data.system);
        if (result.data.llama) setLlamaConfig(result.data.llama);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkGpu = async () => {
    try {
      const result = await (window as any).electronAPI?.system?.checkGpu?.();
      if (result?.success) {
        setGpuInfo(result.data);
      }
    } catch (error) {
      console.error('GPU check failed:', error);
    }
  };

  const getSystemStats = async () => {
    try {
      const result = await (window as any).electronAPI?.system?.stats?.();
      if (result?.success) {
        setSystemStats(result.data);
      }
    } catch (error) {
      console.error('Failed to get system stats:', error);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    try {
      await (window as any).electronAPI?.system?.setConfig?.({
        modules,
        system: systemConfig,
        llama: llamaConfig
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setSaving(false);
    }
  };

  const startAllServices = async () => {
    try {
      await (window as any).electronAPI?.system?.startAll?.();
    } catch (error) {
      console.error('Failed to start services:', error);
    }
  };

  const stopAllServices = async () => {
    try {
      await (window as any).electronAPI?.system?.stopAll?.();
    } catch (error) {
      console.error('Failed to stop services:', error);
    }
  };

  const toggleModule = (module: keyof ModuleConfig) => {
    setModules(prev => ({ ...prev, [module]: !prev[module] }));
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold gradient-text flex items-center gap-3">
            <Settings className="text-accent" size={36} />
            Settings
          </h1>
          <p className="text-text-dim mt-2">Configure Artifact Virtual Enterprise System</p>
        </div>
        <button
          onClick={saveSettings}
          disabled={saving}
          className={`px-6 py-3 rounded-lg flex items-center gap-2 transition-all ${
            saved ? 'bg-green-500 text-white' : 
            saving ? 'bg-primary cursor-not-allowed' :
            'bg-accent hover:bg-accent/80'
          }`}
        >
          {saving ? (
            <RefreshCw className="animate-spin" size={18} />
          ) : saved ? (
            <>✓ Saved</>
          ) : (
            <>
              <Save size={18} />
              Save Changes
            </>
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Module Toggles */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Server className="text-accent" size={20} />
            Module Configuration
          </h3>
          
          <div className="space-y-4">
            {[
              { key: 'sentinel' as const, name: 'SENTINEL', icon: Shield, desc: 'Guardian & Research System' },
              { key: 'legion' as const, name: 'LEGION', icon: Users, desc: 'Multi-Agent Orchestration' },
              { key: 'training' as const, name: 'Training', icon: Brain, desc: 'Auto-start training pipeline' },
              { key: 'ui' as const, name: 'Electron UI', icon: Globe, desc: 'Desktop interface' },
              { key: 'twitter' as const, name: 'Twitter Agent', icon: Bell, desc: 'Autonomous social engagement' },
              { key: 'syndicate' as const, name: 'SYNDICATE', icon: Database, desc: 'Market & news data' },
            ].map(({ key, name, icon: Icon, desc }) => (
              <div key={key} className="flex items-center justify-between p-4 bg-primary/30 rounded-lg">
                <div className="flex items-center gap-3">
                  <Icon className="text-accent" size={20} />
                  <div>
                    <p className="font-medium">{name}</p>
                    <p className="text-sm text-text-dim">{desc}</p>
                  </div>
                </div>
                <button
                  onClick={() => toggleModule(key)}
                  className={`w-12 h-6 rounded-full transition-colors ${
                    modules[key] ? 'bg-accent' : 'bg-primary'
                  }`}
                >
                  <span className={`block w-5 h-5 rounded-full bg-white transform transition-transform ${
                    modules[key] ? 'translate-x-6' : 'translate-x-0.5'
                  }`} />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* System Settings */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Terminal className="text-accent" size={20} />
            System Settings
          </h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-primary/30 rounded-lg">
              <div>
                <p className="font-medium">Lightweight Mode</p>
                <p className="text-sm text-text-dim">Reduce resource usage for CPU-only machines</p>
              </div>
              <button
                onClick={() => setSystemConfig(prev => ({ ...prev, lightweightMode: !prev.lightweightMode }))}
                className={`w-12 h-6 rounded-full transition-colors ${
                  systemConfig.lightweightMode ? 'bg-accent' : 'bg-primary'
                }`}
              >
                <span className={`block w-5 h-5 rounded-full bg-white transform transition-transform ${
                  systemConfig.lightweightMode ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-primary/30 rounded-lg">
              <div>
                <p className="font-medium">Prefer GPU</p>
                <p className="text-sm text-text-dim">Use CUDA when available</p>
              </div>
              <button
                onClick={() => setSystemConfig(prev => ({ ...prev, preferGpu: !prev.preferGpu }))}
                className={`w-12 h-6 rounded-full transition-colors ${
                  systemConfig.preferGpu ? 'bg-accent' : 'bg-primary'
                }`}
              >
                <span className={`block w-5 h-5 rounded-full bg-white transform transition-transform ${
                  systemConfig.preferGpu ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-primary/30 rounded-lg">
              <div>
                <p className="font-medium">CPU Fallback</p>
                <p className="text-sm text-text-dim">Auto-fallback when GPU unavailable</p>
              </div>
              <button
                onClick={() => setSystemConfig(prev => ({ ...prev, fallbackToCpu: !prev.fallbackToCpu }))}
                className={`w-12 h-6 rounded-full transition-colors ${
                  systemConfig.fallbackToCpu ? 'bg-accent' : 'bg-primary'
                }`}
              >
                <span className={`block w-5 h-5 rounded-full bg-white transform transition-transform ${
                  systemConfig.fallbackToCpu ? 'translate-x-6' : 'translate-x-0.5'
                }`} />
              </button>
            </div>

            <div className="flex items-center justify-between p-4 bg-primary/30 rounded-lg">
              <div>
                <p className="font-medium">Dark Mode</p>
                <p className="text-sm text-text-dim">UI theme preference</p>
              </div>
              <button
                onClick={() => setIsDarkMode(!isDarkMode)}
                className={`w-12 h-6 rounded-full transition-colors ${
                  isDarkMode ? 'bg-accent' : 'bg-primary'
                }`}
              >
                <span className={`block w-5 h-5 rounded-full bg-white transform transition-transform flex items-center justify-center ${
                  isDarkMode ? 'translate-x-6' : 'translate-x-0.5'
                }`}>
                  {isDarkMode ? <Moon size={10} className="text-primary" /> : <Sun size={10} className="text-primary" />}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* llama.cpp Configuration */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Brain className="text-accent" size={20} />
            llama.cpp Configuration (Native Inference)
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm text-text-dim mb-2">Server URL</label>
              <input
                type="text"
                value={llamaConfig.serverUrl}
                onChange={(e) => setLlamaConfig(prev => ({ ...prev, serverUrl: e.target.value }))}
                className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="block text-sm text-text-dim mb-2">Max Tokens</label>
              <input
                type="number"
                value={llamaConfig.maxTokens}
                onChange={(e) => setLlamaConfig(prev => ({ ...prev, maxTokens: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="block text-sm text-text-dim mb-2">Temperature: {llamaConfig.temperature}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={llamaConfig.temperature}
                onChange={(e) => setLlamaConfig(prev => ({ ...prev, temperature: parseFloat(e.target.value) }))}
                className="w-full"
              />
            </div>
            <div>
              <label className="block text-sm text-text-dim mb-2">Context Length</label>
              <input
                type="number"
                value={llamaConfig.contextLength}
                onChange={(e) => setLlamaConfig(prev => ({ ...prev, contextLength: parseInt(e.target.value) }))}
                className="w-full px-4 py-2 bg-primary/50 border border-primary rounded-lg focus:outline-none focus:border-accent"
              />
            </div>
          </div>
        </div>

        {/* System Info */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <HardDrive className="text-accent" size={20} />
            System Information
          </h3>
          
          <div className="space-y-3">
            <div className="p-3 bg-primary/30 rounded-lg">
              <p className="text-text-dim text-sm">Platform</p>
              <p className="font-medium capitalize">{systemStats?.platform || 'Loading...'}</p>
            </div>
            <div className="p-3 bg-primary/30 rounded-lg">
              <p className="text-text-dim text-sm">CPU Cores</p>
              <p className="font-medium">{systemStats?.cpus || 'Loading...'}</p>
            </div>
            <div className="p-3 bg-primary/30 rounded-lg">
              <p className="text-text-dim text-sm">Total Memory</p>
              <p className="font-medium">
                {systemStats ? `${(systemStats.totalMemory / (1024 * 1024 * 1024)).toFixed(1)} GB` : 'Loading...'}
              </p>
            </div>
            <div className="p-3 bg-primary/30 rounded-lg">
              <p className="text-text-dim text-sm">Free Memory</p>
              <p className="font-medium">
                {systemStats ? `${(systemStats.freeMemory / (1024 * 1024 * 1024)).toFixed(1)} GB` : 'Loading...'}
              </p>
            </div>
          </div>
        </div>

        {/* GPU Info */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Cpu className="text-accent" size={20} />
            GPU Status
          </h3>
          
          <div className="space-y-3">
            <div className="p-3 bg-primary/30 rounded-lg">
              <p className="text-text-dim text-sm">CUDA Available</p>
              <p className={`font-medium ${gpuInfo?.cuda_available ? 'text-green-400' : 'text-red-400'}`}>
                {gpuInfo?.cuda_available ? 'Yes' : 'No'}
              </p>
            </div>
            {gpuInfo?.cuda_available && (
              <>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">Device</p>
                  <p className="font-medium">{gpuInfo.device_name}</p>
                </div>
                <div className="p-3 bg-primary/30 rounded-lg">
                  <p className="text-text-dim text-sm">VRAM</p>
                  <p className="font-medium">
                    {(gpuInfo.memory_total / (1024 * 1024 * 1024)).toFixed(1)} GB
                  </p>
                </div>
              </>
            )}
            {!gpuInfo?.cuda_available && (
              <p className="text-text-dim text-sm">
                Training will use CPU mode. For faster training, consider using a CUDA-enabled GPU.
              </p>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Power className="text-accent" size={20} />
            Quick Actions
          </h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={startAllServices}
              className="p-4 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors text-center"
            >
              <Power className="mx-auto mb-2" size={24} />
              <p className="text-sm font-medium">Start All Services</p>
            </button>
            <button
              onClick={stopAllServices}
              className="p-4 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors text-center"
            >
              <Power className="mx-auto mb-2" size={24} />
              <p className="text-sm font-medium">Stop All Services</p>
            </button>
            <button
              onClick={checkGpu}
              className="p-4 bg-primary/50 hover:bg-primary rounded-lg transition-colors text-center"
            >
              <RefreshCw className="mx-auto mb-2" size={24} />
              <p className="text-sm font-medium">Refresh GPU Status</p>
            </button>
            <button
              onClick={loadSettings}
              className="p-4 bg-primary/50 hover:bg-primary rounded-lg transition-colors text-center"
            >
              <RefreshCw className="mx-auto mb-2" size={24} />
              <p className="text-sm font-medium">Reload Settings</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
