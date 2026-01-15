// src/components/navigation/MobileNavigation.js
// LEGION Enterprise Dashboard - Mobile Navigation Component

import React, { useState, useEffect } from 'react';
import { useRouter } from '../routing/RouterSystem';
import { useLayout } from '../layout/ResponsiveLayout';

/**
 * Mobile-optimized navigation component
 * Provides bottom tab bar and slide-out drawer for mobile devices
 */
export function MobileNavigation({ tabs, className = '' }) {
  const router = useRouter();
  const layout = useLayout();
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // Close drawer when tab changes
  useEffect(() => {
    setIsDrawerOpen(false);
  }, [router.currentTab]);

  // Close drawer on escape key
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') {
        setIsDrawerOpen(false);
      }
    };

    if (isDrawerOpen) {
      document.addEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [isDrawerOpen]);

  const handleTabClick = (tabId) => {
    router.navigateToTab(tabId.toUpperCase());
  };

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  if (!layout.isMobile) {
    return null;
  }

  return (
    <>
      {/* Mobile Bottom Tab Bar */}
      <nav className={`mobile-bottom-nav ${className}`}>
        <div className="bottom-nav-container">
          {tabs.slice(0, 4).map((tab) => (
            <button
              key={tab.id}
              className={`bottom-nav-item ${router.currentTab.toLowerCase() === tab.id ? 'active' : ''}`}
              onClick={() => handleTabClick(tab.id)}
              aria-label={tab.title}
            >
              <i className={tab.icon} />
              <span className="nav-label">{tab.name}</span>
            </button>
          ))}
          
          {/* More button for additional tabs */}
          {tabs.length > 4 && (
            <button
              className={`bottom-nav-item more-button ${isDrawerOpen ? 'active' : ''}`}
              onClick={toggleDrawer}
              aria-label="More options"
            >
              <i className="fas fa-th" />
              <span className="nav-label">More</span>
            </button>
          )}
        </div>
      </nav>

      {/* Mobile Drawer Overlay */}
      {isDrawerOpen && (
        <div className="mobile-drawer-overlay" onClick={() => setIsDrawerOpen(false)}>
          <div className="mobile-drawer" onClick={(e) => e.stopPropagation()}>
            <div className="drawer-header">
              <h3>Navigation</h3>
              <button 
                className="drawer-close"
                onClick={() => setIsDrawerOpen(false)}
                aria-label="Close drawer"
              >
                <i className="fas fa-times" />
              </button>
            </div>
            
            <div className="drawer-content">
              <div className="drawer-tabs">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    className={`drawer-tab ${router.currentTab.toLowerCase() === tab.id ? 'active' : ''}`}
                    onClick={() => handleTabClick(tab.id)}
                  >
                    <div className="drawer-tab-icon">
                      <i className={tab.icon} />
                    </div>
                    <div className="drawer-tab-content">
                      <span className="drawer-tab-name">{tab.name}</span>
                      <span className="drawer-tab-description">{tab.description}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/**
 * Mobile header component with hamburger menu
 */
export function MobileHeader({ 
  title = "LEGION Enterprise", 
  subtitle = "Dashboard",
  onMenuToggle,
  showBack = false,
  onBack,
  className = ''
}) {
  const layout = useLayout();
  const router = useRouter();

  if (!layout.isMobile) {
    return null;
  }

  return (
    <header className={`mobile-header ${className}`}>
      <div className="mobile-header-content">
        {/* Left side */}
        <div className="mobile-header-left">
          {showBack ? (
            <button 
              className="mobile-back-button"
              onClick={onBack}
              aria-label="Go back"
            >
              <i className="fas fa-arrow-left" />
            </button>
          ) : (
            <button 
              className="mobile-menu-button"
              onClick={onMenuToggle}
              aria-label="Open menu"
            >
              <i className="fas fa-bars" />
            </button>
          )}
        </div>

        {/* Center */}
        <div className="mobile-header-center">
          <h1 className="mobile-title">{title}</h1>
          {subtitle && <span className="mobile-subtitle">{subtitle}</span>}
        </div>

        {/* Right side */}
        <div className="mobile-header-right">
          <button 
            className="mobile-action-button"
            aria-label="Search"
          >
            <i className="fas fa-search" />
          </button>
        </div>
      </div>
    </header>
  );
}

/**
 * Mobile slide-out menu
 */
export function MobileMenu({ 
  isOpen, 
  onClose, 
  tabs, 
  systemStatus,
  className = '' 
}) {
  const router = useRouter();
  const layout = useLayout();

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }

    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  const handleTabClick = (tabId) => {
    router.navigateToTab(tabId.toUpperCase());
    onClose();
  };

  if (!layout.isMobile || !isOpen) {
    return null;
  }

  return (
    <div className={`mobile-menu-overlay ${className}`} onClick={onClose}>
      <nav className="mobile-menu" onClick={(e) => e.stopPropagation()}>
        <div className="mobile-menu-header">
          <div className="menu-title">
            <i className="fas fa-shield-alt" />
            <span>LEGION Enterprise</span>
          </div>
          <button 
            className="menu-close"
            onClick={onClose}
            aria-label="Close menu"
          >
            <i className="fas fa-times" />
          </button>
        </div>

        <div className="mobile-menu-content">
          <div className="menu-tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                className={`menu-tab ${router.currentTab.toLowerCase() === tab.id ? 'active' : ''}`}
                onClick={() => handleTabClick(tab.id)}
              >
                <div className="menu-tab-icon">
                  <i className={tab.icon} />
                </div>
                <div className="menu-tab-content">
                  <span className="menu-tab-name">{tab.name}</span>
                  <span className="menu-tab-description">{tab.description}</span>
                </div>
                <div className="menu-tab-indicator">
                  <i className="fas fa-chevron-right" />
                </div>
              </button>
            ))}
          </div>

          <div className="menu-footer">
            <div className="menu-status">
              <div className={`status-indicator ${systemStatus.systemHealth}`}>
                <i className={`fas fa-${systemStatus.connected ? 'check-circle' : 'exclamation-triangle'}`} />
                <span>{systemStatus.connected ? 'Online' : 'Offline'}</span>
              </div>
              <div className="agent-count">
                <i className="fas fa-users" />
                <span>{systemStatus.agentsOnline} Active Agents</span>
              </div>
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
}

/**
 * Mobile-optimized tab swiper component
 */
export function MobileTabSwiper({ 
  tabs, 
  onTabChange, 
  className = '' 
}) {
  const router = useRouter();
  const layout = useLayout();
  const [startX, setStartX] = useState(0);
  const [isDragging, setIsDragging] = useState(false);

  if (!layout.isMobile) {
    return null;
  }

  const handleTouchStart = (e) => {
    setStartX(e.touches[0].clientX);
    setIsDragging(true);
  };

  const handleTouchEnd = (e) => {
    if (!isDragging) return;
    
    const endX = e.changedTouches[0].clientX;
    const diff = startX - endX;
    const threshold = 100;

    if (Math.abs(diff) > threshold) {
      const currentIndex = tabs.findIndex(tab => tab.id === router.currentTab.toLowerCase());
      let newIndex;

      if (diff > 0 && currentIndex < tabs.length - 1) {
        // Swipe left - next tab
        newIndex = currentIndex + 1;
      } else if (diff < 0 && currentIndex > 0) {
        // Swipe right - previous tab
        newIndex = currentIndex - 1;
      }

      if (newIndex !== undefined) {
        router.navigateToTab(tabs[newIndex].id.toUpperCase());
      }
    }

    setIsDragging(false);
  };

  return (
    <div 
      className={`mobile-tab-swiper ${className}`}
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
    >
      <div className="swiper-indicator">
        <div className="swiper-dots">
          {tabs.map((tab, index) => (
            <button
              key={tab.id}
              className={`swiper-dot ${router.currentTab.toLowerCase() === tab.id ? 'active' : ''}`}
              onClick={() => router.navigateToTab(tab.id.toUpperCase())}
              aria-label={`Go to ${tab.name}`}
            />
          ))}
        </div>
        <div className="swiper-text">
          Swipe to navigate between tabs
        </div>
      </div>
    </div>
  );
}

export default MobileNavigation;
