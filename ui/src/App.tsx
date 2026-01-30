import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useSystemStore } from './stores/systemStore';

// Layout Components
import Sidebar from './components/Sidebar';
import Header from './components/Header';

// Page Components
import Dashboard from './pages/Dashboard';
import GladiusPage from './pages/GladiusPage';
import SentinelPage from './pages/SentinelPage';
import LegionPage from './pages/LegionPage';
import ArtifactPage from './pages/ArtifactPage';
import LogsPage from './pages/LogsPage';
import SettingsPage from './pages/SettingsPage';

function App() {
  const { updateSystemStatus } = useSystemStore();

  useEffect(() => {
    // Initialize system status on mount
    const checkSystemStatus = async () => {
      try {
        // Check GLADIUS status
        const gladiusStatus = await window.electron.gladius.status();
        if (gladiusStatus.success) {
          updateSystemStatus({
            gladius: {
              status: 'running',
              lastUpdate: new Date().toISOString(),
              ...gladiusStatus.data,
            },
          });
        } else {
          updateSystemStatus({
            gladius: { status: 'error', error: gladiusStatus.error },
          });
        }

        // Check SENTINEL status
        const sentinelStatus = await window.electron.sentinel.status();
        if (sentinelStatus.success) {
          updateSystemStatus({
            sentinel: {
              status: sentinelStatus.data.running ? 'running' : 'stopped',
              lastUpdate: new Date().toISOString(),
              pid: sentinelStatus.data.pid,
            },
          });
        }

        // Check LEGION status
        const legionStatus = await window.electron.legion.status();
        if (legionStatus.success) {
          updateSystemStatus({
            legion: {
              status: 'running',
              lastUpdate: new Date().toISOString(),
              activeAgents: legionStatus.data.activeAgents || 0,
            },
          });
        }

        // Check Artifact status
        const artifactStatus = await window.electron.artifact.status();
        if (artifactStatus.success) {
          updateSystemStatus({
            artifact: {
              status: 'running',
              lastUpdate: new Date().toISOString(),
            },
          });
        }
      } catch (error) {
        console.error('Error checking system status:', error);
      }
    };

    // Initial check
    checkSystemStatus();

    // Poll status every 30 seconds
    const interval = setInterval(checkSystemStatus, 30000);

    return () => clearInterval(interval);
  }, [updateSystemStatus]);

  return (
    <Router>
      <div className="flex h-screen overflow-hidden bg-primary">
        {/* Sidebar */}
        <Sidebar />

        {/* Main Content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header />

          {/* Page Content */}
          <main className="flex-1 overflow-y-auto overflow-x-hidden bg-primary p-6 scrollbar-thin">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/gladius" element={<GladiusPage />} />
              <Route path="/sentinel" element={<SentinelPage />} />
              <Route path="/legion" element={<LegionPage />} />
              <Route path="/artifact" element={<ArtifactPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App;
