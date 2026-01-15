// src/components/accessibility/KeyboardNavigation.js
// LEGION Enterprise Dashboard - Keyboard Navigation System

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

/**
 * Keyboard navigation context
 */
const KeyboardNavigationContext = createContext({
  registerShortcut: () => {},
  unregisterShortcut: () => {},
  isShortcutActive: () => false,
  shortcuts: {},
  focusManager: null
});

/**
 * Default keyboard shortcuts for the application
 */
const DEFAULT_SHORTCUTS = {
  // Tab navigation
  'ctrl+1': { action: 'navigate_tab', payload: 'COMMAND', description: 'Navigate to Command Center' },
  'ctrl+2': { action: 'navigate_tab', payload: 'OPERATIONS', description: 'Navigate to Operations' },
  'ctrl+3': { action: 'navigate_tab', payload: 'INTELLIGENCE', description: 'Navigate to Intelligence' },
  'ctrl+4': { action: 'navigate_tab', payload: 'COORDINATION', description: 'Navigate to Coordination' },
  'ctrl+5': { action: 'navigate_tab', payload: 'MANAGEMENT', description: 'Navigate to Management' },
  'ctrl+6': { action: 'navigate_tab', payload: 'OPTIMIZATION', description: 'Navigate to Optimization' },
  'ctrl+7': { action: 'navigate_tab', payload: 'API_MONITORING', description: 'Navigate to API Monitoring' },
  
  // Navigation controls
  'alt+left': { action: 'go_back', description: 'Go back in navigation history' },
  'alt+right': { action: 'go_forward', description: 'Go forward in navigation history' },
  'ctrl+home': { action: 'go_home', description: 'Go to dashboard home' },
  
  // Interface controls
  'ctrl+shift+s': { action: 'toggle_sidebar', description: 'Toggle sidebar' },
  'escape': { action: 'close_modal', description: 'Close modal/overlay' },
  'ctrl+shift+k': { action: 'show_shortcuts', description: 'Show keyboard shortcuts' },
  
  // Search and commands
  'ctrl+k': { action: 'open_command_palette', description: 'Open command palette' },
  'ctrl+slash': { action: 'toggle_help', description: 'Toggle help panel' },
  'f11': { action: 'toggle_fullscreen', description: 'Toggle fullscreen mode' },
  
  // Accessibility
  'ctrl+shift+a': { action: 'toggle_accessibility', description: 'Toggle accessibility mode' },
  'ctrl+shift+h': { action: 'focus_header', description: 'Focus header navigation' },
  'ctrl+shift+m': { action: 'focus_main', description: 'Focus main content' },
  
  // Quick actions
  'ctrl+r': { action: 'refresh_dashboard', description: 'Refresh current dashboard' },
  'ctrl+shift+r': { action: 'hard_refresh', description: 'Hard refresh application' },
};

/**
 * Focus management for keyboard navigation
 */
class FocusManager {
  constructor() {
    this.focusStack = [];
    this.trapActive = false;
    this.lastFocused = null;
  }

  // Push focus trap
  pushFocusTrap(container) {
    if (this.trapActive) {
      this.focusStack.push(this.getCurrentTrap());
    }
    this.setFocusTrap(container);
  }

  // Pop focus trap
  popFocusTrap() {
    this.removeFocusTrap();
    if (this.focusStack.length > 0) {
      const previousTrap = this.focusStack.pop();
      this.setFocusTrap(previousTrap);
    }
  }

  // Set focus trap on container
  setFocusTrap(container) {
    if (!container) return;

    this.lastFocused = document.activeElement;
    this.trapActive = true;
    this.currentTrap = container;

    // Find focusable elements
    const focusableElements = this.getFocusableElements(container);
    if (focusableElements.length === 0) return;

    // Focus first element
    focusableElements[0].focus();

    // Add event listeners
    this.trapKeyHandler = (e) => this.handleTrapKeydown(e, focusableElements);
    document.addEventListener('keydown', this.trapKeyHandler);
  }

  // Remove focus trap
  removeFocusTrap() {
    if (!this.trapActive) return;

    this.trapActive = false;
    this.currentTrap = null;

    if (this.trapKeyHandler) {
      document.removeEventListener('keydown', this.trapKeyHandler);
      this.trapKeyHandler = null;
    }

    // Restore focus
    if (this.lastFocused && this.lastFocused.focus) {
      this.lastFocused.focus();
    }
  }

  // Get current trap container
  getCurrentTrap() {
    return this.currentTrap;
  }

  // Handle keydown in focus trap
  handleTrapKeydown(e, focusableElements) {
    if (e.key !== 'Tab') return;

    const currentIndex = focusableElements.indexOf(document.activeElement);
    
    if (e.shiftKey) {
      // Shift+Tab - go to previous
      if (currentIndex <= 0) {
        e.preventDefault();
        focusableElements[focusableElements.length - 1].focus();
      }
    } else {
      // Tab - go to next
      if (currentIndex >= focusableElements.length - 1) {
        e.preventDefault();
        focusableElements[0].focus();
      }
    }
  }

  // Get focusable elements in container
  getFocusableElements(container) {
    const focusableSelectors = [
      'button:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      'textarea:not([disabled])',
      'a[href]',
      '[tabindex]:not([tabindex="-1"])',
      '[contenteditable]'
    ].join(', ');

    return Array.from(container.querySelectorAll(focusableSelectors))
      .filter(el => this.isVisible(el));
  }

  // Check if element is visible
  isVisible(element) {
    const style = window.getComputedStyle(element);
    return style.display !== 'none' && 
           style.visibility !== 'hidden' && 
           style.opacity !== '0';
  }

  // Focus element by selector
  focusElement(selector) {
    const element = document.querySelector(selector);
    if (element && element.focus) {
      element.focus();
      return true;
    }
    return false;
  }

  // Focus first element in container
  focusFirst(container) {
    const focusableElements = this.getFocusableElements(container || document.body);
    if (focusableElements.length > 0) {
      focusableElements[0].focus();
      return true;
    }
    return false;
  }
}

/**
 * Keyboard navigation provider
 */
export function KeyboardNavigationProvider({ children, onShortcut }) {
  const [shortcuts, setShortcuts] = useState(DEFAULT_SHORTCUTS);
  const [focusManager] = useState(new FocusManager());
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Register custom shortcut
  const registerShortcut = useCallback((key, shortcut) => {
    setShortcuts(prev => ({
      ...prev,
      [key]: shortcut
    }));
  }, []);

  // Unregister shortcut
  const unregisterShortcut = useCallback((key) => {
    setShortcuts(prev => {
      const updated = { ...prev };
      delete updated[key];
      return updated;
    });
  }, []);

  // Check if shortcut is active
  const isShortcutActive = useCallback((key) => {
    return key in shortcuts;
  }, [shortcuts]);

  // Parse key combination
  const parseKeyCombo = (e) => {
    const parts = [];
    
    if (e.ctrlKey || e.metaKey) parts.push('ctrl');
    if (e.altKey) parts.push('alt');
    if (e.shiftKey) parts.push('shift');
    
    // Handle special keys
    const key = e.key.toLowerCase();
    if (key === ' ') parts.push('space');
    else if (key === 'escape') parts.push('escape');
    else if (key === 'enter') parts.push('enter');
    else if (key === 'arrowup') parts.push('up');
    else if (key === 'arrowdown') parts.push('down');
    else if (key === 'arrowleft') parts.push('left');
    else if (key === 'arrowright') parts.push('right');
    else if (key === 'home') parts.push('home');
    else if (key === 'end') parts.push('end');
    else if (key === 'pageup') parts.push('pageup');
    else if (key === 'pagedown') parts.push('pagedown');
    else if (key === 'f11') parts.push('f11');
    else if (key === '/') parts.push('slash');
    else parts.push(key);
    
    return parts.join('+');
  };

  // Handle keyboard events
  useEffect(() => {
    const handleKeyDown = (e) => {
      // Skip if focus is in input elements (unless it's a global shortcut)
      const target = e.target;
      const isInputElement = target.tagName === 'INPUT' || 
                            target.tagName === 'TEXTAREA' || 
                            target.contentEditable === 'true';
      
      const keyCombo = parseKeyCombo(e);
      const shortcut = shortcuts[keyCombo];
      
      if (shortcut) {
        // Check if this is a global shortcut or if we should skip input elements
        const isGlobalShortcut = ['escape', 'f11', 'ctrl+shift+k'].includes(keyCombo);
        
        if (isGlobalShortcut || !isInputElement) {
          e.preventDefault();
          e.stopPropagation();
          
          // Call the shortcut handler
          if (onShortcut) {
            onShortcut(shortcut.action, shortcut.payload, e);
          }
        }
      }

      // Handle special modal/overlay closing
      if (keyCombo === 'escape' && isModalOpen) {
        setIsModalOpen(false);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [shortcuts, onShortcut, isModalOpen]);

  // Provide skip links for accessibility
  const addSkipLinks = useCallback(() => {
    // Check if skip links already exist
    if (document.querySelector('.skip-links')) return;

    const skipLinks = document.createElement('div');
    skipLinks.className = 'skip-links';
    skipLinks.innerHTML = `
      <a href="#main-content" class="skip-link">Skip to main content</a>
      <a href="#navigation" class="skip-link">Skip to navigation</a>
      <a href="#sidebar" class="skip-link">Skip to sidebar</a>
    `;
    
    document.body.insertBefore(skipLinks, document.body.firstChild);
  }, []);

  // Add skip links on mount
  useEffect(() => {
    addSkipLinks();
  }, [addSkipLinks]);

  const value = {
    registerShortcut,
    unregisterShortcut,
    isShortcutActive,
    shortcuts,
    focusManager,
    setIsModalOpen
  };

  return (
    <KeyboardNavigationContext.Provider value={value}>
      {children}
    </KeyboardNavigationContext.Provider>
  );
}

/**
 * Hook to use keyboard navigation
 */
export function useKeyboardNavigation() {
  const context = useContext(KeyboardNavigationContext);
  if (!context) {
    throw new Error('useKeyboardNavigation must be used within KeyboardNavigationProvider');
  }
  return context;
}

/**
 * Hook for component-specific shortcuts
 */
export function useShortcuts(shortcutMap, dependencies = []) {
  const { registerShortcut, unregisterShortcut } = useKeyboardNavigation();

  useEffect(() => {
    // Register shortcuts
    Object.entries(shortcutMap).forEach(([key, shortcut]) => {
      registerShortcut(key, shortcut);
    });

    // Cleanup on unmount
    return () => {
      Object.keys(shortcutMap).forEach(key => {
        unregisterShortcut(key);
      });
    };
  }, [registerShortcut, unregisterShortcut, ...dependencies]);
}

/**
 * Hook for focus trapping
 */
export function useFocusTrap(isActive, containerRef) {
  const { focusManager } = useKeyboardNavigation();

  useEffect(() => {
    if (isActive && containerRef.current) {
      focusManager.pushFocusTrap(containerRef.current);
      return () => focusManager.popFocusTrap();
    }
  }, [isActive, containerRef, focusManager]);
}

/**
 * Keyboard shortcuts help component
 */
export function KeyboardShortcutsHelp({ isOpen, onClose, className = '' }) {
  const { shortcuts } = useKeyboardNavigation();
  const containerRef = React.useRef();

  // Use focus trap when modal is open
  useFocusTrap(isOpen, containerRef);

  if (!isOpen) return null;

  // Group shortcuts by category
  const groupedShortcuts = Object.entries(shortcuts).reduce((groups, [key, shortcut]) => {
    let category = 'General';
    
    if (shortcut.action.includes('navigate')) category = 'Navigation';
    else if (shortcut.action.includes('toggle')) category = 'Interface';
    else if (shortcut.action.includes('focus')) category = 'Accessibility';
    else if (shortcut.action.includes('command') || shortcut.action.includes('search')) category = 'Commands';
    
    if (!groups[category]) groups[category] = [];
    groups[category].push({ key, ...shortcut });
    
    return groups;
  }, {});

  return (
    <div className={`shortcuts-modal-overlay ${className}`} onClick={onClose}>
      <div 
        ref={containerRef}
        className="shortcuts-modal"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="shortcuts-title"
        aria-modal="true"
      >
        <div className="shortcuts-header">
          <h2 id="shortcuts-title">Keyboard Shortcuts</h2>
          <button 
            className="shortcuts-close"
            onClick={onClose}
            aria-label="Close shortcuts help"
          >
            <i className="fas fa-times" />
          </button>
        </div>
        
        <div className="shortcuts-content">
          {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
            <div key={category} className="shortcuts-category">
              <h3 className="category-title">{category}</h3>
              <div className="shortcuts-list">
                {categoryShortcuts.map(({ key, description }) => (
                  <div key={key} className="shortcut-item">
                    <kbd className="shortcut-key">{key.replace(/\+/g, ' + ')}</kbd>
                    <span className="shortcut-description">{description}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
        
        <div className="shortcuts-footer">
          <p>Press <kbd>Ctrl + Shift + K</kbd> to show/hide this help</p>
        </div>
      </div>
    </div>
  );
}

export default KeyboardNavigationProvider;
