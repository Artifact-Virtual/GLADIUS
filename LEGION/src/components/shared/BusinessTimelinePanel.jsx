import React, { useState, useEffect } from 'react';

/**
 * BusinessTimelinePanel - Business Timeline and Milestone Tracker
 * 
 * Displays business timeline with:
 * - Upcoming milestones
 * - Project deadlines
 * - Business events
 * - Achievement tracking
 */
const BusinessTimelinePanel = ({ 
  className = '', 
  onEventClick = () => {},
  refreshInterval = 60000 
}) => {
  const [timelineData, setTimelineData] = useState({
    events: [],
    milestones: [],
    loading: true
  });

  useEffect(() => {
    const fetchTimelineData = async () => {
      try {
        const response = await fetch('/api/business-timeline');
        if (response.ok) {
          const data = await response.json();
          setTimelineData({ ...data, loading: false });
        }
      } catch (error) {
        console.error('Error fetching timeline data:', error);
        // Mock data for development
        setTimelineData({
          events: [
            {
              id: 1,
              title: 'Q4 Planning Session',
              date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
              type: 'meeting',
              priority: 'high',
              description: 'Strategic planning for Q4 objectives'
            },
            {
              id: 2,
              title: 'Product Launch',
              date: new Date(Date.now() + 14 * 24 * 60 * 60 * 1000),
              type: 'milestone',
              priority: 'critical',
              description: 'Legion Enterprise Dashboard v2.0'
            },
            {
              id: 3,
              title: 'Client Review Meeting',
              date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000),
              type: 'meeting',
              priority: 'medium',
              description: 'Monthly client progress review'
            }
          ],
          milestones: [
            {
              id: 1,
              title: 'Revenue Target Achievement',
              progress: 75,
              deadline: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
              status: 'on-track'
            },
            {
              id: 2,
              title: 'Team Expansion Complete',
              progress: 90,
              deadline: new Date(Date.now() + 45 * 24 * 60 * 60 * 1000),
              status: 'ahead'
            }
          ],
          loading: false
        });
      }
    };

    fetchTimelineData();
    const interval = setInterval(fetchTimelineData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const formatDate = (date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(new Date(date));
  };

  const getDaysUntil = (date) => {
    const days = Math.ceil((new Date(date) - new Date()) / (1000 * 60 * 60 * 24));
    if (days < 0) return 'Overdue';
    if (days === 0) return 'Today';
    if (days === 1) return 'Tomorrow';
    return `${days} days`;
  };

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'critical': return '🔴';
      case 'high': return '🟠';
      case 'medium': return '🟡';
      case 'low': return '🟢';
      default: return '⚪';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'milestone': return '🎯';
      case 'meeting': return '📅';
      case 'deadline': return '⏰';
      case 'event': return '📋';
      default: return '📌';
    }
  };

  if (timelineData.loading) {
    return (
      <div className={`business-timeline-panel loading ${className}`}>
        <div className="panel-header">
          <h3>Business Timeline</h3>
          <div className="loading-spinner"></div>
        </div>
        <div className="loading-content">Loading timeline data...</div>
      </div>
    );
  }

  return (
    <div className={`business-timeline-panel ${className}`}>
      <div className="panel-header">
        <h3>Business Timeline</h3>
        <div className="timeline-controls">
          <button className="timeline-filter active">All</button>
          <button className="timeline-filter">This Week</button>
          <button className="timeline-filter">This Month</button>
        </div>
      </div>

      <div className="timeline-content">
        <div className="upcoming-events">
          <h4>Upcoming Events</h4>
          <div className="events-list">
            {timelineData.events.map(event => (
              <div 
                key={event.id}
                className={`event-item ${event.priority}`}
                onClick={() => onEventClick(event)}
              >
                <div className="event-icon">
                  {getTypeIcon(event.type)}
                </div>
                <div className="event-details">
                  <div className="event-title">{event.title}</div>
                  <div className="event-description">{event.description}</div>
                  <div className="event-date">
                    {formatDate(event.date)} • {getDaysUntil(event.date)}
                  </div>
                </div>
                <div className="event-priority">
                  {getPriorityIcon(event.priority)}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="milestones-section">
          <h4>Active Milestones</h4>
          <div className="milestones-list">
            {timelineData.milestones.map(milestone => (
              <div 
                key={milestone.id}
                className={`milestone-item ${milestone.status}`}
                onClick={() => onEventClick(milestone)}
              >
                <div className="milestone-header">
                  <span className="milestone-title">{milestone.title}</span>
                  <span className="milestone-deadline">
                    Due: {getDaysUntil(milestone.deadline)}
                  </span>
                </div>
                <div className="milestone-progress">
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${milestone.progress}%` }}
                    ></div>
                  </div>
                  <span className="progress-text">{milestone.progress}%</span>
                </div>
                <div className={`milestone-status ${milestone.status}`}>
                  {milestone.status === 'on-track' && '✅ On Track'}
                  {milestone.status === 'ahead' && '🚀 Ahead of Schedule'}
                  {milestone.status === 'behind' && '⚠️ Behind Schedule'}
                  {milestone.status === 'at-risk' && '🔴 At Risk'}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BusinessTimelinePanel;
