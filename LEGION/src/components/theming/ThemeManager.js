// src/components/theming/ThemeManager.js
// LEGION Enterprise Dashboard - Theme and Customization System

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';

/**
 * Theme context
 */
const ThemeContext = createContext({
  currentTheme: 'legion-default',
  themes: {},
  setTheme: () => {},
  customizeTheme: () => {},
  resetTheme: () => {},
  exportTheme: () => {},
  importTheme: () => {},
  isDarkMode: false,
  toggleDarkMode: () => {},
  accentColor: '#3182ce',
  setAccentColor: () => {},
  fontScale: 1,
  setFontScale: () => {},
  layoutDensity: 'comfortable',
  setLayoutDensity: () => {}
});

/**
 * Built-in themes
 */
const BUILT_IN_THEMES = {
  'legion-default': {
    name: 'LEGION Default',
    description: 'The default LEGION Enterprise theme',
    colors: {
      primary: '#1a365d',
      secondary: '#2d3748',
      accent: '#3182ce',
      success: '#38a169',
      warning: '#d69e2e',
      error: '#e53e3e',
      background: '#ffffff',
      surface: '#f7fafc',
      border: '#e2e8f0',
      text: '#1a202c',
      textMuted: '#4a5568'
    },
    fonts: {
      primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace'
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      xxl: '48px'
    },
    borderRadius: {
      sm: '4px',
      md: '6px',
      lg: '8px',
      xl: '12px'
    },
    shadows: {
      sm: '0 1px 3px rgba(0, 0, 0, 0.1)',
      md: '0 4px 6px rgba(0, 0, 0, 0.1)',
      lg: '0 10px 15px rgba(0, 0, 0, 0.1)'
    }
  },
  'legion-dark': {
    name: 'LEGION Dark',
    description: 'Dark mode variant of the LEGION theme',
    colors: {
      primary: '#2b6cb0',
      secondary: '#4a5568',
      accent: '#63b3ed',
      success: '#68d391',
      warning: '#fbb042',
      error: '#fc8181',
      background: '#1a202c',
      surface: '#2d3748',
      border: '#4a5568',
      text: '#f7fafc',
      textMuted: '#a0aec0'
    },
    fonts: {
      primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace'
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      xxl: '48px'
    },
    borderRadius: {
      sm: '4px',
      md: '6px',
      lg: '8px',
      xl: '12px'
    },
    shadows: {
      sm: '0 1px 3px rgba(0, 0, 0, 0.3)',
      md: '0 4px 6px rgba(0, 0, 0, 0.3)',
      lg: '0 10px 15px rgba(0, 0, 0, 0.3)'
    }
  },
  'legion-blue': {
    name: 'LEGION Blue',
    description: 'Cool blue theme for focused work',
    colors: {
      primary: '#1e3a8a',
      secondary: '#1e40af',
      accent: '#3b82f6',
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      background: '#f8fafc',
      surface: '#f1f5f9',
      border: '#cbd5e1',
      text: '#0f172a',
      textMuted: '#475569'
    },
    fonts: {
      primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace'
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      xxl: '48px'
    },
    borderRadius: {
      sm: '4px',
      md: '6px',
      lg: '8px',
      xl: '12px'
    },
    shadows: {
      sm: '0 1px 3px rgba(59, 130, 246, 0.1)',
      md: '0 4px 6px rgba(59, 130, 246, 0.1)',
      lg: '0 10px 15px rgba(59, 130, 246, 0.1)'
    }
  },
  'legion-green': {
    name: 'LEGION Green',
    description: 'Natural green theme for productivity',
    colors: {
      primary: '#14532d',
      secondary: '#166534',
      accent: '#22c55e',
      success: '#16a34a',
      warning: '#eab308',
      error: '#dc2626',
      background: '#f9fafb',
      surface: '#f3f4f6',
      border: '#d1d5db',
      text: '#111827',
      textMuted: '#6b7280'
    },
    fonts: {
      primary: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      mono: '"SF Mono", "Monaco", "Inconsolata", "Roboto Mono", monospace'
    },
    spacing: {
      xs: '4px',
      sm: '8px',
      md: '16px',
      lg: '24px',
      xl: '32px',
      xxl: '48px'
    },
    borderRadius: {
      sm: '4px',
      md: '6px',
      lg: '8px',
      xl: '12px'
    },
    shadows: {
      sm: '0 1px 3px rgba(34, 197, 94, 0.1)',
      md: '0 4px 6px rgba(34, 197, 94, 0.1)',
      lg: '0 10px 15px rgba(34, 197, 94, 0.1)'
    }
  }
};

/**
 * Theme storage key
 */
const THEME_STORAGE_KEY = 'legion_theme_preferences';

/**
 * Theme manager provider
 */
export function ThemeProvider({ children }) {
  const [currentTheme, setCurrentTheme] = useState('legion-default');
  const [themes, setThemes] = useState(BUILT_IN_THEMES);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [accentColor, setAccentColorState] = useState('#3182ce');
  const [fontScale, setFontScaleState] = useState(1);
  const [layoutDensity, setLayoutDensityState] = useState('comfortable');

  // Load theme preferences on mount
  useEffect(() => {
    const loadThemePreferences = () => {
      try {
        const saved = localStorage.getItem(THEME_STORAGE_KEY);
        if (saved) {
          const preferences = JSON.parse(saved);
          setCurrentTheme(preferences.currentTheme || 'legion-default');
          setIsDarkMode(preferences.isDarkMode || false);
          setAccentColorState(preferences.accentColor || '#3182ce');
          setFontScaleState(preferences.fontScale || 1);
          setLayoutDensityState(preferences.layoutDensity || 'comfortable');
          
          // Load custom themes
          if (preferences.customThemes) {
            setThemes(prev => ({ ...prev, ...preferences.customThemes }));
          }
        }
      } catch (error) {
        console.warn('Failed to load theme preferences:', error);
      }

      // Detect system preferences
      detectSystemPreferences();
    };

    loadThemePreferences();
  }, []);

  // Detect system theme preferences
  const detectSystemPreferences = useCallback(() => {
    // Detect system dark mode preference
    const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
    if (darkModeQuery.matches) {
      setIsDarkMode(true);
      setCurrentTheme('legion-dark');
    }

    // Listen for system theme changes
    const handleSystemThemeChange = (e) => {
      setIsDarkMode(e.matches);
      setCurrentTheme(e.matches ? 'legion-dark' : 'legion-default');
    };

    darkModeQuery.addEventListener('change', handleSystemThemeChange);
    return () => darkModeQuery.removeEventListener('change', handleSystemThemeChange);
  }, []);

  // Save preferences when they change
  useEffect(() => {
    const preferences = {
      currentTheme,
      isDarkMode,
      accentColor,
      fontScale,
      layoutDensity,
      customThemes: Object.fromEntries(
        Object.entries(themes).filter(([key]) => !BUILT_IN_THEMES[key])
      )
    };

    try {
      localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(preferences));
    } catch (error) {
      console.warn('Failed to save theme preferences:', error);
    }
  }, [currentTheme, themes, isDarkMode, accentColor, fontScale, layoutDensity]);

  // Apply theme to document
  useEffect(() => {
    const applyTheme = () => {
      const theme = themes[currentTheme] || themes['legion-default'];
      const root = document.documentElement;

      // Apply colors
      Object.entries(theme.colors).forEach(([key, value]) => {
        root.style.setProperty(`--color-${key}`, value);
      });

      // Apply fonts
      Object.entries(theme.fonts).forEach(([key, value]) => {
        root.style.setProperty(`--font-${key}`, value);
      });

      // Apply spacing
      Object.entries(theme.spacing).forEach(([key, value]) => {
        root.style.setProperty(`--spacing-${key}`, value);
      });

      // Apply border radius
      Object.entries(theme.borderRadius).forEach(([key, value]) => {
        root.style.setProperty(`--radius-${key}`, value);
      });

      // Apply shadows
      Object.entries(theme.shadows).forEach(([key, value]) => {
        root.style.setProperty(`--shadow-${key}`, value);
      });

      // Apply custom accent color
      root.style.setProperty('--accent-custom', accentColor);

      // Apply font scale
      root.style.setProperty('--font-scale', fontScale.toString());
      root.style.fontSize = `${fontScale * 16}px`;

      // Apply layout density
      const densityMultiplier = {
        compact: 0.8,
        comfortable: 1,
        spacious: 1.2
      }[layoutDensity] || 1;
      
      root.style.setProperty('--density-multiplier', densityMultiplier.toString());

      // Apply theme class
      root.className = root.className.replace(/theme-\w+/g, '');
      root.classList.add(`theme-${currentTheme}`);
      
      // Apply dark mode class
      if (isDarkMode) {
        root.classList.add('dark-mode');
      } else {
        root.classList.remove('dark-mode');
      }

      // Apply density class
      root.className = root.className.replace(/density-\w+/g, '');
      root.classList.add(`density-${layoutDensity}`);
    };

    applyTheme();
  }, [currentTheme, themes, isDarkMode, accentColor, fontScale, layoutDensity]);

  // Theme management functions
  const setTheme = useCallback((themeId) => {
    if (themes[themeId]) {
      setCurrentTheme(themeId);
      // Auto-detect if it's a dark theme
      const theme = themes[themeId];
      setIsDarkMode(theme.name.toLowerCase().includes('dark'));
    }
  }, [themes]);

  const customizeTheme = useCallback((themeId, customizations) => {
    setThemes(prev => ({
      ...prev,
      [themeId]: {
        ...prev[themeId],
        ...customizations,
        name: customizations.name || prev[themeId]?.name || 'Custom Theme'
      }
    }));
  }, []);

  const resetTheme = useCallback((themeId) => {
    if (BUILT_IN_THEMES[themeId]) {
      setThemes(prev => ({
        ...prev,
        [themeId]: BUILT_IN_THEMES[themeId]
      }));
    }
  }, []);

  const exportTheme = useCallback((themeId) => {
    const theme = themes[themeId];
    if (theme) {
      const themeData = {
        ...theme,
        exportedAt: new Date().toISOString(),
        version: '1.0'
      };
      
      const blob = new Blob([JSON.stringify(themeData, null, 2)], {
        type: 'application/json'
      });
      
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${theme.name.toLowerCase().replace(/\s+/g, '-')}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    }
  }, [themes]);

  const importTheme = useCallback((file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      
      reader.onload = (e) => {
        try {
          const themeData = JSON.parse(e.target.result);
          
          // Validate theme structure
          if (!themeData.name || !themeData.colors) {
            throw new Error('Invalid theme file structure');
          }
          
          // Generate unique ID
          const themeId = `custom-${Date.now()}`;
          
          setThemes(prev => ({
            ...prev,
            [themeId]: themeData
          }));
          
          resolve(themeId);
        } catch (error) {
          reject(error);
        }
      };
      
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }, []);

  const toggleDarkMode = useCallback(() => {
    setIsDarkMode(prev => {
      const newDarkMode = !prev;
      // Switch to appropriate theme
      if (newDarkMode) {
        setCurrentTheme('legion-dark');
      } else {
        setCurrentTheme('legion-default');
      }
      return newDarkMode;
    });
  }, []);

  const setAccentColor = useCallback((color) => {
    setAccentColorState(color);
  }, []);

  const setFontScale = useCallback((scale) => {
    setFontScaleState(Math.max(0.75, Math.min(1.5, scale)));
  }, []);

  const setLayoutDensity = useCallback((density) => {
    if (['compact', 'comfortable', 'spacious'].includes(density)) {
      setLayoutDensityState(density);
    }
  }, []);

  const value = {
    currentTheme,
    themes,
    setTheme,
    customizeTheme,
    resetTheme,
    exportTheme,
    importTheme,
    isDarkMode,
    toggleDarkMode,
    accentColor,
    setAccentColor,
    fontScale,
    setFontScale,
    layoutDensity,
    setLayoutDensity
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
}

/**
 * Hook to use theme context
 */
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

/**
 * Theme selector component
 */
export function ThemeSelector({ className = '' }) {
  const { currentTheme, themes, setTheme } = useTheme();

  return (
    <div className={`theme-selector ${className}`}>
      <label className="theme-selector-label">
        Choose Theme
      </label>
      <div className="theme-options">
        {Object.entries(themes).map(([themeId, theme]) => (
          <button
            key={themeId}
            className={`theme-option ${currentTheme === themeId ? 'active' : ''}`}
            onClick={() => setTheme(themeId)}
            title={theme.description}
          >
            <div 
              className="theme-preview"
              style={{
                background: `linear-gradient(45deg, ${theme.colors.primary}, ${theme.colors.accent})`
              }}
            />
            <span className="theme-name">{theme.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

/**
 * Color picker component
 */
export function ColorPicker({ 
  label, 
  value, 
  onChange, 
  className = '',
  presetColors = []
}) {
  return (
    <div className={`color-picker ${className}`}>
      <label className="color-picker-label">{label}</label>
      <div className="color-picker-controls">
        <input
          type="color"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="color-input"
        />
        <input
          type="text"
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="color-text-input"
          placeholder="#000000"
        />
      </div>
      {presetColors.length > 0 && (
        <div className="color-presets">
          {presetColors.map((color) => (
            <button
              key={color}
              className={`color-preset ${value === color ? 'active' : ''}`}
              style={{ backgroundColor: color }}
              onClick={() => onChange(color)}
              title={color}
              aria-label={`Set color to ${color}`}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default ThemeProvider;
