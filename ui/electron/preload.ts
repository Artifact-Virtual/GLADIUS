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
}

declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}

