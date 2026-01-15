// src/components/layout/ResponsiveLayout.js
// LEGION Enterprise Dashboard - Responsive Layout System

import React, { useState, useEffect, useContext, createContext } from 'react';

/**
 * Layout Context for sharing responsive state
 */
const LayoutContext = createContext({
  screenSize: 'desktop',
  isMobile: false,
  isTablet: false,
  isDesktop: true,
  sidebarCollapsed: false,
  setSidebarCollapsed: () => {},
  orientation: 'landscape',
  containerWidth: 1200,
  breakpoints: {}
});

/**
 * Breakpoint definitions
 */
export const BREAKPOINTS = {
  mobile: 480,
  tablet: 768,
  desktop: 1024,
  large: 1200,
  xlarge: 1440
};

/**
 * Hook for responsive layout functionality
 */
export function useResponsiveLayout() {
  const [screenSize, setScreenSize] = useState('desktop');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [orientation, setOrientation] = useState('landscape');
  const [containerWidth, setContainerWidth] = useState(1200);

  useEffect(() => {
    const updateLayout = () => {
      const width = window.innerWidth;
      const height = window.innerHeight;
      
      // Determine screen size
      let newScreenSize = 'desktop';
      if (width <= BREAKPOINTS.mobile) {
        newScreenSize = 'mobile';
      } else if (width <= BREAKPOINTS.tablet) {
        newScreenSize = 'tablet';
      } else if (width <= BREAKPOINTS.desktop) {
        newScreenSize = 'desktop';
      } else if (width <= BREAKPOINTS.large) {
        newScreenSize = 'large';
      } else {
        newScreenSize = 'xlarge';
      }
      
      // Update orientation
      const newOrientation = width > height ? 'landscape' : 'portrait';
      
      // Auto-collapse sidebar on mobile
      if (newScreenSize === 'mobile' && !sidebarCollapsed) {
        setSidebarCollapsed(true);
      }
      
      setScreenSize(newScreenSize);
      setOrientation(newOrientation);
      setContainerWidth(width);
    };

    // Initial layout calculation
    updateLayout();

    // Listen for resize events
    window.addEventListener('resize', updateLayout);
    window.addEventListener('orientationchange', () => {
      setTimeout(updateLayout, 100); // Delay for orientation change
    });

    return () => {
      window.removeEventListener('resize', updateLayout);
      window.removeEventListener('orientationchange', updateLayout);
    };
  }, [sidebarCollapsed]);

  // Load persisted sidebar state
  useEffect(() => {
    try {
      const saved = localStorage.getItem('legion_sidebar_collapsed');
      if (saved !== null) {
        setSidebarCollapsed(JSON.parse(saved));
      }
    } catch (error) {
      console.warn('Failed to load sidebar state:', error);
    }
  }, []);

  // Persist sidebar state
  useEffect(() => {
    try {
      localStorage.setItem('legion_sidebar_collapsed', JSON.stringify(sidebarCollapsed));
    } catch (error) {
      console.warn('Failed to save sidebar state:', error);
    }
  }, [sidebarCollapsed]);

  const isMobile = screenSize === 'mobile';
  const isTablet = screenSize === 'tablet';
  const isDesktop = ['desktop', 'large', 'xlarge'].includes(screenSize);

  return {
    screenSize,
    isMobile,
    isTablet,
    isDesktop,
    sidebarCollapsed,
    setSidebarCollapsed,
    orientation,
    containerWidth,
    breakpoints: BREAKPOINTS
  };
}

/**
 * Responsive Layout Provider Component
 */
export function ResponsiveLayoutProvider({ children }) {
  const layoutState = useResponsiveLayout();

  return (
    <LayoutContext.Provider value={layoutState}>
      {children}
    </LayoutContext.Provider>
  );
}

/**
 * Hook to use layout context
 */
export function useLayout() {
  const context = useContext(LayoutContext);
  if (!context) {
    throw new Error('useLayout must be used within ResponsiveLayoutProvider');
  }
  return context;
}

/**
 * Grid System Component
 */
export function Grid({ children, className = '', container = false, item = false, spacing = 2, ...props }) {
  const { screenSize } = useLayout();
  
  const baseClass = container ? 'grid-container' : item ? 'grid-item' : 'grid';
  const spacingClass = container ? `spacing-${spacing}` : '';
  const responsiveClass = `responsive-${screenSize}`;
  
  return (
    <div 
      className={`${baseClass} ${spacingClass} ${responsiveClass} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

/**
 * Responsive Container Component
 */
export function Container({ children, className = '', maxWidth = 'large', fluid = false }) {
  const { containerWidth } = useLayout();
  
  const containerClass = fluid ? 'container-fluid' : 'container';
  const maxWidthClass = `max-width-${maxWidth}`;
  
  return (
    <div className={`${containerClass} ${maxWidthClass} ${className}`}>
      {children}
    </div>
  );
}

/**
 * Responsive Columns Component
 */
export function Columns({ children, className = '', ...props }) {
  return (
    <div className={`columns ${className}`} {...props}>
      {children}
    </div>
  );
}

export function Column({ 
  children, 
  className = '', 
  size = 'auto',
  mobile = null,
  tablet = null,
  desktop = null,
  ...props 
}) {
  const { screenSize } = useLayout();
  
  // Determine column size based on screen size
  let columnSize = size;
  if (screenSize === 'mobile' && mobile) columnSize = mobile;
  else if (screenSize === 'tablet' && tablet) columnSize = tablet;
  else if (['desktop', 'large', 'xlarge'].includes(screenSize) && desktop) columnSize = desktop;
  
  const columnClass = `column column-${columnSize}`;
  
  return (
    <div className={`${columnClass} ${className}`} {...props}>
      {children}
    </div>
  );
}

/**
 * Responsive Visibility Component
 */
export function Show({ children, on = [], only = null }) {
  const { screenSize } = useLayout();
  
  if (only && screenSize !== only) return null;
  if (on.length > 0 && !on.includes(screenSize)) return null;
  
  return children;
}

export function Hide({ children, on = [], except = null }) {
  const { screenSize } = useLayout();
  
  if (except && screenSize === except) return null;
  if (on.length > 0 && on.includes(screenSize)) return null;
  
  return children;
}

/**
 * Responsive Text Component
 */
export function ResponsiveText({ 
  children, 
  className = '',
  size = 'medium',
  mobileSize = null,
  tabletSize = null,
  desktopSize = null 
}) {
  const { screenSize } = useLayout();
  
  let textSize = size;
  if (screenSize === 'mobile' && mobileSize) textSize = mobileSize;
  else if (screenSize === 'tablet' && tabletSize) textSize = tabletSize;
  else if (['desktop', 'large', 'xlarge'].includes(screenSize) && desktopSize) textSize = desktopSize;
  
  return (
    <span className={`text-${textSize} ${className}`}>
      {children}
    </span>
  );
}

/**
 * Responsive Spacer Component
 */
export function Spacer({ 
  size = 'medium',
  mobileSize = null,
  tabletSize = null,
  desktopSize = null,
  vertical = false,
  className = ''
}) {
  const { screenSize } = useLayout();
  
  let spacerSize = size;
  if (screenSize === 'mobile' && mobileSize) spacerSize = mobileSize;
  else if (screenSize === 'tablet' && tabletSize) spacerSize = tabletSize;
  else if (['desktop', 'large', 'xlarge'].includes(screenSize) && desktopSize) spacerSize = desktopSize;
  
  const direction = vertical ? 'vertical' : 'horizontal';
  
  return <div className={`spacer spacer-${direction} spacer-${spacerSize} ${className}`} />;
}

/**
 * Layout Debug Component (development only)
 */
export function LayoutDebug() {
  const layout = useLayout();
  
  if (process.env.NODE_ENV !== 'development') return null;
  
  return (
    <div className="layout-debug">
      <div className="debug-info">
        <strong>Layout Debug:</strong>
        <span>Screen: {layout.screenSize}</span>
        <span>Width: {layout.containerWidth}px</span>
        <span>Orientation: {layout.orientation}</span>
        <span>Sidebar: {layout.sidebarCollapsed ? 'Collapsed' : 'Expanded'}</span>
      </div>
    </div>
  );
}

/**
 * Media Query Hook
 */
export function useMediaQuery(query) {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handler = (event) => setMatches(event.matches);
    mediaQuery.addEventListener('change', handler);

    return () => mediaQuery.removeEventListener('change', handler);
  }, [query]);

  return matches;
}

/**
 * Viewport Hook
 */
export function useViewport() {
  const [viewport, setViewport] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0
  });

  useEffect(() => {
    const updateViewport = () => {
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight
      });
    };

    window.addEventListener('resize', updateViewport);
    return () => window.removeEventListener('resize', updateViewport);
  }, []);

  return viewport;
}

export default ResponsiveLayoutProvider;
