import path from 'path';
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ mode }) => {
    const env = loadEnv(mode, '.', '');
    return {
      server: {
        port: 3000,
        host: '0.0.0.0',
      },
      plugins: [react()],
      define: {
        // Gemini API key - use either prefixed or non-prefixed
        'process.env.API_KEY': JSON.stringify(env.VITE_GEMINI_API_KEY || env.GEMINI_API_KEY),
        'process.env.GEMINI_API_KEY': JSON.stringify(env.VITE_GEMINI_API_KEY || env.GEMINI_API_KEY),
        // Model config for persistence
        'process.env.MODEL_NAME': JSON.stringify(env.VITE_MODEL_NAME || 'gladius1.1:71M-native'),
        'process.env.MODEL_VERSION': JSON.stringify(env.VITE_MODEL_VERSION || '1.1.0'),
        'process.env.MODEL_PARAMS': JSON.stringify(env.VITE_MODEL_PARAMS || '71000000'),
        'process.env.PERSIST_STATE': JSON.stringify(env.VITE_PERSIST_STATE || 'true')
      },
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '.'),
        }
      }
    };
});
