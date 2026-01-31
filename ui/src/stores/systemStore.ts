import { create } from 'zustand';
import { AppState, SystemStatus, Route, Theme } from '../types';

const defaultTheme: Theme = {
  primary: '#0A0E27',
  secondary: '#1A1F3A',
  accent: '#00D9FF',
  accentPurple: '#9D4EDD',
  success: '#00FF87',
  warning: '#FFB800',
  error: '#FF3366',
  text: '#E8E9ED',
  textDim: '#9CA3AF',
};

const defaultSystemStatus: SystemStatus = {
  gladius: { status: 'unknown' },
  sentinel: { status: 'unknown' },
  legion: { status: 'unknown' },
  artifact: { status: 'unknown' },
};

export const useSystemStore = create<AppState>((set) => ({
  systemStatus: defaultSystemStatus,
  currentRoute: '/',
  theme: defaultTheme,

  updateSystemStatus: (status: Partial<SystemStatus>) =>
    set((state) => ({
      systemStatus: {
        ...state.systemStatus,
        ...status,
      },
    })),

  setRoute: (route: Route) =>
    set({ currentRoute: route }),
}));

// Helper hooks for specific modules
export const useGladiusStatus = () => useSystemStore((state) => state.systemStatus.gladius);
export const useSentinelStatus = () => useSystemStore((state) => state.systemStatus.sentinel);
export const useLegionStatus = () => useSystemStore((state) => state.systemStatus.legion);
export const useArtifactStatus = () => useSystemStore((state) => state.systemStatus.artifact);
export const useCurrentRoute = () => useSystemStore((state) => state.currentRoute);
export const useTheme = () => useSystemStore((state) => state.theme);
