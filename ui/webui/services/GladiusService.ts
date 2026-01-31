/**
 * GladiusService - Real-time connection to GLADIUS AI System
 * Fetches actual system state, metrics, and training status
 * Persists data to localStorage when deployed to Vercel without backend
 */

import { SwarmState } from '../types';

export interface GladiusSystemState {
  state: SwarmState;
  modelParams: number;  // 71M = 71000000
  vectorCount: number;  // From Hektor VDB
  trainingProgress: number;  // 0-100
  epochsCompleted: number;
  currentLoss: number;
  tokensProcessed: number;
  memoryUsageMB: number;
  cpuUsage: number;
  gpuAvailable: boolean;
  modulesActive: {
    sentinel: boolean;
    legion: boolean;
    syndicate: boolean;
    automata: boolean;
    hektor: boolean;
    training: boolean;
  };
  lastActivity: number;
}

export interface GladiusMetrics {
  inferenceLatencyMs: number;
  tokensPerSecond: number;
  contextLength: number;
  temperature: number;
  modelName: string;
  modelVersion: string;
}

// Storage key for persistence
const STORAGE_KEY = 'gladius_system_state';

// Get persisted model info from env or defaults
const getModelDefaults = () => ({
  modelParams: parseInt(process.env.MODEL_PARAMS || '71000000', 10),
  modelName: process.env.MODEL_NAME || 'gladius1.1:71M-native',
  modelVersion: process.env.MODEL_VERSION || '1.1.0'
});

const DEFAULT_STATE: GladiusSystemState = {
  state: SwarmState.SLEEPING,
  modelParams: getModelDefaults().modelParams,
  vectorCount: 0,
  trainingProgress: 0,
  epochsCompleted: 0,
  currentLoss: 0,
  tokensProcessed: 0,
  memoryUsageMB: 0,
  cpuUsage: 0,
  gpuAvailable: false,
  modulesActive: {
    sentinel: false,
    legion: false,
    syndicate: false,
    automata: false,
    hektor: false,
    training: false
  },
  lastActivity: Date.now()
};

export class GladiusService {
  private baseUrl: string;
  private pollingInterval: number | null = null;
  private currentState: GladiusSystemState;
  private isConnected: boolean = false;
  private connectionAttempts: number = 0;
  private maxConnectionAttempts: number = 3;
  
  public onStateUpdate: (state: GladiusSystemState) => void = () => {};
  public onMetricsUpdate: (metrics: GladiusMetrics) => void = () => {};
  public onError: (error: string) => void = () => {};
  public onConnectionChange: (connected: boolean) => void = () => {};

  constructor(baseUrl: string = 'http://localhost:7000') {
    this.baseUrl = baseUrl;
    // Load persisted state or use defaults
    this.currentState = this.loadPersistedState();
  }

  /**
   * Load state from localStorage if available
   */
  private loadPersistedState(): GladiusSystemState {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Merge with defaults to ensure all fields exist
        return {
          ...DEFAULT_STATE,
          ...parsed,
          // Always use env model params as source of truth
          modelParams: getModelDefaults().modelParams,
          lastActivity: Date.now()
        };
      }
    } catch (e) {
      console.warn('Failed to load persisted state:', e);
    }
    return { ...DEFAULT_STATE };
  }

  /**
   * Persist current state to localStorage
   */
  private persistState() {
    try {
      // Only persist important fields that should survive reload
      const toPersist = {
        modelParams: this.currentState.modelParams,
        vectorCount: this.currentState.vectorCount,
        epochsCompleted: this.currentState.epochsCompleted,
        tokensProcessed: this.currentState.tokensProcessed,
        trainingProgress: this.currentState.trainingProgress
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(toPersist));
    } catch (e) {
      console.warn('Failed to persist state:', e);
    }
  }

  /**
   * Start polling for system state
   */
  public startPolling(intervalMs: number = 2000) {
    if (this.pollingInterval) return;
    
    this.fetchState();  // Immediate first fetch
    this.pollingInterval = window.setInterval(() => {
      this.fetchState();
    }, intervalMs);
  }

  public stopPolling() {
    if (this.pollingInterval) {
      clearInterval(this.pollingInterval);
      this.pollingInterval = null;
    }
  }

  /**
   * Fetch current system state from GLADIUS backend
   */
  private async fetchState() {
    try {
      // Try to fetch from GLADIUS infra API
      const response = await fetch(`${this.baseUrl}/api/status`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(3000)
      });

      if (response.ok) {
        const data = await response.json();
        this.parseApiResponse(data);
        this.isConnected = true;
        this.connectionAttempts = 0;
        this.onConnectionChange(true);
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      this.connectionAttempts++;
      
      if (this.connectionAttempts >= this.maxConnectionAttempts) {
        // Backend not available - use persisted/default state
        if (this.isConnected) {
          this.isConnected = false;
          this.onConnectionChange(false);
          console.log('GLADIUS backend disconnected - using persisted state');
        }
        // Still emit state updates with persisted data
        this.onStateUpdate(this.currentState);
      }
    }
  }

  /**
   * Parse API response into GladiusSystemState
   */
  private parseApiResponse(data: any) {
    const newState: GladiusSystemState = {
      state: this.determineState(data),
      modelParams: data.model?.params || getModelDefaults().modelParams,
      vectorCount: data.hektor?.vector_count || this.currentState.vectorCount,
      trainingProgress: data.training?.progress || 0,
      epochsCompleted: data.training?.epochs || this.currentState.epochsCompleted,
      currentLoss: data.training?.loss || 0,
      tokensProcessed: data.training?.tokens || this.currentState.tokensProcessed,
      memoryUsageMB: data.system?.memory_mb || 0,
      cpuUsage: data.system?.cpu_percent || 0,
      gpuAvailable: data.system?.gpu_available || false,
      modulesActive: {
        sentinel: data.modules?.sentinel || false,
        legion: data.modules?.legion || false,
        syndicate: data.modules?.syndicate || false,
        automata: data.modules?.automata || false,
        hektor: data.modules?.hektor || false,
        training: data.training?.active || false
      },
      lastActivity: Date.now()
    };

    this.currentState = newState;
    this.persistState();  // Save to localStorage
    this.onStateUpdate(newState);

    // Also emit metrics if available
    if (data.inference) {
      const defaults = getModelDefaults();
      this.onMetricsUpdate({
        inferenceLatencyMs: data.inference.latency_ms || 0,
        tokensPerSecond: data.inference.tokens_per_second || 0,
        contextLength: data.inference.context_length || 2048,
        temperature: data.inference.temperature || 0.7,
        modelName: data.model?.name || defaults.modelName,
        modelVersion: data.model?.version || defaults.modelVersion
      });
    }
  }

  /**
   * Determine SwarmState from system data
   */
  private determineState(data: any): SwarmState {
    // Use direct state from API if provided
    if (data.state) {
      const stateStr = String(data.state).toUpperCase();
      if (stateStr === 'LEARNING' || stateStr === 'TRAINING') {
        return SwarmState.LEARNING;
      }
      if (stateStr === 'INTERACTING' || stateStr === 'ACTIVE') {
        return SwarmState.INTERACTING;
      }
      if (stateStr === 'SLEEPING' || stateStr === 'IDLE') {
        return SwarmState.SLEEPING;
      }
    }
    
    // Fallback: Training active = LEARNING
    if (data.training?.active) {
      return SwarmState.LEARNING;
    }
    
    // Fallback: Active inference/chat = INTERACTING
    if (data.inference?.active || data.chat?.active) {
      return SwarmState.INTERACTING;
    }
    
    // Any module active = INTERACTING
    if (data.modules?.sentinel || data.modules?.syndicate || data.modules?.hektor) {
      return SwarmState.INTERACTING;
    }
    
    // System idle = SLEEPING
    return SwarmState.SLEEPING;
  }

  /**
   * Get scaled particle count based on model parameters
   * 71M params → scaled to reasonable particle count
   */
  public getScaledParticleCount(maxParticles: number = 50000): number {
    // Scale: 71M → base 15000, can go up with larger models
    const baseRatio = this.currentState.modelParams / 71000000;
    const scaled = Math.min(maxParticles, Math.floor(15000 * baseRatio));
    return Math.max(5000, scaled);  // Minimum 5000 particles
  }

  /**
   * Manually trigger state change (for UI controls)
   */
  public async triggerStateChange(targetState: SwarmState): Promise<boolean> {
    // If disconnected, just update local state
    if (!this.isConnected) {
      this.currentState.state = targetState;
      this.currentState.lastActivity = Date.now();
      this.onStateUpdate(this.currentState);
      return true;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/state`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: targetState })
      });
      
      if (response.ok) {
        this.currentState.state = targetState;
        this.currentState.lastActivity = Date.now();
        this.onStateUpdate(this.currentState);
        return true;
      }
    } catch (error) {
      // Fallback to local state change
      this.currentState.state = targetState;
      this.currentState.lastActivity = Date.now();
      this.onStateUpdate(this.currentState);
      return true;
    }
    return false;
  }

  /**
   * Start training via API
   */
  public async startTraining(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/training/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        this.currentState.state = SwarmState.LEARNING;
        this.currentState.modulesActive.training = true;
        this.currentState.lastActivity = Date.now();
        this.onStateUpdate(this.currentState);
        return true;
      }
    } catch (error) {
      this.onError(`Failed to start training: ${error}`);
    }
    return false;
  }

  /**
   * Stop training via API
   */
  public async stopTraining(): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/api/training/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (response.ok) {
        this.currentState.modulesActive.training = false;
        this.currentState.lastActivity = Date.now();
        this.onStateUpdate(this.currentState);
        return true;
      }
    } catch (error) {
      this.onError(`Failed to stop training: ${error}`);
    }
    return false;
  }

  /**
   * Update vector count (called when Hektor updates)
   */
  public updateVectorCount(count: number) {
    this.currentState.vectorCount = count;
    this.persistState();
    this.onStateUpdate(this.currentState);
  }

  public getCurrentState(): GladiusSystemState {
    return { ...this.currentState };
  }

  public isBackendConnected(): boolean {
    return this.isConnected;
  }

  public disconnect() {
    this.stopPolling();
  }
}

// Singleton instance
export const gladiusService = new GladiusService();
