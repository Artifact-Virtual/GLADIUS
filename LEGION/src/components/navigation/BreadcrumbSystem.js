// src/components/navigation/BreadcrumbSystem.js
// LEGION Enterprise Dashboard - Enhanced Breadcrumb Navigation System

import React, { useState, useEffect } from 'react';
import { useRouter } from '../routing/RouterSystem';
import { useLayout } from '../layout/ResponsiveLayout';

/**
 * Enhanced breadcrumb navigation with context-aware paths
 */
export function EnhancedBreadcrumbNavigation({ 
  className = '',
  showIcons = true,
  showHome = true,
  maxItems = 5,
  separator = '/',
  compact = false
}) {
  const router = useRouter();
  const layout = useLayout();
  const [breadcrumbs, setBreadcrumbs] = useState([]);

  // Tab metadata for breadcrumb generation
  const TAB_METADATA = {
    'COMMAND': {
      label: 'Command Center',
      path: '/dashboard/command',
      icon: 'fas fa-terminal',
      parent: null,
      description: 'System Overview & Control'
    },
    'OPERATIONS': {
      label: 'Operations',
      path: '/dashboard/operations',
      icon: 'fas fa-chart-line',
      parent: null,
      description: 'Business Operations Management'
    },
    'INTELLIGENCE': {
      label: 'Intelligence',
      path: '/dashboard/intelligence',
      icon: 'fas fa-brain',
      parent: null,
      description: 'Business Intelligence & Analytics'
    },
    'COORDINATION': {
      label: 'Coordination',
      path: '/dashboard/coordination',
      icon: 'fas fa-network-wired',
      parent: null,
      description: 'Agent & System Coordination'
    },
    'MANAGEMENT': {
      label: 'Management',
      path: '/dashboard/management',
      icon: 'fas fa-cogs',
      parent: null,
      description: 'Workflow & Process Management'
    },
    'OPTIMIZATION': {
      label: 'Optimization',
      path: '/dashboard/optimization',
      icon: 'fas fa-rocket',
      parent: null,
      description: 'Performance & System Optimization'
    },
    'API_MONITORING': {
      label: 'API Monitoring',
      path: '/dashboard/api-monitoring',
      icon: 'fas fa-plug',
      parent: null,
      description: 'External API Management'
    }
  };

  // Generate breadcrumb trail
  useEffect(() => {
    const generateBreadcrumbs = () => {
      const trail = [];

      // Add home/dashboard root if enabled
      if (showHome) {
        trail.push({
          label: layout.isMobile ? 'Dashboard' : 'LEGION Enterprise',
          path: '/dashboard',
          icon: 'fas fa-home',
          isActive: false,
          clickable: true,
          id: 'home'
        });
      }

      // Add current tab
      const currentTabData = TAB_METADATA[router.currentTab];
      if (currentTabData) {
        trail.push({
          label: currentTabData.label,
          path: currentTabData.path,
          icon: currentTabData.icon,
          isActive: true,
          clickable: false,
          id: router.currentTab.toLowerCase(),
          description: currentTabData.description
        });
      }

      // Limit breadcrumbs if needed
      if (trail.length > maxItems) {
        const start = trail.slice(0, 1); // Keep home
        const end = trail.slice(-maxItems + 2); // Keep last few + current
        const ellipsis = {
          label: '...',
          path: null,
          icon: 'fas fa-ellipsis-h',
          isActive: false,
          clickable: false,
          id: 'ellipsis',
          isEllipsis: true
        };
        setBreadcrumbs([...start, ellipsis, ...end]);
      } else {
        setBreadcrumbs(trail);
      }
    };

    generateBreadcrumbs();
  }, [router.currentTab, showHome, maxItems, layout.isMobile]);

  const handleBreadcrumbClick = (breadcrumb) => {
    if (!breadcrumb.clickable) return;

    if (breadcrumb.id === 'home') {
      router.navigateToTab('COMMAND'); // Default to command center
    } else {
      router.navigateToTab(breadcrumb.id.toUpperCase());
    }
  };

  if (breadcrumbs.length === 0) return null;

  return (
    <nav className={`enhanced-breadcrumb ${compact ? 'compact' : ''} ${className}`} aria-label="Breadcrumb navigation">
      <ol className="breadcrumb-trail">
        {breadcrumbs.map((crumb, index) => (
          <li key={crumb.id} className={`breadcrumb-segment ${crumb.isActive ? 'active' : ''} ${crumb.isEllipsis ? 'ellipsis' : ''}`}>
            {crumb.clickable ? (
              <button
                className="breadcrumb-link"
                onClick={() => handleBreadcrumbClick(crumb)}
                aria-label={`Navigate to ${crumb.label}`}
                title={crumb.description || crumb.label}
              >
                {showIcons && !compact && (
                  <i className={crumb.icon} aria-hidden="true" />
                )}
                <span className="breadcrumb-text">{crumb.label}</span>
              </button>
            ) : (
              <span 
                className={`breadcrumb-current ${crumb.isEllipsis ? 'ellipsis-indicator' : ''}`}
                aria-current={crumb.isActive ? 'page' : undefined}
                title={crumb.description || crumb.label}
              >
                {showIcons && !compact && !crumb.isEllipsis && (
                  <i className={crumb.icon} aria-hidden="true" />
                )}
                <span className="breadcrumb-text">{crumb.label}</span>
              </span>
            )}
            
            {index < breadcrumbs.length - 1 && (
              <span className="breadcrumb-separator" aria-hidden="true">
                {separator === '/' ? <i className="fas fa-chevron-right" /> : separator}
              </span>
            )}
          </li>
        ))}
      </ol>
      
      {/* Navigation context info */}
      {!compact && !layout.isMobile && (
        <div className="breadcrumb-context">
          <div className="navigation-info">
            <button 
              className="nav-back"
              onClick={router.goBack}
              disabled={!router.canGoBack}
              title="Go back"
              aria-label="Navigate back"
            >
              <i className="fas fa-arrow-left" />
            </button>
            <button 
              className="nav-forward"
              onClick={router.goForward}
              disabled={!router.canGoForward}
              title="Go forward"
              aria-label="Navigate forward"
            >
              <i className="fas fa-arrow-right" />
            </button>
          </div>
        </div>
      )}
    </nav>
  );
}

/**
 * Contextual navigation component showing related sections
 */
export function ContextualNavigation({ className = '' }) {
  const router = useRouter();
  const layout = useLayout();

  // Define related sections for each tab
  const RELATED_SECTIONS = {
    'COMMAND': [
      { id: 'operations', label: 'Operations', icon: 'fas fa-chart-line' },
      { id: 'intelligence', label: 'Intelligence', icon: 'fas fa-brain' }
    ],
    'OPERATIONS': [
      { id: 'command', label: 'Command', icon: 'fas fa-terminal' },
      { id: 'management', label: 'Management', icon: 'fas fa-cogs' }
    ],
    'INTELLIGENCE': [
      { id: 'command', label: 'Command', icon: 'fas fa-terminal' },
      { id: 'operations', label: 'Operations', icon: 'fas fa-chart-line' }
    ],
    'COORDINATION': [
      { id: 'command', label: 'Command', icon: 'fas fa-terminal' },
      { id: 'management', label: 'Management', icon: 'fas fa-cogs' }
    ],
    'MANAGEMENT': [
      { id: 'operations', label: 'Operations', icon: 'fas fa-chart-line' },
      { id: 'optimization', label: 'Optimization', icon: 'fas fa-rocket' }
    ],
    'OPTIMIZATION': [
      { id: 'management', label: 'Management', icon: 'fas fa-cogs' },
      { id: 'api-monitoring', label: 'API Monitoring', icon: 'fas fa-plug' }
    ],
    'API_MONITORING': [
      { id: 'coordination', label: 'Coordination', icon: 'fas fa-network-wired' },
      { id: 'optimization', label: 'Optimization', icon: 'fas fa-rocket' }
    ]
  };

  const relatedSections = RELATED_SECTIONS[router.currentTab] || [];

  if (relatedSections.length === 0 || layout.isMobile) return null;

  return (
    <nav className={`contextual-navigation ${className}`} aria-label="Related sections">
      <div className="contextual-header">
        <span className="contextual-title">Related Sections</span>
      </div>
      <div className="contextual-links">
        {relatedSections.map((section) => (
          <button
            key={section.id}
            className="contextual-link"
            onClick={() => router.navigateToTab(section.id.toUpperCase().replace('-', '_'))}
            title={`Navigate to ${section.label}`}
          >
            <i className={section.icon} />
            <span>{section.label}</span>
          </button>
        ))}
      </div>
    </nav>
  );
}

/**
 * Navigation history sidebar component
 */
export function NavigationHistorySidebar({ className = '', maxItems = 10 }) {
  const router = useRouter();
  const layout = useLayout();
  const [isOpen, setIsOpen] = useState(false);

  const history = router.getRecentHistory(maxItems);

  if (layout.isMobile) return null;

  return (
    <div className={`nav-history-sidebar ${isOpen ? 'open' : ''} ${className}`}>
      <button 
        className="history-toggle"
        onClick={() => setIsOpen(!isOpen)}
        title="Navigation History"
        aria-label="Toggle navigation history"
      >
        <i className="fas fa-history" />
      </button>
      
      {isOpen && (
        <div className="history-panel">
          <div className="history-header">
            <h4>Navigation History</h4>
            <button 
              className="history-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close history"
            >
              <i className="fas fa-times" />
            </button>
          </div>
          
          <div className="history-content">
            {history.length === 0 ? (
              <div className="history-empty">
                <i className="fas fa-history" />
                <span>No navigation history</span>
              </div>
            ) : (
              <ul className="history-list">
                {history.map((entry, index) => (
                  <li key={`${entry.timestamp}-${index}`} className={`history-entry ${entry.isActive ? 'active' : ''}`}>
                    <button
                      className="history-item"
                      onClick={() => router.navigateToTab(entry.tabId)}
                      disabled={entry.isActive}
                      title={`Navigate to ${entry.tabId}`}
                    >
                      <div className="history-info">
                        <span className="history-tab">{entry.tabId}</span>
                        <span className="history-time">
                          {new Date(entry.timestamp).toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </span>
                      </div>
                    </button>
                  </li>
                ))}
              </ul>
            )}
            
            {history.length > 0 && (
              <div className="history-actions">
                <button 
                  className="clear-history"
                  onClick={router.clearHistory}
                  title="Clear navigation history"
                >
                  <i className="fas fa-trash" />
                  Clear History
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default EnhancedBreadcrumbNavigation;
