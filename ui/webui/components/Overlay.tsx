
import React, { useState } from 'react';
import { SwarmState, AIEngineType, AISettings, GladiusHUDMetrics } from '../types';
import StateSelector from './StateSelector';

interface OverlayProps {
  currentState: SwarmState;
  onStateChange: (state: SwarmState) => void;
  isStarted: boolean;
  onStart: () => void;
  transcriptions?: { text: string; isUser: boolean }[];
  isThinking?: boolean;
  settings: AISettings;
  onSettingsChange: (s: AISettings) => void;
  hudMetrics?: GladiusHUDMetrics;
  isBackendConnected?: boolean;
}

// Format large numbers with K/M/B suffix
const formatNumber = (n: number): string => {
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(1) + 'K';
  return n.toString();
};

const Overlay: React.FC<OverlayProps> = ({ 
  currentState, onStateChange, isStarted, onStart, 
  transcriptions = [], isThinking = false, settings, onSettingsChange,
  hudMetrics, isBackendConnected = false
}) => {
  const [showSettings, setShowSettings] = useState(false);
  const [showMetrics, setShowMetrics] = useState(true);

  const triggerKeySelect = async () => {
    if ((window as any).aistudio?.openSelectKey) {
      await (window as any).aistudio.openSelectKey();
    } else {
      alert("Platform API Key manager not found. Ensure you are in the correct environment.");
    }
  };

  if (!isStarted) {
    return (
      <div className="absolute inset-0 z-50 flex items-center justify-center bg-black">
        <div className="max-w-2xl text-center px-6 animate-in fade-in duration-1000">
          <div className="mb-4 text-[10px] uppercase tracking-[0.5em] text-white/30">
            Artifact Virtual Enterprise
          </div>
          <h1 className="text-6xl md:text-8xl font-display font-bold mb-4 tracking-tighter bg-clip-text text-transparent bg-gradient-to-b from-white to-white/20">
            GLADIUS
          </h1>
          <div className="text-sm text-white/40 mb-8 font-mono">
            v1.1 · {formatNumber(parseInt(process.env.MODEL_PARAMS || '71000000', 10))} Parameters · Native AGI
          </div>
          <button
            onClick={onStart}
            className="group relative px-16 py-6 border border-white/20 rounded-full transition-all hover:bg-white hover:text-black"
          >
            <span className="text-sm font-display uppercase tracking-[0.5em]">Initialize</span>
          </button>
        </div>
      </div>
    );
  }

  const showAIPanel = currentState !== SwarmState.SLEEPING;

  return (
    <div className="absolute inset-0 pointer-events-none flex flex-col justify-between p-8 md:p-12">
      {/* Settings Modal */}
      {showSettings && (
        <div className="absolute inset-0 z-[60] flex items-center justify-center bg-black/80 backdrop-blur-xl pointer-events-auto">
          <div className="bg-white/5 border border-white/10 p-10 rounded-3xl w-full max-w-lg">
            <h3 className="text-2xl font-display mb-8">SYSTEM_CONFIG</h3>
            
            <div className="space-y-6">
              <div>
                <label className="text-[10px] uppercase tracking-widest opacity-40 mb-2 block">Active Engine</label>
                <div className="flex gap-2">
                  {[AIEngineType.LLAMA, AIEngineType.GEMINI].map(e => (
                    <button
                      key={e}
                      onClick={() => onSettingsChange({ ...settings, engine: e })}
                      className={`flex-1 py-3 rounded-lg border transition-all ${settings.engine === e ? 'bg-white text-black border-white' : 'bg-black/40 border-white/10 opacity-50'}`}
                    >
                      {e === AIEngineType.LLAMA ? 'GLADIUS (Native)' : e}
                    </button>
                  ))}
                </div>
              </div>

              {settings.engine === AIEngineType.GEMINI && (
                <button 
                  onClick={triggerKeySelect}
                  className="w-full py-4 bg-cyan-500/20 border border-cyan-500/50 rounded-xl text-cyan-400 text-sm font-bold uppercase tracking-widest hover:bg-cyan-500/30 transition-all"
                >
                  Manage Gemini API Keys
                </button>
              )}

              {(settings.engine === AIEngineType.LLAMA || settings.engine === AIEngineType.GLADIUS) && (
                <div className="space-y-4">
                  <div>
                    <label className="text-[10px] uppercase tracking-widest opacity-40 mb-2 block">llama.cpp Endpoint</label>
                    <input 
                      type="text" 
                      value={settings.llamaEndpoint} 
                      onChange={(e) => onSettingsChange({...settings, llamaEndpoint: e.target.value})}
                      className="w-full bg-black/60 border border-white/10 rounded-lg p-3 text-sm font-mono focus:outline-none focus:border-white/40"
                    />
                  </div>
                  <div>
                    <label className="text-[10px] uppercase tracking-widest opacity-40 mb-2 block">Model Name</label>
                    <input 
                      type="text" 
                      value={settings.llamaModelPath} 
                      onChange={(e) => onSettingsChange({...settings, llamaModelPath: e.target.value})}
                      className="w-full bg-black/60 border border-white/10 rounded-lg p-3 text-sm font-mono focus:outline-none focus:border-white/40"
                    />
                  </div>
                  <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                    <div className="text-[10px] uppercase tracking-widest text-orange-400 mb-1">Native Mode</div>
                    <div className="text-xs text-white/60">
                      Using GLADIUS native {formatNumber(parseInt(process.env.MODEL_PARAMS || '71000000', 10))} model via llama.cpp server
                    </div>
                  </div>
                </div>
              )}
            </div>

            <button 
              onClick={() => setShowSettings(false)}
              className="mt-10 w-full py-4 bg-white/10 rounded-xl text-white text-xs uppercase tracking-widest hover:bg-white/20 transition-all"
            >
              Apply & Close
            </button>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-start">
        <div className="flex flex-col gap-1">
          <h2 className="text-xl font-display font-bold tracking-widest text-white/90">
            GLADIUS_1.1
          </h2>
          <div className="flex items-center gap-2">
            <span className={`text-[9px] uppercase tracking-[0.2em] px-2 py-0.5 rounded ${
              settings.engine === AIEngineType.GEMINI ? 'bg-indigo-500/20 text-indigo-400' : 'bg-orange-500/20 text-orange-400'
            }`}>
              CORE: {settings.engine === AIEngineType.LLAMA ? 'NATIVE' : settings.engine}
            </span>
            {hudMetrics?.gpuAvailable && (
              <span className="text-[9px] uppercase tracking-[0.2em] px-2 py-0.5 rounded bg-green-500/20 text-green-400">
                GPU
              </span>
            )}
            {/* Connection status indicator */}
            <span className={`text-[9px] uppercase tracking-[0.2em] px-2 py-0.5 rounded ${
              isBackendConnected 
                ? 'bg-green-500/20 text-green-400' 
                : 'bg-yellow-500/20 text-yellow-400'
            }`}>
              {isBackendConnected ? 'SYNCED' : 'STANDALONE'}
            </span>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          {showAIPanel && (
            <div className="text-right flex flex-col items-end">
              <div className="flex items-center gap-3 px-4 py-2 bg-white/5 border border-white/10 rounded-full">
                <span className={`w-1.5 h-1.5 rounded-full ${isThinking ? 'bg-cyan-400 animate-ping' : 'bg-white/20'}`}></span>
                <span className="text-[9px] font-bold uppercase tracking-[0.2em]">{isThinking ? 'Neural_Sync' : 'Monitoring'}</span>
              </div>
              <div className="max-w-sm mt-6 flex flex-col gap-3">
                {transcriptions.map((t, i) => (
                  <div key={i} className={`text-sm font-display tracking-tight leading-snug ${t.isUser ? 'text-white/30 italic text-xs' : 'text-white/80'}`}>
                    {t.isUser ? `> ${t.text}` : t.text}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          <button 
            onClick={() => setShowSettings(true)}
            className="pointer-events-auto p-3 bg-white/5 border border-white/10 rounded-full hover:bg-white/20 transition-all group"
          >
            <svg className="w-5 h-5 opacity-40 group-hover:opacity-100 group-hover:rotate-90 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
          </button>
        </div>
      </div>

      {/* Bottom section with state selector and metrics */}
      <div className="flex flex-col md:flex-row justify-between items-end gap-8">
        <div className="pointer-events-auto">
          <StateSelector currentState={currentState} onSelect={onStateChange} />
        </div>

        {/* Metrics HUD */}
        <div 
          className={`transition-opacity duration-500 ${showMetrics ? 'opacity-100' : 'opacity-20'}`}
          onMouseEnter={() => setShowMetrics(true)}
          onMouseLeave={() => setShowMetrics(true)}
        >
          <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-4 min-w-[280px]">
            <div className="flex justify-between items-center mb-3">
              <span className="text-[9px] uppercase tracking-widest text-white/40">System Telemetry</span>
              <div className="flex gap-1">
                {hudMetrics?.modulesActive?.map(m => (
                  <span key={m} className="text-[8px] px-1.5 py-0.5 bg-green-500/20 text-green-400 rounded">
                    {m.slice(0, 3)}
                  </span>
                ))}
                {!isBackendConnected && (
                  <span className="text-[8px] px-1.5 py-0.5 bg-yellow-500/20 text-yellow-400 rounded">
                    CACHED
                  </span>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-x-6 gap-y-2 text-[10px] font-mono">
              <div className="flex justify-between">
                <span className="text-white/40">PARAMS</span>
                <span className="text-white/80">{formatNumber(hudMetrics?.parameterCount || 71000000)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">MOTES</span>
                <span className="text-white/80">{formatNumber(hudMetrics?.particleCount || 15000)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">VECTORS</span>
                <span className="text-white/80">{formatNumber(hudMetrics?.vectorCount || 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">TOKENS</span>
                <span className="text-white/80">{formatNumber(hudMetrics?.tokensProcessed || 0)}</span>
              </div>
              
              {hudMetrics?.trainingProgress !== undefined && hudMetrics.trainingProgress > 0 && (
                <>
                  <div className="col-span-2 mt-2 pt-2 border-t border-white/10">
                    <div className="flex justify-between mb-1">
                      <span className="text-cyan-400">TRAINING</span>
                      <span className="text-cyan-400">{hudMetrics.trainingProgress.toFixed(1)}%</span>
                    </div>
                    <div className="w-full bg-white/10 rounded-full h-1">
                      <div 
                        className="bg-cyan-400 h-1 rounded-full transition-all duration-500"
                        style={{ width: `${hudMetrics.trainingProgress}%` }}
                      />
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">EPOCH</span>
                    <span className="text-white/80">{hudMetrics.epochsCompleted}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/40">LOSS</span>
                    <span className="text-white/80">{hudMetrics.currentLoss.toFixed(4)}</span>
                  </div>
                </>
              )}
              
              <div className="col-span-2 mt-2 pt-2 border-t border-white/10 flex justify-between">
                <span className="text-white/40">MEM</span>
                <span className="text-white/80">{hudMetrics?.memoryUsageMB || 0}MB</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">CPU</span>
                <span className="text-white/80">{(hudMetrics?.cpuUsage || 0).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-white/40">LATENCY</span>
                <span className="text-white/80">{hudMetrics?.inferenceLatencyMs || 0}ms</span>
              </div>
            </div>
            
            <div className="mt-3 pt-2 border-t border-white/10 flex justify-between text-[9px]">
              <span className="text-white/30">U_TIME</span>
              <span className="text-white/50 font-mono">{new Date().toISOString().slice(11,19)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Overlay;
