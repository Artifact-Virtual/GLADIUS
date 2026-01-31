
import React, { useEffect, useRef, useState } from 'react';
import { SwarmEngine } from './services/SwarmEngine';
import { SwarmState, AIEngineType, AISettings, GladiusHUDMetrics } from './types';
import { audioEngine } from './services/AudioEngine';
import { LiveService } from './services/LiveService';
import { LlamaService } from './services/LlamaService';
import { gladiusService, GladiusSystemState } from './services/GladiusService';
import Overlay from './components/Overlay';

// Default GLADIUS configuration
const DEFAULT_SETTINGS: AISettings = {
  engine: AIEngineType.LLAMA,  // GLADIUS native by default
  llamaEndpoint: import.meta.env.VITE_LLAMA_ENDPOINT || 'http://localhost:8080',
  llamaModelPath: import.meta.env.VITE_MODEL_NAME || 'gladius1.1:71M-native',
  gladiusApiUrl: import.meta.env.VITE_GLADIUS_API || 'http://localhost:7001'
};

const App: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const engineRef = useRef<SwarmEngine | null>(null);
  const liveServiceRef = useRef<LiveService | null>(null);
  const llamaServiceRef = useRef<LlamaService | null>(null);
  
  const [currentState, setCurrentState] = useState<SwarmState>(SwarmState.SLEEPING);
  const stateRef = useRef<SwarmState>(SwarmState.SLEEPING);
  const [isStarted, setIsStarted] = useState(false);
  const [isThinking, setIsThinking] = useState(false);
  const [transcriptions, setTranscriptions] = useState<{text: string, isUser: boolean}[]>([]);
  const [isBackendConnected, setIsBackendConnected] = useState(false);
  
  const [settings, setSettings] = useState<AISettings>(DEFAULT_SETTINGS);
  
  // GLADIUS system metrics for HUD
  const [hudMetrics, setHudMetrics] = useState<GladiusHUDMetrics>({
    modelName: 'GLADIUS',
    modelVersion: '1.1.0',
    parameterCount: parseInt(import.meta.env.VITE_MODEL_PARAMS || '71000000', 10),
    particleCount: 15000,
    vectorCount: 0,
    trainingProgress: 0,
    epochsCompleted: 0,
    currentLoss: 0,
    tokensProcessed: 0,
    inferenceLatencyMs: 0,
    tokensPerSecond: 0,
    memoryUsageMB: 0,
    cpuUsage: 0,
    gpuAvailable: false,
    uptime: 0,
    modulesActive: []
  });

  // Update ref whenever state changes
  useEffect(() => {
    stateRef.current = currentState;
  }, [currentState]);

  // Connect to GLADIUS system for real-time state
  useEffect(() => {
    if (isStarted) {
      // Track connection status
      gladiusService.onConnectionChange = (connected: boolean) => {
        setIsBackendConnected(connected);
        if (!connected) {
          // Show friendly message when disconnected
          setTranscriptions(prev => {
            const last = prev[prev.length - 1];
            if (last?.text?.includes('Standalone mode')) return prev;
            return [...prev.slice(-2), { 
              text: 'Standalone mode active. Swarm operating autonomously.', 
              isUser: false 
            }];
          });
        }
      };

      // Start polling GLADIUS system status
      gladiusService.onStateUpdate = (sysState: GladiusSystemState) => {
        // Update swarm state based on system state
        if (sysState.state !== stateRef.current) {
          handleStateChange(sysState.state);
        }
        
        // Update particle count based on model params
        if (engineRef.current) {
          engineRef.current.setParticleCountFromModel(sysState.modelParams);
        }
        
        // Update HUD metrics
        const activeModules: string[] = [];
        if (sysState.modulesActive.sentinel) activeModules.push('SENTINEL');
        if (sysState.modulesActive.legion) activeModules.push('LEGION');
        if (sysState.modulesActive.syndicate) activeModules.push('SYNDICATE');
        if (sysState.modulesActive.automata) activeModules.push('AUTOMATA');
        if (sysState.modulesActive.hektor) activeModules.push('HEKTOR');
        if (sysState.modulesActive.training) activeModules.push('TRAINING');
        
        setHudMetrics(prev => ({
          ...prev,
          parameterCount: sysState.modelParams,
          particleCount: engineRef.current?.metrics.particleCount || 15000,
          vectorCount: sysState.vectorCount,
          trainingProgress: sysState.trainingProgress,
          epochsCompleted: sysState.epochsCompleted,
          currentLoss: sysState.currentLoss,
          tokensProcessed: sysState.tokensProcessed,
          memoryUsageMB: sysState.memoryUsageMB,
          cpuUsage: sysState.cpuUsage,
          gpuAvailable: sysState.gpuAvailable,
          modulesActive: activeModules
        }));
      };
      
      gladiusService.startPolling(2000);
      
      return () => {
        gladiusService.stopPolling();
      };
    }
  }, [isStarted]);

  // Inactivity monitor
  useEffect(() => {
    const interval = setInterval(() => {
      if (stateRef.current === SwarmState.INTERACTING) {
        let lastActivity = 0;
        if (settings.engine === AIEngineType.GEMINI && liveServiceRef.current) {
          lastActivity = liveServiceRef.current.lastActivityTime;
        } else if ((settings.engine === AIEngineType.LLAMA || settings.engine === AIEngineType.GLADIUS) && llamaServiceRef.current) {
          lastActivity = llamaServiceRef.current.getLastActivityTime();
        }

        if (lastActivity && Date.now() - lastActivity > 10000) {
          handleStateChange(SwarmState.LEARNING);
        }
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [settings.engine]);

  // Canvas and animation setup
  useEffect(() => {
    if (canvasRef.current && !engineRef.current) {
      engineRef.current = new SwarmEngine(canvasRef.current);
      
      // Set initial particle count based on GLADIUS model
      const modelParams = parseInt(import.meta.env.VITE_MODEL_PARAMS || '71000000', 10);
      engineRef.current.setParticleCountFromModel(modelParams);
      
      const animate = () => {
        engineRef.current?.update();
        engineRef.current?.draw();
        
        // Update HUD with swarm metrics
        if (engineRef.current) {
          const metrics = engineRef.current.getMetrics();
          setHudMetrics(prev => ({
            ...prev,
            particleCount: metrics.particleCount
          }));
        }
        
        requestAnimationFrame(animate);
      };
      animate();
      
      const handleResize = () => engineRef.current?.resize(window.innerWidth, window.innerHeight);
      const handleMouseMove = (e: MouseEvent) => engineRef.current?.setMouse(e.clientX, e.clientY);
      window.addEventListener('resize', handleResize);
      window.addEventListener('mousemove', handleMouseMove);
      return () => {
        window.removeEventListener('resize', handleResize);
        window.removeEventListener('mousemove', handleMouseMove);
      };
    }
  }, []);

  const handleStateChange = async (state: SwarmState) => {
    setCurrentState(state);
    stateRef.current = state;
    engineRef.current?.setState(state);
    audioEngine.updateState(state);

    if (state === SwarmState.SLEEPING) {
      liveServiceRef.current?.disconnect();
      llamaServiceRef.current?.disconnect();
      liveServiceRef.current = null;
      llamaServiceRef.current = null;
      setTranscriptions([]);
      return;
    }

    if (settings.engine === AIEngineType.GEMINI) {
      if (!liveServiceRef.current) {
        liveServiceRef.current = new LiveService();
        await liveServiceRef.current.connect();
      }
      
      liveServiceRef.current.onThinking = setIsThinking;
      liveServiceRef.current.onAmplitude = (amp) => engineRef.current?.setAIActivity(isThinking, amp);
      liveServiceRef.current.onTranscription = (text, isUser) => {
        setTranscriptions(prev => [...prev.slice(-3), { text, isUser }]);
      };
      liveServiceRef.current.onUserInputDetected = () => {
        if (stateRef.current === SwarmState.LEARNING) {
          handleStateChange(SwarmState.INTERACTING);
        }
      };

    } else {
      // LLAMA / GLADIUS native
      if (!llamaServiceRef.current) {
        llamaServiceRef.current = new LlamaService(settings);
        await llamaServiceRef.current.connect();
      }
      
      llamaServiceRef.current.onThinking = setIsThinking;
      llamaServiceRef.current.onAmplitude = (amp) => engineRef.current?.setAIActivity(isThinking, amp);
      llamaServiceRef.current.onTranscription = (text, isUser) => {
        setTranscriptions(prev => [...prev.slice(-3), { text, isUser }]);
      };
      llamaServiceRef.current.onUserInputDetected = () => {
        if (stateRef.current === SwarmState.LEARNING) {
          handleStateChange(SwarmState.INTERACTING);
        }
      };
    }
  };

  const handleStart = () => {
    setIsStarted(true);
    audioEngine.init();
    handleStateChange(SwarmState.SLEEPING);
  };

  return (
    <div className="relative w-full h-screen bg-black overflow-hidden select-none">
      <canvas ref={canvasRef} className="absolute inset-0 cursor-none" />
      <Overlay 
        currentState={currentState} 
        onStateChange={handleStateChange} 
        isStarted={isStarted} 
        onStart={handleStart}
        transcriptions={transcriptions}
        isThinking={isThinking}
        settings={settings}
        onSettingsChange={setSettings}
        hudMetrics={hudMetrics}
        isBackendConnected={isBackendConnected}
      />
      <div className="absolute inset-0 pointer-events-none shadow-[inset_0_0_200px_rgba(0,0,0,1)]"></div>
    </div>
  );
};

export default App;
