// System Status Types
export interface SystemStatus {
  gladius: ModuleStatus;
  sentinel: ModuleStatus;
  legion: ModuleStatus;
  artifact: ModuleStatus;
}

export interface ModuleStatus {
  status: 'running' | 'stopped' | 'error' | 'unknown';
  uptime?: number;
  lastUpdate?: string;
  pid?: number;
  activeAgents?: number;
  error?: string;
}

// GLADIUS Types
export interface GladiusConfig {
  dataset?: string;
  metric?: string;
  epochs?: number;
  batchSize?: number;
}

export interface BenchmarkResult {
  metric: string;
  score: number;
  timestamp: string;
  details?: Record<string, any>;
}

export interface TrainingProgress {
  epoch: number;
  totalEpochs: number;
  loss: number;
  accuracy?: number;
  eta?: string;
}

// SENTINEL Types
export interface SentinelConfig {
  port?: number;
  logLevel?: 'debug' | 'info' | 'warning' | 'error';
}

export interface ScanConfig {
  target: string;
  depth?: number;
  profile?: 'quick' | 'standard' | 'deep';
}

export interface ScanResult {
  target: string;
  findings: Finding[];
  timestamp: string;
  duration: number;
}

export interface Finding {
  severity: 'critical' | 'high' | 'medium' | 'low' | 'info';
  type: string;
  description: string;
  location?: string;
  recommendation?: string;
}

// LEGION Types
export interface AgentConfig {
  name: string;
  type: string;
  role?: string;
}

export interface Agent {
  id: string;
  name: string;
  type: string;
  role: string;
  status: 'idle' | 'active' | 'deployed' | 'stopped';
  created: string;
  lastActive?: string;
}

export interface DeployConfig {
  target?: string;
  mode?: 'autonomous' | 'supervised' | 'manual';
}

// Artifact Types
export interface ArtifactFilter {
  type?: string;
  tag?: string;
}

export interface Artifact {
  id: string;
  name: string;
  type: string;
  description?: string;
  tags: string[];
  size: number;
  created: string;
  modified: string;
  path: string;
}

export interface ArtifactConfig {
  name: string;
  type: string;
  path: string;
  description?: string;
  tags?: string[];
}

// Log Types
export interface LogFile {
  name: string;
  path: string;
  size: number;
  modified: Date;
}

export interface LogStreamData {
  logName: string;
  line: string;
  timestamp: string;
}

// IPC Response Types
export interface IPCResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

// Navigation Types
export type Route = 
  | '/'
  | '/gladius'
  | '/sentinel'
  | '/legion'
  | '/artifact'
  | '/logs'
  | '/settings';

// Theme Types
export interface Theme {
  primary: string;
  secondary: string;
  accent: string;
  accentPurple: string;
  success: string;
  warning: string;
  error: string;
  text: string;
  textDim: string;
}

// Store Types
export interface AppState {
  systemStatus: SystemStatus;
  currentRoute: Route;
  theme: Theme;
  updateSystemStatus: (status: Partial<SystemStatus>) => void;
  setRoute: (route: Route) => void;
}
