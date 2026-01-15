// src/components/theming/ThemeCustomizer.js
// LEGION Enterprise Dashboard - Theme Customization Panel

import React, { useState, useCallback } from 'react';
import { useTheme, ColorPicker } from './ThemeManager';
import './ThemeCustomizer.css';

/**
 * Theme customization panel component
 */
export function ThemeCustomizer({ isOpen = false, onClose = () => {} }) {
  const {
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
  } = useTheme();

  const [activeTab, setActiveTab] = useState('themes');
  const [customColors, setCustomColors] = useState({});
  const [isImporting, setIsImporting] = useState(false);

  const currentThemeData = themes[currentTheme] || themes['legion-default'];

  // Handle color customization
  const handleColorChange = useCallback((colorKey, value) => {
    setCustomColors(prev => ({
      ...prev,
      [colorKey]: value
    }));

    // Apply customization to current theme
    customizeTheme(currentTheme, {
      colors: {
        ...currentThemeData.colors,
        [colorKey]: value
      }
    });
  }, [currentTheme, currentThemeData, customizeTheme]);

  // Handle font scale change
  const handleFontScaleChange = useCallback((e) => {
    const scale = parseFloat(e.target.value);
    setFontScale(scale);
  }, [setFontScale]);

  // Handle theme import
  const handleThemeImport = useCallback(async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsImporting(true);
    try {
      const themeId = await importTheme(file);
      setTheme(themeId);
      alert('Theme imported successfully!');
    } catch (error) {
      alert(`Failed to import theme: ${error.message}`);
    } finally {
      setIsImporting(false);
      e.target.value = ''; // Reset file input
    }
  }, [importTheme, setTheme]);

  // Preset accent colors
  const accentPresets = [
    '#3182ce', '#e53e3e', '#38a169', '#d69e2e', 
    '#805ad5', '#dd6b20', '#3182ce', '#319795'
  ];

  // Color customization sections
  const colorSections = [
    {
      title: 'Primary Colors',
      colors: ['primary', 'secondary', 'accent']
    },
    {
      title: 'Status Colors',
      colors: ['success', 'warning', 'error']
    },
    {
      title: 'Background Colors',
      colors: ['background', 'surface', 'border']
    },
    {
      title: 'Text Colors',
      colors: ['text', 'textMuted']
    }
  ];

  if (!isOpen) return null;

  return (
    <div className="theme-customizer-overlay" onClick={onClose}>
      <div className="theme-customizer" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="customizer-header">
          <h2 className="customizer-title">Theme Customization</h2>
          <button
            className="customizer-close"
            onClick={onClose}
            aria-label="Close theme customizer"
          >
            ×
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="customizer-tabs">
          {[
            { id: 'themes', label: 'Themes', icon: '🎨' },
            { id: 'colors', label: 'Colors', icon: '🌈' },
            { id: 'layout', label: 'Layout', icon: '📐' },
            { id: 'export', label: 'Import/Export', icon: '💾' }
          ].map((tab) => (
            <button
              key={tab.id}
              className={`customizer-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="customizer-content">
          {/* Themes Tab */}
          {activeTab === 'themes' && (
            <div className="tab-content">
              <div className="section">
                <h3 className="section-title">Built-in Themes</h3>
                <div className="theme-grid">
                  {Object.entries(themes).map(([themeId, theme]) => (
                    <button
                      key={themeId}
                      className={`theme-card ${currentTheme === themeId ? 'active' : ''}`}
                      onClick={() => setTheme(themeId)}
                    >
                      <div 
                        className="theme-card-preview"
                        style={{
                          background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.accent})`
                        }}
                      />
                      <div className="theme-card-info">
                        <h4 className="theme-card-name">{theme.name}</h4>
                        <p className="theme-card-description">{theme.description}</p>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="section">
                <h3 className="section-title">Quick Settings</h3>
                <div className="quick-settings">
                  <label className="setting-item">
                    <input
                      type="checkbox"
                      checked={isDarkMode}
                      onChange={toggleDarkMode}
                    />
                    <span className="setting-label">Dark Mode</span>
                  </label>
                </div>
              </div>
            </div>
          )}

          {/* Colors Tab */}
          {activeTab === 'colors' && (
            <div className="tab-content">
              <div className="section">
                <h3 className="section-title">Accent Color</h3>
                <ColorPicker
                  label="Primary Accent"
                  value={accentColor}
                  onChange={setAccentColor}
                  presetColors={accentPresets}
                />
              </div>

              {colorSections.map((section) => (
                <div key={section.title} className="section">
                  <h3 className="section-title">{section.title}</h3>
                  <div className="color-grid">
                    {section.colors.map((colorKey) => (
                      <ColorPicker
                        key={colorKey}
                        label={colorKey.charAt(0).toUpperCase() + colorKey.slice(1)}
                        value={customColors[colorKey] || currentThemeData.colors[colorKey]}
                        onChange={(value) => handleColorChange(colorKey, value)}
                      />
                    ))}
                  </div>
                </div>
              ))}

              <div className="section">
                <div className="section-actions">
                  <button
                    className="action-button secondary"
                    onClick={() => resetTheme(currentTheme)}
                  >
                    Reset Colors
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Layout Tab */}
          {activeTab === 'layout' && (
            <div className="tab-content">
              <div className="section">
                <h3 className="section-title">Font Scale</h3>
                <div className="scale-control">
                  <input
                    type="range"
                    min="0.75"
                    max="1.5"
                    step="0.05"
                    value={fontScale}
                    onChange={handleFontScaleChange}
                    className="scale-slider"
                  />
                  <div className="scale-display">
                    <span className="scale-value">{Math.round(fontScale * 100)}%</span>
                    <div className="scale-preview" style={{ fontSize: `${fontScale}em` }}>
                      Sample Text
                    </div>
                  </div>
                </div>
              </div>

              <div className="section">
                <h3 className="section-title">Layout Density</h3>
                <div className="density-options">
                  {[
                    { value: 'compact', label: 'Compact', description: 'More content, less spacing' },
                    { value: 'comfortable', label: 'Comfortable', description: 'Balanced spacing' },
                    { value: 'spacious', label: 'Spacious', description: 'More spacing, easier reading' }
                  ].map((option) => (
                    <label key={option.value} className="density-option">
                      <input
                        type="radio"
                        name="density"
                        value={option.value}
                        checked={layoutDensity === option.value}
                        onChange={() => setLayoutDensity(option.value)}
                      />
                      <div className="density-info">
                        <span className="density-label">{option.label}</span>
                        <span className="density-description">{option.description}</span>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Import/Export Tab */}
          {activeTab === 'export' && (
            <div className="tab-content">
              <div className="section">
                <h3 className="section-title">Export Theme</h3>
                <p className="section-description">
                  Save your current theme configuration to a file.
                </p>
                <button
                  className="action-button primary"
                  onClick={() => exportTheme(currentTheme)}
                >
                  Export Current Theme
                </button>
              </div>

              <div className="section">
                <h3 className="section-title">Import Theme</h3>
                <p className="section-description">
                  Load a theme configuration from a file.
                </p>
                <div className="import-control">
                  <input
                    type="file"
                    accept=".json"
                    onChange={handleThemeImport}
                    disabled={isImporting}
                    className="file-input"
                    id="theme-import"
                  />
                  <label htmlFor="theme-import" className="file-label">
                    {isImporting ? 'Importing...' : 'Choose Theme File'}
                  </label>
                </div>
              </div>

              <div className="section">
                <h3 className="section-title">Reset Everything</h3>
                <p className="section-description">
                  Reset all customizations to default values.
                </p>
                <button
                  className="action-button danger"
                  onClick={() => {
                    if (confirm('Are you sure you want to reset all customizations?')) {
                      setTheme('legion-default');
                      setFontScale(1);
                      setLayoutDensity('comfortable');
                      setCustomColors({});
                    }
                  }}
                >
                  Reset All Settings
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

/**
 * Theme customizer toggle button
 */
export function ThemeCustomizerButton({ className = '' }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        className={`theme-customizer-button ${className}`}
        onClick={() => setIsOpen(true)}
        title="Customize Theme"
        aria-label="Open theme customizer"
      >
        🎨
      </button>
      <ThemeCustomizer
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  );
}

export default ThemeCustomizer;
