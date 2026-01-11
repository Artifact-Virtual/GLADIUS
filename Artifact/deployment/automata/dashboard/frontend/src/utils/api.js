import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
const INFRA_API_URL = import.meta.env.VITE_INFRA_API_URL || 'http://localhost:7000';

// Create axios instance for Automata API
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Create axios instance for Infra API (no auth required currently)
const infraApi = axios.create({
  baseURL: INFRA_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API Methods
export const authAPI = {
  login: (username, password) => 
    api.post('/auth/login', { username, password }),
  verify: () => 
    api.get('/auth/verify'),
};

export const statusAPI = {
  getStatus: () => 
    api.get('/status'),
  start: () => 
    api.post('/status/start'),
  stop: () => 
    api.post('/status/stop'),
};

export const configAPI = {
  getConfig: () => 
    api.get('/config'),
  updateConfig: (key, value) => 
    api.put('/config', { key, value }),
  getPlatforms: () => 
    api.get('/config/platforms'),
};

export const socialAPI = {
  getPosts: (platform) => 
    api.get('/social/posts', { params: { platform } }),
  createPost: (data) => 
    api.post('/social/post', data),
  cancelPost: (postId) => 
    api.delete(`/social/post/${postId}`),
};

export const analyticsAPI = {
  getAnalytics: () => 
    api.get('/analytics'),
  getPlatformAnalytics: (platform) => 
    api.get(`/analytics/social/${platform}`),
};

export const erpAPI = {
  triggerSync: (system, entityType) => 
    api.post('/erp/sync', { system, entity_type: entityType }),
};

// Infra API Methods (Market Data, Assets, Portfolios)
export const infraAPI = {
  // Markets
  getMarkets: () => infraApi.get('/markets'),
  createMarket: (data) => infraApi.post('/markets', data),
  
  // Assets
  getAssets: () => infraApi.get('/assets'),
  createAsset: (data) => infraApi.post('/assets', data),
  
  // Portfolios
  getPortfolios: () => infraApi.get('/portfolios'),
  getPortfolio: (id) => infraApi.get(`/portfolios/${id}`),
  createPortfolio: (data) => infraApi.post('/portfolios', data),
  
  // Prices
  ingestPrice: (data) => infraApi.post('/prices', data),
  
  // Health check
  health: () => infraApi.get('/docs').then(() => ({ status: 'ok' })).catch(() => ({ status: 'down' })),
};

// Service Health Checks
export const healthAPI = {
  checkInfra: async () => {
    try {
      await infraApi.get('/docs');
      return { service: 'infra', status: 'up', port: 7000 };
    } catch {
      return { service: 'infra', status: 'down', port: 7000 };
    }
  },
  checkDashboard: async () => {
    try {
      await api.get('/health');
      return { service: 'dashboard', status: 'up', port: 5000 };
    } catch {
      return { service: 'dashboard', status: 'down', port: 5000 };
    }
  },
  checkAll: async () => {
    const [infra, dashboard] = await Promise.all([
      healthAPI.checkInfra(),
      healthAPI.checkDashboard(),
    ]);
    return { infra, dashboard, timestamp: new Date().toISOString() };
  },
};

export default api;
