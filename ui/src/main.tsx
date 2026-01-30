import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles/index.css';

// Disable right-click context menu in production
if (process.env.NODE_ENV === 'production') {
  document.addEventListener('contextmenu', (e) => e.preventDefault());
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Log version info
console.log('GLADIUS Dashboard');
console.log('Version:', import.meta.env.VITE_APP_VERSION || '1.0.0');
console.log('Environment:', import.meta.env.MODE);
