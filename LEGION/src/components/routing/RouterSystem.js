// src/components/routing/RouterSystem.js
// LEGION Enterprise Dashboard - Navigation Router System

import React, { useState, useEffect } from 'react';

/**
 * Enhanced routing system for LEGION Enterprise Dashboard
 * Provides tab-based navigation with history management and state persistence
 */
class RouterSystem {
  constructor() {
    this.currentTab = 'COMMAND';
    this.history = [];
    this.historyIndex = -1;
    this.listeners = new Set();
    this.maxHistorySize = 50;
    
    // Initialize from localStorage
    this.loadPersistedState();
  }

  /**
   * Load persisted routing state from localStorage
   */
  loadPersistedState() {
    try {
      const saved = localStorage.getItem('legion_router_state');
      if (saved) {
        const state = JSON.parse(saved);
        this.currentTab = state.currentTab || 'COMMAND';
        this.history = state.history || [];
        this.historyIndex = state.historyIndex || -1;
      }
    } catch (error) {
      console.warn('Failed to load router state:', error);
    }
  }

  /**
   * Persist routing state to localStorage
   */
  persistState() {
    try {
      const state = {
        currentTab: this.currentTab,
        history: this.history,
        historyIndex: this.historyIndex
      };
      localStorage.setItem('legion_router_state', JSON.stringify(state));
    } catch (error) {
      console.warn('Failed to persist router state:', error);
    }
  }

  /**
   * Navigate to a specific tab
   */
  navigateToTab(tabId, addToHistory = true) {
    if (this.currentTab === tabId) return;

    const previousTab = this.currentTab;
    this.currentTab = tabId;

    if (addToHistory) {
      this.addToHistory(tabId, previousTab);
    }

    this.persistState();
    this.notifyListeners();
  }

  /**
   * Add navigation to history
   */
  addToHistory(tabId, fromTab) {
    const historyEntry = {
      tabId,
      fromTab,
      timestamp: Date.now(),
      path: this.getTabPath(tabId)
    };

    // Remove any entries after current index (when navigating from middle of history)
    this.history = this.history.slice(0, this.historyIndex + 1);
    
    // Add new entry
    this.history.push(historyEntry);
    this.historyIndex = this.history.length - 1;

    // Limit history size
    if (this.history.length > this.maxHistorySize) {
      this.history = this.history.slice(-this.maxHistorySize);
      this.historyIndex = this.history.length - 1;
    }
  }

  /**
   * Get the path for a tab (useful for breadcrumbs)
   */
  getTabPath(tabId) {
    const paths = {
      'COMMAND': '/dashboard/command',
      'OPERATIONS': '/dashboard/operations',
      'INTELLIGENCE': '/dashboard/intelligence',
      'COORDINATION': '/dashboard/coordination',
      'MANAGEMENT': '/dashboard/management',
      'OPTIMIZATION': '/dashboard/optimization',
      'API_MONITORING': '/dashboard/api-monitoring'
    };
    return paths[tabId] || '/dashboard';
  }

  /**
   * Navigate back in history
   */
  goBack() {
    if (this.canGoBack()) {
      this.historyIndex--;
      const entry = this.history[this.historyIndex];
      this.currentTab = entry.tabId;
      this.persistState();
      this.notifyListeners();
      return true;
    }
    return false;
  }

  /**
   * Navigate forward in history
   */
  goForward() {
    if (this.canGoForward()) {
      this.historyIndex++;
      const entry = this.history[this.historyIndex];
      this.currentTab = entry.tabId;
      this.persistState();
      this.notifyListeners();
      return true;
    }
    return false;
  }

  /**
   * Check if can navigate back
   */
  canGoBack() {
    return this.historyIndex > 0;
  }

  /**
   * Check if can navigate forward
   */
  canGoForward() {
    return this.historyIndex < this.history.length - 1;
  }

  /**
   * Get current navigation state
   */
  getCurrentState() {
    return {
      currentTab: this.currentTab,
      canGoBack: this.canGoBack(),
      canGoForward: this.canGoForward(),
      history: this.history,
      historyIndex: this.historyIndex,
      path: this.getTabPath(this.currentTab)
    };
  }

  /**
   * Get breadcrumb trail
   */
  getBreadcrumbs() {
    const breadcrumbs = [];
    
    // Add dashboard root
    breadcrumbs.push({
      label: 'LEGION Enterprise',
      path: '/dashboard',
      isActive: false
    });

    // Add current tab
    const tabLabels = {
      'COMMAND': 'Command Center',
      'OPERATIONS': 'Operations',
      'INTELLIGENCE': 'Intelligence',
      'COORDINATION': 'Coordination',
      'MANAGEMENT': 'Management',
      'OPTIMIZATION': 'Optimization',
      'API_MONITORING': 'API Monitoring'
    };

    breadcrumbs.push({
      label: tabLabels[this.currentTab] || this.currentTab,
      path: this.getTabPath(this.currentTab),
      isActive: true
    });

    return breadcrumbs;
  }

  /**
   * Subscribe to navigation changes
   */
  subscribe(listener) {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  /**
   * Notify all listeners of navigation changes
   */
  notifyListeners() {
    const state = this.getCurrentState();
    this.listeners.forEach(listener => {
      try {
        listener(state);
      } catch (error) {
        console.error('Router listener error:', error);
      }
    });
  }

  /**
   * Clear navigation history
   */
  clearHistory() {
    this.history = [];
    this.historyIndex = -1;
    this.persistState();
  }

  /**
   * Get recent navigation history
   */
  getRecentHistory(limit = 10) {
    return this.history
      .slice(-limit)
      .reverse()
      .map(entry => ({
        ...entry,
        isActive: entry.tabId === this.currentTab
      }));
  }
}

// Create singleton instance
const routerInstance = new RouterSystem();

/**
 * React hook for using the router system
 */
export function useRouter() {
  const [state, setState] = useState(routerInstance.getCurrentState());

  useEffect(() => {
    const unsubscribe = routerInstance.subscribe(setState);
    return unsubscribe;
  }, []);

  return {
    ...state,
    navigateToTab: (tabId) => routerInstance.navigateToTab(tabId),
    goBack: () => routerInstance.goBack(),
    goForward: () => routerInstance.goForward(),
    getBreadcrumbs: () => routerInstance.getBreadcrumbs(),
    getRecentHistory: (limit) => routerInstance.getRecentHistory(limit),
    clearHistory: () => routerInstance.clearHistory()
  };
}

/**
 * Navigation component for handling keyboard shortcuts and browser events
 */
export function NavigationManager({ children }) {
  const router = useRouter();

  useEffect(() => {
    const handleKeyboard = (event) => {
      // Handle navigation shortcuts
      if (event.ctrlKey || event.metaKey) {
        const shortcutMap = {
          '1': 'COMMAND',
          '2': 'OPERATIONS',
          '3': 'INTELLIGENCE',
          '4': 'COORDINATION',
          '5': 'MANAGEMENT',
          '6': 'OPTIMIZATION',
          '7': 'API_MONITORING'
        };

        if (shortcutMap[event.key]) {
          event.preventDefault();
          router.navigateToTab(shortcutMap[event.key]);
        }
      }

      // Handle browser-like navigation
      if (event.altKey) {
        if (event.key === 'ArrowLeft') {
          event.preventDefault();
          router.goBack();
        } else if (event.key === 'ArrowRight') {
          event.preventDefault();
          router.goForward();
        }
      }
    };

    const handlePopstate = (event) => {
      // Handle browser back/forward buttons
      if (event.state && event.state.tabId) {
        router.navigateToTab(event.state.tabId, false);
      }
    };

    document.addEventListener('keydown', handleKeyboard);
    window.addEventListener('popstate', handlePopstate);

    return () => {
      document.removeEventListener('keydown', handleKeyboard);
      window.removeEventListener('popstate', handlePopstate);
    };
  }, [router]);

  // Update browser history
  useEffect(() => {
    const state = { tabId: router.currentTab };
    const url = router.path;
    
    try {
      window.history.pushState(state, '', url);
    } catch (error) {
      console.warn('Failed to update browser history:', error);
    }
  }, [router.currentTab, router.path]);

  return children;
}

/**
 * Breadcrumb navigation component
 */
export function BreadcrumbNavigation({ className = '' }) {
  const router = useRouter();
  const breadcrumbs = router.getBreadcrumbs();

  return (
    <nav className={`breadcrumb-navigation ${className}`} aria-label="Breadcrumb">
      <ol className="breadcrumb-list">
        {breadcrumbs.map((crumb, index) => (
          <li key={index} className={`breadcrumb-item ${crumb.isActive ? 'active' : ''}`}>
            {crumb.isActive ? (
              <span className="breadcrumb-current" aria-current="page">
                {crumb.label}
              </span>
            ) : (
              <button
                className="breadcrumb-link"
                onClick={() => router.navigateToTab('COMMAND')}
                aria-label={`Navigate to ${crumb.label}`}
              >
                {crumb.label}
              </button>
            )}
            {index < breadcrumbs.length - 1 && (
              <span className="breadcrumb-separator" aria-hidden="true">
                /
              </span>
            )}
          </li>
        ))}
      </ol>
    </nav>
  );
}

/**
 * Navigation history component
 */
export function NavigationHistory({ maxItems = 5, className = '' }) {
  const router = useRouter();
  const history = router.getRecentHistory(maxItems);

  if (history.length === 0) return null;

  return (
    <div className={`navigation-history ${className}`}>
      <h4 className="history-title">Recent Navigation</h4>
      <ul className="history-list">
        {history.map((entry, index) => (
          <li key={`${entry.timestamp}-${index}`} className={`history-item ${entry.isActive ? 'active' : ''}`}>
            <button
              className="history-link"
              onClick={() => router.navigateToTab(entry.tabId)}
              disabled={entry.isActive}
              aria-label={`Navigate to ${entry.tabId}`}
            >
              <span className="history-tab">{entry.tabId}</span>
              <span className="history-time">
                {new Date(entry.timestamp).toLocaleTimeString()}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default routerInstance;
