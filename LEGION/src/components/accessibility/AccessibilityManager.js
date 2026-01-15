// src/components/accessibility/AccessibilityManager.js
// LEGION Enterprise Dashboard - Accessibility Management System

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

/**
 * Accessibility context
 */
const AccessibilityContext = createContext({
  isHighContrast: false,
  isReducedMotion: false,
  isLargeText: false,
  screenReaderMode: false,
  keyboardOnlyMode: false,
  toggleHighContrast: () => {},
  toggleReducedMotion: () => {},
  toggleLargeText: () => {},
  toggleScreenReaderMode: () => {},
  toggleKeyboardOnlyMode: () => {},
  announceToScreenReader: () => {},
  focusAnnouncements: true
});

/**
 * Accessibility preferences storage
 */
const ACCESSIBILITY_STORAGE_KEY = 'legion_accessibility_preferences';

/**
 * Screen reader announcements manager
 */
class ScreenReaderAnnouncer {
  constructor() {
    this.announcer = null;
    this.createAnnouncer();
  }

  createAnnouncer() {
    // Remove existing announcer
    if (this.announcer) {
      document.body.removeChild(this.announcer);
    }

    // Create new announcer
    this.announcer = document.createElement('div');
    this.announcer.setAttribute('aria-live', 'polite');
    this.announcer.setAttribute('aria-atomic', 'true');
    this.announcer.setAttribute('aria-hidden', 'false');
    this.announcer.className = 'sr-only screen-reader-announcer';
    this.announcer.style.cssText = `
      position: absolute !important;
      width: 1px !important;
      height: 1px !important;
      padding: 0 !important;
      margin: -1px !important;
      overflow: hidden !important;
      clip: rect(0, 0, 0, 0) !important;
      white-space: nowrap !important;
      border: 0 !important;
    `;
    document.body.appendChild(this.announcer);
  }

  announce(message, priority = 'polite') {
    if (!this.announcer || !message) return;

    // Clear previous message
    this.announcer.textContent = '';
    
    // Set priority
    this.announcer.setAttribute('aria-live', priority);
    
    // Announce new message
    setTimeout(() => {
      this.announcer.textContent = message;
    }, 100);

    // Clear after announcement
    setTimeout(() => {
      this.announcer.textContent = '';
    }, 3000);
  }

  destroy() {
    if (this.announcer && document.body.contains(this.announcer)) {
      document.body.removeChild(this.announcer);
      this.announcer = null;
    }
  }
}

/**
 * Accessibility manager provider
 */
export function AccessibilityProvider({ children }) {
  // Accessibility states
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [isReducedMotion, setIsReducedMotion] = useState(false);
  const [isLargeText, setIsLargeText] = useState(false);
  const [screenReaderMode, setScreenReaderMode] = useState(false);
  const [keyboardOnlyMode, setKeyboardOnlyMode] = useState(false);
  const [focusAnnouncements, setFocusAnnouncements] = useState(true);
  
  // Screen reader announcer
  const [announcer] = useState(new ScreenReaderAnnouncer());

  // Load preferences on mount
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const saved = localStorage.getItem(ACCESSIBILITY_STORAGE_KEY);
        if (saved) {
          const preferences = JSON.parse(saved);
          setIsHighContrast(preferences.isHighContrast || false);
          setIsReducedMotion(preferences.isReducedMotion || false);
          setIsLargeText(preferences.isLargeText || false);
          setScreenReaderMode(preferences.screenReaderMode || false);
          setKeyboardOnlyMode(preferences.keyboardOnlyMode || false);
          setFocusAnnouncements(preferences.focusAnnouncements !== false);
        }
      } catch (error) {
        console.warn('Failed to load accessibility preferences:', error);
      }

      // Detect browser preferences
      detectBrowserPreferences();
    };

    loadPreferences();
  }, []);

  // Detect browser accessibility preferences
  const detectBrowserPreferences = useCallback(() => {
    // Detect prefers-reduced-motion
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      setIsReducedMotion(true);
    }

    // Detect prefers-contrast
    if (window.matchMedia('(prefers-contrast: high)').matches) {
      setIsHighContrast(true);
    }

    // Listen for changes
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');

    const handleMotionChange = (e) => setIsReducedMotion(e.matches);
    const handleContrastChange = (e) => setIsHighContrast(e.matches);

    motionQuery.addEventListener('change', handleMotionChange);
    contrastQuery.addEventListener('change', handleContrastChange);

    return () => {
      motionQuery.removeEventListener('change', handleMotionChange);
      contrastQuery.removeEventListener('change', handleContrastChange);
    };
  }, []);

  // Save preferences when they change
  useEffect(() => {
    const preferences = {
      isHighContrast,
      isReducedMotion,
      isLargeText,
      screenReaderMode,
      keyboardOnlyMode,
      focusAnnouncements
    };

    try {
      localStorage.setItem(ACCESSIBILITY_STORAGE_KEY, JSON.stringify(preferences));
    } catch (error) {
      console.warn('Failed to save accessibility preferences:', error);
    }
  }, [isHighContrast, isReducedMotion, isLargeText, screenReaderMode, keyboardOnlyMode, focusAnnouncements]);

  // Apply accessibility settings to document
  useEffect(() => {
    const root = document.documentElement;
    
    // High contrast
    if (isHighContrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Reduced motion
    if (isReducedMotion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    // Large text
    if (isLargeText) {
      root.classList.add('large-text');
    } else {
      root.classList.remove('large-text');
    }

    // Screen reader mode
    if (screenReaderMode) {
      root.classList.add('screen-reader-mode');
    } else {
      root.classList.remove('screen-reader-mode');
    }

    // Keyboard only mode
    if (keyboardOnlyMode) {
      root.classList.add('keyboard-only-mode');
    } else {
      root.classList.remove('keyboard-only-mode');
    }
  }, [isHighContrast, isReducedMotion, isLargeText, screenReaderMode, keyboardOnlyMode]);

  // Detect keyboard usage
  useEffect(() => {
    let keyboardUsed = false;

    const handleKeyDown = (e) => {
      if (e.key === 'Tab') {
        keyboardUsed = true;
        if (!keyboardOnlyMode) {
          setKeyboardOnlyMode(true);
        }
      }
    };

    const handleMouseDown = () => {
      if (keyboardUsed && keyboardOnlyMode) {
        keyboardUsed = false;
        setKeyboardOnlyMode(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('mousedown', handleMouseDown);
    };
  }, [keyboardOnlyMode]);

  // Toggle functions
  const toggleHighContrast = useCallback(() => {
    setIsHighContrast(prev => {
      const newValue = !prev;
      announcer.announce(
        newValue ? 'High contrast mode enabled' : 'High contrast mode disabled'
      );
      return newValue;
    });
  }, [announcer]);

  const toggleReducedMotion = useCallback(() => {
    setIsReducedMotion(prev => {
      const newValue = !prev;
      announcer.announce(
        newValue ? 'Reduced motion enabled' : 'Reduced motion disabled'
      );
      return newValue;
    });
  }, [announcer]);

  const toggleLargeText = useCallback(() => {
    setIsLargeText(prev => {
      const newValue = !prev;
      announcer.announce(
        newValue ? 'Large text mode enabled' : 'Large text mode disabled'
      );
      return newValue;
    });
  }, [announcer]);

  const toggleScreenReaderMode = useCallback(() => {
    setScreenReaderMode(prev => {
      const newValue = !prev;
      announcer.announce(
        newValue ? 'Screen reader optimizations enabled' : 'Screen reader optimizations disabled'
      );
      return newValue;
    });
  }, [announcer]);

  const toggleKeyboardOnlyMode = useCallback(() => {
    setKeyboardOnlyMode(prev => {
      const newValue = !prev;
      announcer.announce(
        newValue ? 'Keyboard-only navigation enabled' : 'Keyboard-only navigation disabled'
      );
      return newValue;
    });
  }, [announcer]);

  // Screen reader announcement function
  const announceToScreenReader = useCallback((message, priority = 'polite') => {
    announcer.announce(message, priority);
  }, [announcer]);

  // Cleanup announcer on unmount
  useEffect(() => {
    return () => announcer.destroy();
  }, [announcer]);

  const value = {
    isHighContrast,
    isReducedMotion,
    isLargeText,
    screenReaderMode,
    keyboardOnlyMode,
    focusAnnouncements,
    toggleHighContrast,
    toggleReducedMotion,
    toggleLargeText,
    toggleScreenReaderMode,
    toggleKeyboardOnlyMode,
    announceToScreenReader
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
}

/**
 * Hook to use accessibility context
 */
export function useAccessibility() {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within AccessibilityProvider');
  }
  return context;
}

/**
 * Accessibility control panel component
 */
export function AccessibilityPanel({ isOpen, onClose, className = '' }) {
  const {
    isHighContrast,
    isReducedMotion,
    isLargeText,
    screenReaderMode,
    keyboardOnlyMode,
    focusAnnouncements,
    toggleHighContrast,
    toggleReducedMotion,
    toggleLargeText,
    toggleScreenReaderMode,
    toggleKeyboardOnlyMode
  } = useAccessibility();

  if (!isOpen) return null;

  return (
    <div className={`accessibility-panel-overlay ${className}`} onClick={onClose}>
      <div 
        className="accessibility-panel"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="accessibility-title"
        aria-modal="true"
      >
        <div className="accessibility-header">
          <h2 id="accessibility-title">Accessibility Settings</h2>
          <button 
            className="accessibility-close"
            onClick={onClose}
            aria-label="Close accessibility settings"
          >
            <i className="fas fa-times" />
          </button>
        </div>
        
        <div className="accessibility-content">
          <div className="accessibility-section">
            <h3>Visual Preferences</h3>
            <div className="accessibility-controls">
              <label className="accessibility-toggle">
                <input
                  type="checkbox"
                  checked={isHighContrast}
                  onChange={toggleHighContrast}
                  aria-describedby="high-contrast-desc"
                />
                <span className="toggle-slider" />
                <div className="toggle-content">
                  <span className="toggle-label">High Contrast</span>
                  <span id="high-contrast-desc" className="toggle-description">
                    Increases contrast for better visibility
                  </span>
                </div>
              </label>

              <label className="accessibility-toggle">
                <input
                  type="checkbox"
                  checked={isLargeText}
                  onChange={toggleLargeText}
                  aria-describedby="large-text-desc"
                />
                <span className="toggle-slider" />
                <div className="toggle-content">
                  <span className="toggle-label">Large Text</span>
                  <span id="large-text-desc" className="toggle-description">
                    Increases font size throughout the interface
                  </span>
                </div>
              </label>
            </div>
          </div>

          <div className="accessibility-section">
            <h3>Motion & Animation</h3>
            <div className="accessibility-controls">
              <label className="accessibility-toggle">
                <input
                  type="checkbox"
                  checked={isReducedMotion}
                  onChange={toggleReducedMotion}
                  aria-describedby="reduced-motion-desc"
                />
                <span className="toggle-slider" />
                <div className="toggle-content">
                  <span className="toggle-label">Reduced Motion</span>
                  <span id="reduced-motion-desc" className="toggle-description">
                    Reduces animations and transitions
                  </span>
                </div>
              </label>
            </div>
          </div>

          <div className="accessibility-section">
            <h3>Navigation Preferences</h3>
            <div className="accessibility-controls">
              <label className="accessibility-toggle">
                <input
                  type="checkbox"
                  checked={screenReaderMode}
                  onChange={toggleScreenReaderMode}
                  aria-describedby="screen-reader-desc"
                />
                <span className="toggle-slider" />
                <div className="toggle-content">
                  <span className="toggle-label">Screen Reader Optimizations</span>
                  <span id="screen-reader-desc" className="toggle-description">
                    Optimizes interface for screen reader users
                  </span>
                </div>
              </label>

              <label className="accessibility-toggle">
                <input
                  type="checkbox"
                  checked={keyboardOnlyMode}
                  onChange={toggleKeyboardOnlyMode}
                  aria-describedby="keyboard-only-desc"
                />
                <span className="toggle-slider" />
                <div className="toggle-content">
                  <span className="toggle-label">Keyboard-Only Navigation</span>
                  <span id="keyboard-only-desc" className="toggle-description">
                    Enhanced keyboard navigation and focus indicators
                  </span>
                </div>
              </label>
            </div>
          </div>
        </div>

        <div className="accessibility-footer">
          <p>
            These settings are saved locally and will persist across sessions.
            For additional accessibility features, check your browser and operating system settings.
          </p>
        </div>
      </div>
    </div>
  );
}

/**
 * Live region component for announcements
 */
export function LiveRegion({ 
  children, 
  politeness = 'polite', 
  atomic = true, 
  relevant = 'all',
  className = '' 
}) {
  return (
    <div
      className={`live-region ${className}`}
      aria-live={politeness}
      aria-atomic={atomic}
      aria-relevant={relevant}
      role="status"
    >
      {children}
    </div>
  );
}

/**
 * Skip to content component
 */
export function SkipToContent({ targetId = 'main-content', children = 'Skip to main content' }) {
  return (
    <a 
      href={`#${targetId}`}
      className="skip-to-content"
      onKeyDown={(e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          const target = document.getElementById(targetId);
          if (target) {
            target.focus();
            target.scrollIntoView();
          }
        }
      }}
    >
      {children}
    </a>
  );
}

export default AccessibilityProvider;
