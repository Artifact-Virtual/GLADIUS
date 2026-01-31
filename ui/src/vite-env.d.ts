/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_APP_VERSION: string;
  readonly MODE: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Electron API types
interface ElectronAPI {
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
    electron: ElectronAPI;
  }
}

export {};
