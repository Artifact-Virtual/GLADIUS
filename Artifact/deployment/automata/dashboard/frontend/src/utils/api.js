import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
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

export default api;
