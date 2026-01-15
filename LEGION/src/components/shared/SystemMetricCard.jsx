// src/components/shared/SystemMetricCard.jsx
import React, { useState, useEffect } from 'react';

const SystemMetricCard = ({ 
  title, 
  value, 
  unit = '', 
  change = null, 
  changeType = 'positive', // 'positive', 'negative', 'neutral'
  trend = null, // array of values for trend line
  icon = null, 
  status = 'normal', // 'normal', 'warning', 'critical', 'success'
  loading = false,
  size = 'medium', // 'small', 'medium', 'large'
  variant = 'default', // 'default', 'minimal', 'detailed', 'compact'
  onClick = null,
  refreshInterval = null,
  customColor = null,
  subtitle = null,
  target = null,
  targetLabel = 'Target',
  precision = 2,
  animate = true,
  showTrend = true,
  className = '',
  ...props 
}) => {
  const [currentValue, setCurrentValue] = useState(value);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    if (animate && value !== currentValue) {
      setIsAnimating(true);
      const timer = setTimeout(() => {
        setCurrentValue(value);
        setIsAnimating(false);
      }, 300);
      return () => clearTimeout(timer);
    } else {
      setCurrentValue(value);
    }
  }, [value, animate, currentValue]);

  useEffect(() => {
    if (refreshInterval && typeof refreshInterval === 'function') {
      const interval = setInterval(refreshInterval, 30000); // 30 second refresh
      return () => clearInterval(interval);
    }
  }, [refreshInterval]);

  const formatValue = (val) => {
    if (val === null || val === undefined) return '--';
    if (typeof val === 'number') {
      if (val >= 1000000) {
        return `${(val / 1000000).toFixed(1)}M`;
      } else if (val >= 1000) {
        return `${(val / 1000).toFixed(1)}K`;
      } else if (val % 1 !== 0) {
        return val.toFixed(precision);
      }
      return val.toString();
    }
    return val;
  };

  const getStatusColor = () => {
    if (customColor) return customColor;
    switch (status) {
      case 'success': return '#28a745';
      case 'warning': return '#ffc107';
      case 'critical': return '#dc3545';
      default: return '#17a2b8';
    }
  };

  const getChangeColor = () => {
    switch (changeType) {
      case 'positive': return '#28a745';
      case 'negative': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const generateTrendPath = () => {
    if (!trend || trend.length < 2) return '';
    
    const width = 60;
    const height = 20;
    const min = Math.min(...trend);
    const max = Math.max(...trend);
    const range = max - min || 1;
    
    const points = trend.map((val, index) => {
      const x = (index / (trend.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    });
    
    return `M ${points.join(' L ')}`;
  };

  const renderTrendLine = () => {
    if (!showTrend || !trend || trend.length < 2) return null;
    
    return (
      <div className="metric-trend">
        <svg width="60" height="20" viewBox="0 0 60 20">
          <path
            d={generateTrendPath()}
            fill="none"
            stroke={getStatusColor()}
            strokeWidth="2"
            opacity="0.7"
          />
        </svg>
      </div>
    );
  };

  const renderProgressBar = () => {
    if (target === null || target === undefined) return null;
    
    const percentage = Math.min((currentValue / target) * 100, 100);
    
    return (
      <div className="metric-progress">
        <div className="progress-bar">
          <div 
            className="progress-fill"
            style={{ 
              width: `${percentage}%`,
              backgroundColor: getStatusColor()
            }}
          />
        </div>
        <span className="progress-label">
          {targetLabel}: {formatValue(target)}{unit}
        </span>
      </div>
    );
  };

  const cardClasses = [
    'system-metric-card',
    `metric-${size}`,
    `metric-${variant}`,
    `metric-${status}`,
    loading ? 'metric-loading' : '',
    isAnimating ? 'metric-animating' : '',
    onClick ? 'metric-clickable' : '',
    className
  ].filter(Boolean).join(' ');

  if (loading) {
    return (
      <div className={cardClasses} {...props}>
        <div className="metric-loading-content">
          <div className="metric-skeleton metric-skeleton-title"></div>
          <div className="metric-skeleton metric-skeleton-value"></div>
          {change && <div className="metric-skeleton metric-skeleton-change"></div>}
        </div>
      </div>
    );
  }

  return (
    <div 
      className={cardClasses} 
      onClick={onClick}
      style={{ '--metric-color': getStatusColor() }}
      {...props}
    >
      <div className="metric-content">
        {/* Header */}
        <div className="metric-header">
          {icon && <div className="metric-icon">{icon}</div>}
          <div className="metric-title-section">
            <h3 className="metric-title">{title}</h3>
            {subtitle && <p className="metric-subtitle">{subtitle}</p>}
          </div>
          {variant !== 'minimal' && renderTrendLine()}
        </div>

        {/* Main Value */}
        <div className="metric-value-section">
          <div className="metric-main-value">
            <span className="metric-value">{formatValue(currentValue)}</span>
            {unit && <span className="metric-unit">{unit}</span>}
          </div>
          
          {change !== null && (
            <div className="metric-change" style={{ color: getChangeColor() }}>
              <i className={`fas ${changeType === 'positive' ? 'fa-arrow-up' : changeType === 'negative' ? 'fa-arrow-down' : 'fa-minus'}`}></i>
              <span>{Math.abs(change)}{unit}</span>
            </div>
          )}
        </div>

        {/* Progress Bar */}
        {variant === 'detailed' && renderProgressBar()}

        {/* Status Indicator */}
        <div className="metric-status-indicator" style={{ backgroundColor: getStatusColor() }}></div>
      </div>
    </div>
  );
};

export default SystemMetricCard;
