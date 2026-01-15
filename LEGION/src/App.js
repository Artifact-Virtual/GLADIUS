// src/App.js
// LEGION Enterprise Dashboard - Main Application

import React, { useState, useEffect } from 'react';
import './theme/GlobalTheme.css'; // Import unified theme

// Import Dashboard Components
import CommandDashboard from './components/CommandDashboard.jsx';
import OperationsDashboard from './components/OperationsDashboard.jsx';
import IntelligenceDashboard from './components/IntelligenceDashboard.jsx';
import CoordinationDashboard from './components/CoordinationDashboard.jsx';
import ManagementDashboard from './components/ManagementDashboard.jsx';
import OptimizationDashboard from './components/OptimizationDashboard.jsx';
import ApiMonitoringDashboard from './components/ApiMonitoringDashboard.jsx';

// Tab Configuration
const DASHBOARD_TABS = [
  { id: 'command', name: 'COMMAND', icon: 'fas fa-terminal', component: CommandDashboard },
  { id: 'operations', name: 'OPERATIONS', icon: 'fas fa-chart-line', component: OperationsDashboard },
  { id: 'intelligence', name: 'INTELLIGENCE', icon: 'fas fa-brain', component: IntelligenceDashboard },
  { id: 'coordination', name: 'COORDINATION', icon: 'fas fa-network-wired', component: CoordinationDashboard },
  { id: 'management', name: 'MANAGEMENT', icon: 'fas fa-cogs', component: ManagementDashboard },
  { id: 'optimization', name: 'OPTIMIZATION', icon: 'fas fa-rocket', component: OptimizationDashboard },
  { id: 'api-monitoring', name: 'API MONITORING', icon: 'fas fa-monitor-heart-rate', component: ApiMonitoringDashboard }
];

function App() {
  // Get initial tab from localStorage or default to 'command'
  const [activeTab, setActiveTab] = useState(() => {
    const savedTab = localStorage.getItem('legion-enterprise-active-tab');
    return savedTab && DASHBOARD_TABS.find(tab => tab.id === savedTab) ? savedTab : 'command';
  });
  
  // Persist active tab to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('legion-enterprise-active-tab', activeTab);
  }, [activeTab]);
  
  const ActiveComponent = DASHBOARD_TABS.find(tab => tab.id === activeTab)?.component || CommandDashboard;

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="brand-container">
          <img src="/av-black-logo.png" alt="Artifact Virtual" className="brand-logo" />
          <div className="brand-text">
            <h1>LEGION ENTERPRISE</h1>
            <span>AI-Powered Enterprise Management Platform</span>
          </div>
        </div>
        
        {/* Navigation Tabs */}
        <nav className="main-navigation">
          {DASHBOARD_TABS.map(tab => (
            <button
              key={tab.id}
              className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <i className={tab.icon}></i>
              <span>{tab.name}</span>
            </button>
          ))}
        </nav>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <ActiveComponent />
      </main>
    </div>
  );
}

export default App;
