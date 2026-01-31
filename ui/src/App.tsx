import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { CosmicBackground } from './components/CosmicBackground';
import Sidebar from './components/Sidebar';
import { TrainingConsole } from './components/training/TrainingConsole';
import { TelemetryDashboard } from './components/telemetry/TelemetryDashboard';

// Import pages from existing structure
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const Training = React.lazy(() => import('./pages/Training'));
const Sentinel = React.lazy(() => import('./pages/SentinelPage'));
const Legion = React.lazy(() => import('./pages/LegionPage'));
const Logs = React.lazy(() => import('./pages/LogsPage'));
const Artifact = React.lazy(() => import('./pages/ArtifactPage'));
const Arty = React.lazy(() => import('./pages/Arty'));
const Syndicate = React.lazy(() => import('./pages/Syndicate'));
const Gladius = React.lazy(() => import('./pages/GladiusPage'));
const Settings = React.lazy(() => import('./pages/SettingsPage'));

function App() {
  return (
    <BrowserRouter>
      <div className="relative min-h-screen bg-bg-primary text-text-primary flex">
        <CosmicBackground />
        {/* Sidebar Navigation */}
        <Sidebar />
        
        {/* Main Content */}
        <main className="flex-1 relative z-10 overflow-auto">
          <div className="p-6">
            <React.Suspense fallback={
              <div className="flex items-center justify-center h-screen">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500" />
              </div>
            }>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/gladius" element={<Gladius />} />
                <Route path="/training" element={<Training />} />
                <Route path="/training/console" element={<TrainingConsole />} />
                <Route path="/telemetry" element={<TelemetryDashboard />} />
                <Route path="/sentinel" element={<Sentinel />} />
                <Route path="/legion" element={<Legion />} />
                <Route path="/logs" element={<Logs />} />
                <Route path="/artifact" element={<Artifact />} />
                <Route path="/arty" element={<Arty />} />
                <Route path="/syndicate" element={<Syndicate />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </React.Suspense>
          </div>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
