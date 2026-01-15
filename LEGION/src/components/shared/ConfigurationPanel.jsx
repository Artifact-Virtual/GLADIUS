// src/components/shared/ConfigurationPanel.jsx

import React, { useState, useEffect } from 'react';

const ConfigurationPanel = ({
  // Panel configuration
  title = 'Configuration Panel',
  description = 'Manage system settings and preferences',
  variant = 'default', // 'default', 'minimal', 'detailed', 'compact'
  size = 'medium', // 'small', 'medium', 'large', 'full'
  
  // Settings configuration
  sections = [],
  settings = {},
  schema = {},
  
  // Display options
  collapsible = true,
  searchable = true,
  tabbed = false,
  showDescriptions = true,
  showDefaults = true,
  showValidation = true,
  
  // Behavior options
  autoSave = false,
  saveDelay = 1000,
  resetable = true,
  exportable = false,
  importable = false,
  
  // Event handlers
  onChange = null,
  onSave = null,
  onReset = null,
  onExport = null,
  onImport = null,
  onValidate = null,
  
  // Custom styling
  className = '',
  style = {}
}) => {
  const [currentSettings, setCurrentSettings] = useState(settings);
  const [expandedSections, setExpandedSections] = useState(new Set());
  const [activeTab, setActiveTab] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [validationErrors, setValidationErrors] = useState({});
  const [isDirty, setIsDirty] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Auto-save functionality
  useEffect(() => {
    if (!autoSave || !isDirty) return;

    const saveTimer = setTimeout(() => {
      handleSave();
    }, saveDelay);

    return () => clearTimeout(saveTimer);
  }, [currentSettings, autoSave, saveDelay, isDirty]);

  // Initialize expanded sections
  useEffect(() => {
    if (variant === 'detailed' || !collapsible) {
      setExpandedSections(new Set(sections.map((_, index) => index)));
    } else {
      setExpandedSections(new Set([0])); // First section expanded by default
    }
  }, [sections, variant, collapsible]);

  // Handle setting change
  const handleSettingChange = (sectionIndex, settingKey, value) => {
    const newSettings = { ...currentSettings };
    if (!newSettings[sectionIndex]) {
      newSettings[sectionIndex] = {};
    }
    newSettings[sectionIndex][settingKey] = value;

    setCurrentSettings(newSettings);
    setIsDirty(true);

    // Validate setting
    if (onValidate) {
      const errors = onValidate(sectionIndex, settingKey, value);
      setValidationErrors(prev => ({
        ...prev,
        [`${sectionIndex}.${settingKey}`]: errors
      }));
    }

    // Call onChange handler
    if (onChange) {
      onChange(sectionIndex, settingKey, value, newSettings);
    }
  };

  // Handle save
  const handleSave = async () => {
    if (!onSave) return;

    setIsSaving(true);
    try {
      await onSave(currentSettings);
      setIsDirty(false);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  // Handle reset
  const handleReset = () => {
    setCurrentSettings(settings);
    setValidationErrors({});
    setIsDirty(false);
    
    if (onReset) {
      onReset();
    }
  };

  // Handle export
  const handleExport = () => {
    const exportData = JSON.stringify(currentSettings, null, 2);
    
    if (onExport) {
      onExport(exportData);
    } else {
      // Default export to file
      const blob = new Blob([exportData], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'configuration.json';
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  // Handle import
  const handleImport = (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedSettings = JSON.parse(e.target.result);
        
        if (onImport) {
          onImport(importedSettings);
        } else {
          setCurrentSettings(importedSettings);
          setIsDirty(true);
        }
      } catch (error) {
        console.error('Failed to import settings:', error);
      }
    };
    reader.readAsText(file);
  };

  // Toggle section expansion
  const toggleSection = (index) => {
    if (!collapsible) return;

    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // Filter sections based on search
  const filteredSections = sections.filter(section => {
    if (!searchQuery) return true;
    
    const query = searchQuery.toLowerCase();
    return section.title?.toLowerCase().includes(query) ||
           section.description?.toLowerCase().includes(query) ||
           section.settings?.some(setting => 
             setting.key?.toLowerCase().includes(query) ||
             setting.label?.toLowerCase().includes(query) ||
             setting.description?.toLowerCase().includes(query)
           );
  });

  // Render setting input based on type
  const renderSettingInput = (sectionIndex, setting) => {
    const settingKey = setting.key;
    const currentValue = currentSettings[sectionIndex]?.[settingKey] ?? setting.default;
    const errorKey = `${sectionIndex}.${settingKey}`;
    const hasError = validationErrors[errorKey];

    const commonProps = {
      id: `setting-${sectionIndex}-${settingKey}`,
      value: currentValue || '',
      onChange: (e) => handleSettingChange(sectionIndex, settingKey, 
        setting.type === 'number' ? parseFloat(e.target.value) : e.target.value),
      className: `setting-input ${hasError ? 'error' : ''}`,
      disabled: setting.disabled
    };

    switch (setting.type) {
      case 'text':
      case 'email':
      case 'url':
        return (
          <input
            type={setting.type}
            placeholder={setting.placeholder}
            {...commonProps}
          />
        );

      case 'password':
        return (
          <input
            type="password"
            placeholder={setting.placeholder}
            {...commonProps}
          />
        );

      case 'number':
        return (
          <input
            type="number"
            min={setting.min}
            max={setting.max}
            step={setting.step}
            placeholder={setting.placeholder}
            {...commonProps}
          />
        );

      case 'textarea':
        return (
          <textarea
            rows={setting.rows || 3}
            placeholder={setting.placeholder}
            {...commonProps}
          />
        );

      case 'select':
        return (
          <select {...commonProps}>
            {setting.options?.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );

      case 'checkbox':
        return (
          <input
            type="checkbox"
            checked={currentValue || false}
            onChange={(e) => handleSettingChange(sectionIndex, settingKey, e.target.checked)}
            className={`setting-checkbox ${hasError ? 'error' : ''}`}
            disabled={setting.disabled}
          />
        );

      case 'radio':
        return (
          <div className="radio-group">
            {setting.options?.map(option => (
              <label key={option.value} className="radio-option">
                <input
                  type="radio"
                  name={`${sectionIndex}-${settingKey}`}
                  value={option.value}
                  checked={currentValue === option.value}
                  onChange={(e) => handleSettingChange(sectionIndex, settingKey, e.target.value)}
                  disabled={setting.disabled}
                />
                <span className="radio-label">{option.label}</span>
              </label>
            ))}
          </div>
        );

      case 'range':
        return (
          <div className="range-input">
            <input
              type="range"
              min={setting.min || 0}
              max={setting.max || 100}
              step={setting.step || 1}
              value={currentValue || setting.default || 0}
              onChange={(e) => handleSettingChange(sectionIndex, settingKey, parseFloat(e.target.value))}
              className={`setting-range ${hasError ? 'error' : ''}`}
              disabled={setting.disabled}
            />
            <span className="range-value">{currentValue || setting.default || 0}</span>
          </div>
        );

      case 'color':
        return (
          <input
            type="color"
            {...commonProps}
            className={`setting-color ${hasError ? 'error' : ''}`}
          />
        );

      case 'file':
        return (
          <input
            type="file"
            accept={setting.accept}
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) {
                handleSettingChange(sectionIndex, settingKey, file);
              }
            }}
            className={`setting-file ${hasError ? 'error' : ''}`}
            disabled={setting.disabled}
          />
        );

      default:
        return (
          <input
            type="text"
            placeholder={setting.placeholder}
            {...commonProps}
          />
        );
    }
  };

  // Render setting
  const renderSetting = (sectionIndex, setting, settingIndex) => {
    const errorKey = `${sectionIndex}.${setting.key}`;
    const hasError = validationErrors[errorKey];
    const currentValue = currentSettings[sectionIndex]?.[setting.key];
    const isDefault = currentValue === setting.default;

    return (
      <div key={setting.key} className={`setting-item ${hasError ? 'has-error' : ''}`}>
        <div className="setting-header">
          <label 
            htmlFor={`setting-${sectionIndex}-${setting.key}`}
            className="setting-label"
          >
            {setting.label || setting.key}
            {setting.required && <span className="required-indicator">*</span>}
          </label>
          
          {showDefaults && !isDefault && (
            <button
              className="reset-to-default"
              onClick={() => handleSettingChange(sectionIndex, setting.key, setting.default)}
              title="Reset to default"
            >
              <i className="fas fa-undo" />
            </button>
          )}
        </div>

        <div className="setting-input-container">
          {renderSettingInput(sectionIndex, setting)}
        </div>

        {showDescriptions && setting.description && (
          <p className="setting-description">{setting.description}</p>
        )}

        {showDefaults && setting.default !== undefined && (
          <div className="setting-default">
            Default: {String(setting.default)}
          </div>
        )}

        {showValidation && hasError && (
          <div className="setting-error">
            {Array.isArray(hasError) ? hasError.join(', ') : hasError}
          </div>
        )}
      </div>
    );
  };

  // Render section
  const renderSection = (section, index) => {
    const isExpanded = expandedSections.has(index);
    
    return (
      <div key={index} className={`config-section ${isExpanded ? 'expanded' : 'collapsed'}`}>
        <div 
          className="section-header"
          onClick={() => toggleSection(index)}
        >
          <div className="section-title-container">
            <h3 className="section-title">{section.title}</h3>
            {section.description && (
              <p className="section-description">{section.description}</p>
            )}
          </div>
          
          {collapsible && (
            <button className="section-toggle">
              <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'}`} />
            </button>
          )}
        </div>

        {isExpanded && (
          <div className="section-content">
            {section.settings?.map((setting, settingIndex) => 
              renderSetting(index, setting, settingIndex)
            )}
          </div>
        )}
      </div>
    );
  };

  return (
    <div 
      className={`
        configuration-panel
        variant-${variant}
        size-${size}
        ${tabbed ? 'tabbed' : ''}
        ${isDirty ? 'dirty' : ''}
        ${className}
      `}
      style={style}
    >
      {/* Header */}
      <div className="panel-header">
        <div className="panel-title-section">
          <h2 className="panel-title">{title}</h2>
          {description && variant !== 'minimal' && (
            <p className="panel-description">{description}</p>
          )}
        </div>

        <div className="panel-controls">
          {isDirty && (
            <div className="dirty-indicator">
              <i className="fas fa-circle" />
              <span>Unsaved changes</span>
            </div>
          )}

          {exportable && (
            <button 
              className="panel-action export"
              onClick={handleExport}
              title="Export configuration"
            >
              <i className="fas fa-download" />
              {variant === 'detailed' && <span>Export</span>}
            </button>
          )}

          {importable && (
            <label className="panel-action import" title="Import configuration">
              <i className="fas fa-upload" />
              {variant === 'detailed' && <span>Import</span>}
              <input
                type="file"
                accept=".json"
                onChange={handleImport}
                style={{ display: 'none' }}
              />
            </label>
          )}

          {resetable && (
            <button 
              className="panel-action reset"
              onClick={handleReset}
              disabled={!isDirty}
              title="Reset all settings"
            >
              <i className="fas fa-undo" />
              {variant === 'detailed' && <span>Reset</span>}
            </button>
          )}

          {!autoSave && onSave && (
            <button 
              className="panel-action save primary"
              onClick={handleSave}
              disabled={!isDirty || isSaving}
              title="Save configuration"
            >
              <i className={`fas fa-${isSaving ? 'spinner fa-spin' : 'save'}`} />
              {variant === 'detailed' && <span>{isSaving ? 'Saving...' : 'Save'}</span>}
            </button>
          )}
        </div>
      </div>

      {/* Search */}
      {searchable && variant !== 'minimal' && (
        <div className="panel-search">
          <div className="search-input">
            <i className="fas fa-search" />
            <input
              type="text"
              placeholder="Search settings..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button 
                className="clear-search"
                onClick={() => setSearchQuery('')}
              >
                <i className="fas fa-times" />
              </button>
            )}
          </div>
        </div>
      )}

      {/* Tabs */}
      {tabbed && (
        <div className="panel-tabs">
          {filteredSections.map((section, index) => (
            <button
              key={index}
              className={`tab-button ${activeTab === index ? 'active' : ''}`}
              onClick={() => setActiveTab(index)}
            >
              {section.title}
            </button>
          ))}
        </div>
      )}

      {/* Content */}
      <div className="panel-content">
        {tabbed ? (
          filteredSections[activeTab] && renderSection(filteredSections[activeTab], activeTab)
        ) : (
          filteredSections.map((section, index) => renderSection(section, index))
        )}

        {filteredSections.length === 0 && searchQuery && (
          <div className="no-results">
            <i className="fas fa-search" />
            <p>No settings match your search criteria</p>
            <button onClick={() => setSearchQuery('')}>Clear search</button>
          </div>
        )}
      </div>

      {/* Footer */}
      {variant === 'detailed' && (
        <div className="panel-footer">
          <div className="footer-info">
            <span>{Object.keys(currentSettings).length} sections configured</span>
            {autoSave && <span>Auto-save enabled</span>}
          </div>
          
          <div className="footer-actions">
            {isDirty && !autoSave && (
              <span className="save-reminder">
                <i className="fas fa-exclamation-triangle" />
                Don't forget to save your changes
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ConfigurationPanel;
