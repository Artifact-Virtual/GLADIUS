
export enum SwarmState {
  SLEEPING = 'SLEEPING',
  LEARNING = 'LEARNING',
  INTERACTING = 'INTERACTING'
}

export enum AIEngineType {
  GEMINI = 'GEMINI',
  LLAMA = 'LLAMA',      // GLADIUS native via llama.cpp
  GLADIUS = 'GLADIUS'   // Alias for LLAMA (native)
}

export interface Particle {
  x: number;
  y: number;
  vx: number;
  vy: number;
  ax: number;
  ay: number;
  size: number;
  color: string;
  originalColor: { r: number, g: number, b: number };
  life: number;
}

export interface SwarmParams {
  drag: number;
  cohesion: number;
  speed: number;
  turbulence: number;
  mouseForce: number;
  bloom: number;
  thinkingEnergy: number;
  audioAmplitude: number;
}

export interface AISettings {
  engine: AIEngineType;
  llamaEndpoint: string;
  llamaModelPath: string;
  gladiusApiUrl?: string;  // For system status polling
}

// GLADIUS System Metrics for HUD display
export interface GladiusHUDMetrics {
  modelName: string;
  modelVersion: string;
  parameterCount: number;
  particleCount: number;
  vectorCount: number;
  trainingProgress: number;
  epochsCompleted: number;
  currentLoss: number;
  tokensProcessed: number;
  inferenceLatencyMs: number;
  tokensPerSecond: number;
  memoryUsageMB: number;
  cpuUsage: number;
  gpuAvailable: boolean;
  uptime: number;
  modulesActive: string[];
}
