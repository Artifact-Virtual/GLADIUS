// src/components/shared/LiveDataFeed.jsx
import React, { useState, useEffect, useRef, useMemo } from 'react';

const LiveDataFeed = ({
  data = [],
  title = 'Live Data Feed',
  maxItems = 50,
  updateInterval = 1000, // ms
  variant = 'default', // 'default', 'minimal', 'detailed', 'compact'
  size = 'medium', // 'small', 'medium', 'large'
  showTimestamp = true,
  showFilter = true,
  showSearch = true,
  showStats = true,
  autoScroll = true,
  pauseOnHover = true,
  groupByTime = false,
  realTime = true,
  onItemClick = null,
  onFilter = null,
  onSearch = null,
  className = '',
  itemRenderer = null, // Custom item renderer function
  filterOptions = [],
  searchPlaceholder = 'Search feed...',
  emptyMessage = 'No data available',
  loadingMessage = 'Loading data...',
  ...props
}) => {
  const [feedData, setFeedData] = useState([]);
  const [filteredData, setFilteredData] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [stats, setStats] = useState({});
  const feedRef = useRef(null);
  const intervalRef = useRef(null);

  // Initialize data
  useEffect(() => {
    if (data && data.length > 0) {
      setFeedData(data.slice(-maxItems));
      setIsLoading(false);
    }
  }, [data, maxItems]);

  // Filter and search data
  useEffect(() => {
    let filtered = [...feedData];

    // Apply filter
    if (selectedFilter && selectedFilter !== 'all') {
      filtered = filtered.filter(item => {
        if (typeof onFilter === 'function') {
          return onFilter(item, selectedFilter);
        }
        return item.type === selectedFilter || item.category === selectedFilter;
      });
    }

    // Apply search
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(item => {
        if (typeof onSearch === 'function') {
          return onSearch(item, query);
        }
        const searchFields = [
          item.title,
          item.message,
          item.description,
          item.source,
          item.type,
          item.category
        ].filter(Boolean);
        
        return searchFields.some(field => 
          field.toLowerCase().includes(query)
        );
      });
    }

    setFilteredData(filtered);
  }, [feedData, selectedFilter, searchQuery, onFilter, onSearch]);

  // Calculate stats
  useEffect(() => {
    const newStats = {
      total: feedData.length,
      filtered: filteredData.length,
      types: {},
      recentActivity: 0
    };

    // Count by type/category
    feedData.forEach(item => {
      const key = item.type || item.category || 'unknown';
      newStats.types[key] = (newStats.types[key] || 0) + 1;
    });

    // Recent activity (last 5 minutes)
    const fiveMinutesAgo = Date.now() - (5 * 60 * 1000);
    newStats.recentActivity = feedData.filter(item => {
      const itemTime = new Date(item.timestamp || item.time).getTime();
      return itemTime > fiveMinutesAgo;
    }).length;

    setStats(newStats);
  }, [feedData, filteredData]);

  // Auto-scroll to bottom
  useEffect(() => {
    if (autoScroll && feedRef.current && !isPaused) {
      feedRef.current.scrollTop = feedRef.current.scrollHeight;
    }
  }, [filteredData, autoScroll, isPaused]);

  // Real-time updates
  useEffect(() => {
    if (realTime && updateInterval > 0) {
      intervalRef.current = setInterval(() => {
        // This would typically fetch new data from an API
        // For now, we'll just simulate updates
        if (!isPaused && data && data.length > feedData.length) {
          const newItems = data.slice(feedData.length);
          setFeedData(prev => [...prev, ...newItems].slice(-maxItems));
        }
      }, updateInterval);

      return () => {
        if (intervalRef.current) {
          clearInterval(intervalRef.current);
        }
      };
    }
  }, [realTime, updateInterval, isPaused, data, feedData.length, maxItems]);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const getItemColor = (item) => {
    switch (item.type || item.level || item.severity) {
      case 'error':
      case 'critical':
        return '#dc3545';
      case 'warning':
      case 'alert':
        return '#ffc107';
      case 'success':
      case 'completed':
        return '#28a745';
      case 'info':
      case 'notification':
        return '#17a2b8';
      default:
        return '#6c757d';
    }
  };

  const getItemIcon = (item) => {
    switch (item.type || item.level) {
      case 'error':
      case 'critical':
        return 'fas fa-exclamation-circle';
      case 'warning':
      case 'alert':
        return 'fas fa-exclamation-triangle';
      case 'success':
      case 'completed':
        return 'fas fa-check-circle';
      case 'info':
      case 'notification':
        return 'fas fa-info-circle';
      case 'user':
        return 'fas fa-user';
      case 'system':
        return 'fas fa-cog';
      case 'agent':
        return 'fas fa-robot';
      default:
        return 'fas fa-circle';
    }
  };

  const groupedData = useMemo(() => {
    if (!groupByTime) return { ungrouped: filteredData };

    const groups = {};
    filteredData.forEach(item => {
      const date = new Date(item.timestamp || item.time);
      const key = date.toDateString();
      if (!groups[key]) groups[key] = [];
      groups[key].push(item);
    });

    return groups;
  }, [filteredData, groupByTime]);

  const defaultItemRenderer = (item, index) => (
    <div 
      key={item.id || index}
      className={`feed-item item-${item.type || 'default'}`}
      onClick={() => onItemClick && onItemClick(item)}
      style={{ '--item-color': getItemColor(item) }}
    >
      <div className="item-indicator">
        <i 
          className={getItemIcon(item)}
          style={{ color: getItemColor(item) }}
        />
      </div>
      <div className="item-content">
        <div className="item-header">
          <span className="item-title">
            {item.title || item.message || 'Untitled'}
          </span>
          {showTimestamp && (
            <span className="item-timestamp">
              {formatTimestamp(item.timestamp || item.time)}
            </span>
          )}
        </div>
        {(item.description || item.details) && variant !== 'minimal' && (
          <div className="item-description">
            {item.description || item.details}
          </div>
        )}
        {item.source && variant === 'detailed' && (
          <div className="item-source">
            Source: {item.source}
          </div>
        )}
      </div>
    </div>
  );

  const feedClasses = [
    'live-data-feed',
    `variant-${variant}`,
    `size-${size}`,
    isPaused ? 'paused' : '',
    isLoading ? 'loading' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={feedClasses} {...props}>
      {/* Header */}
      <div className="feed-header">
        <div className="feed-title">
          <h3>{title}</h3>
          <div className="feed-status">
            <div className={`status-indicator ${realTime && !isPaused ? 'live' : 'paused'}`} />
            <span className="status-text">
              {isLoading ? 'Loading...' : realTime && !isPaused ? 'Live' : 'Paused'}
            </span>
          </div>
        </div>
        
        <div className="feed-controls">
          {realTime && (
            <button
              className={`control-btn pause-btn ${isPaused ? 'active' : ''}`}
              onClick={() => setIsPaused(!isPaused)}
              title={isPaused ? 'Resume' : 'Pause'}
            >
              <i className={`fas ${isPaused ? 'fa-play' : 'fa-pause'}`} />
            </button>
          )}
          <button
            className="control-btn clear-btn"
            onClick={() => {
              setFeedData([]);
              setFilteredData([]);
            }}
            title="Clear feed"
          >
            <i className="fas fa-trash" />
          </button>
        </div>
      </div>

      {/* Stats */}
      {showStats && variant !== 'minimal' && (
        <div className="feed-stats">
          <div className="stat-item">
            <span className="stat-label">Total</span>
            <span className="stat-value">{stats.total}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Filtered</span>
            <span className="stat-value">{stats.filtered}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Recent</span>
            <span className="stat-value">{stats.recentActivity}</span>
          </div>
        </div>
      )}

      {/* Filters and Search */}
      {(showFilter || showSearch) && variant !== 'minimal' && (
        <div className="feed-filters">
          {showSearch && (
            <div className="search-input">
              <i className="fas fa-search" />
              <input
                type="text"
                placeholder={searchPlaceholder}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          )}
          {showFilter && filterOptions.length > 0 && (
            <select
              className="filter-select"
              value={selectedFilter}
              onChange={(e) => setSelectedFilter(e.target.value)}
            >
              <option value="all">All Types</option>
              {filterOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          )}
        </div>
      )}

      {/* Feed Content */}
      <div 
        className="feed-content"
        ref={feedRef}
        onMouseEnter={() => pauseOnHover && setIsPaused(true)}
        onMouseLeave={() => pauseOnHover && setIsPaused(false)}
      >
        {isLoading ? (
          <div className="feed-loading">
            <i className="fas fa-spinner fa-spin" />
            <span>{loadingMessage}</span>
          </div>
        ) : filteredData.length === 0 ? (
          <div className="feed-empty">
            <i className="fas fa-inbox" />
            <span>{emptyMessage}</span>
          </div>
        ) : groupByTime ? (
          Object.entries(groupedData).map(([date, items]) => (
            <div key={date} className="feed-group">
              <div className="group-header">
                <span className="group-date">{date}</span>
                <span className="group-count">{items.length} items</span>
              </div>
              <div className="group-items">
                {items.map((item, index) => 
                  itemRenderer ? itemRenderer(item, index) : defaultItemRenderer(item, index)
                )}
              </div>
            </div>
          ))
        ) : (
          filteredData.map((item, index) => 
            itemRenderer ? itemRenderer(item, index) : defaultItemRenderer(item, index)
          )
        )}
      </div>
    </div>
  );
};

export default LiveDataFeed;
