import { contextBridge, ipcRenderer } from 'electron';

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
  // GLADIUS operations
  gladius: {
    status: () => ipcRenderer.invoke('gladius:status'),
    benchmark: (config: any) => ipcRenderer.invoke('gladius:benchmark', config),
    train: (config: any) => ipcRenderer.invoke('gladius:train', config),
    interact: (message: string) => ipcRenderer.invoke('gladius:interact', message),
  },

  // SENTINEL operations
  sentinel: {
    status: () => ipcRenderer.invoke('sentinel:status'),
    start: (config?: any) => ipcRenderer.invoke('sentinel:start', config),
    stop: () => ipcRenderer.invoke('sentinel:stop'),
    scan: (target: string, options?: any) => ipcRenderer.invoke('sentinel:scan', target, options),
  },

  // LEGION operations
  legion: {
    status: () => ipcRenderer.invoke('legion:status'),
    start: (config?: any) => ipcRenderer.invoke('legion:start', config),
    stop: () => ipcRenderer.invoke('legion:stop'),
    listAgents: () => ipcRenderer.invoke('legion:list-agents'),
    createAgent: (config: any) => ipcRenderer.invoke('legion:create-agent', config),
    deployAgent: (agentId: string, config?: any) => ipcRenderer.invoke('legion:deploy-agent', agentId, config),
    stopAgent: (processId: string) => ipcRenderer.invoke('legion:stop-agent', processId),
  },

  // Training operations
  training: {
    status: () => ipcRenderer.invoke('training:status'),
    start: (config: any) => ipcRenderer.invoke('training:start', config),
    stop: () => ipcRenderer.invoke('training:stop'),
    pause: () => ipcRenderer.invoke('training:pause'),
    resume: () => ipcRenderer.invoke('training:resume'),
    metrics: () => ipcRenderer.invoke('training:metrics'),
    onOutput: (callback: (data: any) => void) => {
      ipcRenderer.on('training:output', (_event, data) => callback(data));
    },
    onComplete: (callback: (data: any) => void) => {
      ipcRenderer.on('training:complete', (_event, data) => callback(data));
    },
    onError: (callback: (data: any) => void) => {
      ipcRenderer.on('training:error', (_event, data) => callback(data));
    },
    removeListeners: () => {
      ipcRenderer.removeAllListeners('training:output');
      ipcRenderer.removeAllListeners('training:complete');
      ipcRenderer.removeAllListeners('training:error');
    },
  },

  // Logs operations
  logs: {
    list: () => ipcRenderer.invoke('logs:list'),
    read: (logName: string, lines?: number) => ipcRenderer.invoke('logs:read', logName, lines),
    streamStart: (logName: string) => ipcRenderer.invoke('logs:stream-start', logName),
    streamStop: (logName: string) => ipcRenderer.invoke('logs:stream-stop', logName),
    clear: (logName: string) => ipcRenderer.invoke('logs:clear', logName),
    onStreamData: (callback: (data: any) => void) => {
      ipcRenderer.on('logs:stream-data', (_event, data) => callback(data));
    },
    onStreamError: (callback: (data: any) => void) => {
      ipcRenderer.on('logs:stream-error', (_event, data) => callback(data));
    },
    removeStreamListeners: () => {
      ipcRenderer.removeAllListeners('logs:stream-data');
      ipcRenderer.removeAllListeners('logs:stream-error');
    },
  },

  // Artifact operations
  artifact: {
    status: () => ipcRenderer.invoke('artifact:status'),
    list: (filter?: any) => ipcRenderer.invoke('artifact:list', filter),
    get: (artifactId: string) => ipcRenderer.invoke('artifact:get', artifactId),
    create: (config: any) => ipcRenderer.invoke('artifact:create', config),
    delete: (artifactId: string) => ipcRenderer.invoke('artifact:delete', artifactId),
    export: (artifactId: string, destination: string) => ipcRenderer.invoke('artifact:export', artifactId, destination),
  },

  // System operations
  system: {
    status: () => ipcRenderer.invoke('system:status'),
    stats: () => ipcRenderer.invoke('system:stats'),
    getConfig: () => ipcRenderer.invoke('system:config:get'),
    setConfig: (updates: any) => ipcRenderer.invoke('system:config:set', updates),
    checkGpu: () => ipcRenderer.invoke('system:gpu:check'),
    startAll: () => ipcRenderer.invoke('system:start-all'),
    stopAll: () => ipcRenderer.invoke('system:stop-all'),
  },
});

// Export types for TypeScript
export interface ElectronAPI {
  gladius: {
    status: () => Promise<any>;
    benchmark: (config: any) => Promise<any>;
    train: (config: any) => Promise<any>;
    interact: (message: string) => Promise<any>;
  };
  sentinel: {
    status: () => Promise<any>;
    start: (config?: any) => Promise<any>;
    stop: () => Promise<any>;
    scan: (target: string, options?: any) => Promise<any>;
  };
  legion: {
    status: () => Promise<any>;
    start: (config?: any) => Promise<any>;
    stop: () => Promise<any>;
    listAgents: () => Promise<any>;
    createAgent: (config: any) => Promise<any>;
    deployAgent: (agentId: string, config?: any) => Promise<any>;
    stopAgent: (processId: string) => Promise<any>;
  };
  training: {
    status: () => Promise<any>;
    start: (config: any) => Promise<any>;
    stop: () => Promise<any>;
    pause: () => Promise<any>;
    resume: () => Promise<any>;
    metrics: () => Promise<any>;
    onOutput: (callback: (data: any) => void) => void;
    onComplete: (callback: (data: any) => void) => void;
    onError: (callback: (data: any) => void) => void;
    removeListeners: () => void;
  };
  logs: {
    list: () => Promise<any>;
    read: (logName: string, lines?: number) => Promise<any>;
    streamStart: (logName: string) => Promise<any>;
    streamStop: (logName: string) => Promise<any>;
    clear: (logName: string) => Promise<any>;
    onStreamData: (callback: (data: any) => void) => void;
    onStreamError: (callback: (data: any) => void) => void;
    removeStreamListeners: () => void;
  };
  artifact: {
    status: () => Promise<any>;
    list: (filter?: any) => Promise<any>;
    get: (artifactId: string) => Promise<any>;
    create: (config: any) => Promise<any>;
    delete: (artifactId: string) => Promise<any>;
    export: (artifactId: string, destination: string) => Promise<any>;
  };
  system: {
    status: () => Promise<any>;
    stats: () => Promise<any>;
    getConfig: () => Promise<any>;
    setConfig: (updates: any) => Promise<any>;
    checkGpu: () => Promise<any>;
    startAll: () => Promise<any>;
    stopAll: () => Promise<any>;
  };
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

