import React, { useState, useEffect } from 'react';

const BusinessTimelineCalendar = ({ timelineData, onEventUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('timeline'); // 'timeline', 'calendar', 'gantt', 'milestones'
  const [timeRange, setTimeRange] = useState('quarter');
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filterCategory, setFilterCategory] = useState('all');
  const [data, setData] = useState({
    events: [],
    milestones: [],
    projects: [],
    timeline: {},
    calendar: {},
    dependencies: []
  });

  useEffect(() => {
    const loadTimelineData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided timelineData or fetch from API
        if (timelineData) {
          setData(timelineData);
        } else {
          const response = await fetch(`/api/enterprise/business-timeline?timeRange=${timeRange}&category=${filterCategory}`);
          if (!response.ok) throw new Error('Failed to load timeline data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading timeline data:', err);
        setError(err.message);
        
        // Mock comprehensive timeline data for development
        const mockData = {
          events: [
            {
              id: 'ev001',
              title: 'Q4 Product Launch',
              description: 'Major AI platform release with new features',
              startDate: '2024-10-15',
              endDate: '2024-10-30',
              category: 'product',
              priority: 'high',
              status: 'in_progress',
              progress: 65,
              owner: 'Product Team',
              department: 'Engineering',
              budget: 150000,
              attendees: ['John Doe', 'Jane Smith', 'Mike Johnson'],
              tags: ['launch', 'ai', 'platform'],
              dependencies: ['ev002', 'ev003']
            },
            {
              id: 'ev002',
              title: 'Marketing Campaign Kickoff',
              description: 'Launch comprehensive marketing campaign for new product',
              startDate: '2024-09-01',
              endDate: '2024-10-15',
              category: 'marketing',
              priority: 'high',
              status: 'completed',
              progress: 100,
              owner: 'Marketing Team',
              department: 'Marketing',
              budget: 75000,
              attendees: ['Sarah Wilson', 'Tom Brown', 'Lisa Davis'],
              tags: ['campaign', 'digital', 'launch'],
              dependencies: []
            },
            {
              id: 'ev003',
              title: 'Security Audit & Compliance',
              description: 'Comprehensive security review and compliance certification',
              startDate: '2024-08-15',
              endDate: '2024-09-30',
              category: 'compliance',
              priority: 'critical',
              status: 'completed',
              progress: 100,
              owner: 'Security Team',
              department: 'Legal',
              budget: 45000,
              attendees: ['Alex Chen', 'Maya Patel', 'David Kim'],
              tags: ['security', 'audit', 'compliance'],
              dependencies: []
            },
            {
              id: 'ev004',
              title: 'Q1 Board Meeting',
              description: 'Quarterly board meeting and strategic planning session',
              startDate: '2025-01-15',
              endDate: '2025-01-15',
              category: 'meeting',
              priority: 'high',
              status: 'planned',
              progress: 0,
              owner: 'Executive Team',
              department: 'Strategy',
              budget: 5000,
              attendees: ['CEO', 'CTO', 'CFO', 'Board Members'],
              tags: ['board', 'strategy', 'quarterly'],
              dependencies: []
            },
            {
              id: 'ev005',
              title: 'Customer Success Program',
              description: 'Launch new customer success and retention initiative',
              startDate: '2024-11-01',
              endDate: '2024-12-31',
              category: 'customer',
              priority: 'medium',
              status: 'planned',
              progress: 0,
              owner: 'Customer Success',
              department: 'Operations',
              budget: 95000,
              attendees: ['Rachel Green', 'Monica Geller', 'Ross Geller'],
              tags: ['customer', 'retention', 'success'],
              dependencies: ['ev001']
            },
            {
              id: 'ev006',
              title: 'Holiday Team Building',
              description: 'Annual team building and holiday celebration event',
              startDate: '2024-12-15',
              endDate: '2024-12-15',
              category: 'team',
              priority: 'low',
              status: 'planned',
              progress: 0,
              owner: 'HR Team',
              department: 'Operations',
              budget: 15000,
              attendees: ['All Employees'],
              tags: ['team', 'holiday', 'celebration'],
              dependencies: []
            }
          ],
          milestones: [
            {
              id: 'ms001',
              title: 'Product Beta Release',
              date: '2024-10-01',
              category: 'product',
              status: 'completed',
              description: 'Beta version released to select customers',
              impact: 'high',
              owner: 'Product Team',
              achievements: ['100 beta users onboarded', '95% uptime achieved', 'Positive feedback received']
            },
            {
              id: 'ms002',
              title: 'Series A Funding Close',
              date: '2024-11-30',
              category: 'finance',
              status: 'in_progress',
              description: 'Complete Series A funding round',
              impact: 'critical',
              owner: 'Executive Team',
              achievements: ['Term sheet signed', 'Due diligence in progress']
            },
            {
              id: 'ms003',
              title: '1000 Active Users',
              date: '2024-12-31',
              category: 'growth',
              status: 'planned',
              description: 'Reach 1000 active users milestone',
              impact: 'high',
              owner: 'Growth Team',
              achievements: []
            },
            {
              id: 'ms004',
              title: 'ISO Certification',
              date: '2025-02-28',
              category: 'compliance',
              status: 'planned',
              description: 'Achieve ISO 27001 security certification',
              impact: 'high',
              owner: 'Security Team',
              achievements: []
            },
            {
              id: 'ms005',
              title: 'Market Expansion',
              date: '2025-03-31',
              category: 'business',
              status: 'planned',
              description: 'Expand to European market',
              impact: 'critical',
              owner: 'Business Development',
              achievements: []
            }
          ],
          projects: [
            {
              id: 'proj001',
              name: 'AI Platform 2.0',
              description: 'Next generation AI platform development',
              startDate: '2024-07-01',
              endDate: '2024-12-31',
              status: 'in_progress',
              progress: 68,
              team: 'Engineering',
              budget: 500000,
              phases: [
                { name: 'Research & Design', status: 'completed', progress: 100, duration: 30 },
                { name: 'Development', status: 'in_progress', progress: 75, duration: 120 },
                { name: 'Testing', status: 'planned', progress: 0, duration: 45 },
                { name: 'Deployment', status: 'planned', progress: 0, duration: 15 }
              ]
            },
            {
              id: 'proj002',
              name: 'Customer Portal',
              description: 'Self-service customer portal development',
              startDate: '2024-09-01',
              endDate: '2025-01-31',
              status: 'in_progress',
              progress: 35,
              team: 'Frontend',
              budget: 200000,
              phases: [
                { name: 'UI/UX Design', status: 'completed', progress: 100, duration: 30 },
                { name: 'Frontend Development', status: 'in_progress', progress: 60, duration: 90 },
                { name: 'Backend Integration', status: 'planned', progress: 0, duration: 45 },
                { name: 'QA & Launch', status: 'planned', progress: 0, duration: 15 }
              ]
            },
            {
              id: 'proj003',
              name: 'Mobile App',
              description: 'Native mobile application for iOS and Android',
              startDate: '2025-01-01',
              endDate: '2025-06-30',
              status: 'planned',
              progress: 0,
              team: 'Mobile',
              budget: 350000,
              phases: [
                { name: 'Planning & Design', status: 'planned', progress: 0, duration: 45 },
                { name: 'iOS Development', status: 'planned', progress: 0, duration: 90 },
                { name: 'Android Development', status: 'planned', progress: 0, duration: 90 },
                { name: 'Testing & Release', status: 'planned', progress: 0, duration: 30 }
              ]
            }
          ],
          timeline: {
            quarters: [
              {
                name: 'Q3 2024',
                period: '2024-07-01 to 2024-09-30',
                status: 'completed',
                achievements: 8,
                events: 12,
                budget: 145000,
                highlights: ['Security audit completed', 'Beta testing initiated', 'Team expansion']
              },
              {
                name: 'Q4 2024',
                period: '2024-10-01 to 2024-12-31',
                status: 'in_progress',
                achievements: 3,
                events: 8,
                budget: 280000,
                highlights: ['Product launch', 'Marketing campaign', 'Customer onboarding']
              },
              {
                name: 'Q1 2025',
                period: '2025-01-01 to 2025-03-31',
                status: 'planned',
                achievements: 0,
                events: 6,
                budget: 320000,
                highlights: ['Board meetings', 'Market expansion', 'Mobile app development']
              },
              {
                name: 'Q2 2025',
                period: '2025-04-01 to 2025-06-30',
                status: 'planned',
                achievements: 0,
                events: 4,
                budget: 250000,
                highlights: ['International launch', 'Partnership deals', 'Platform scaling']
              }
            ]
          },
          calendar: {
            currentMonth: {
              name: 'October 2024',
              weeks: [
                {
                  weekNumber: 40,
                  days: [
                    { date: '2024-09-30', events: [], isCurrentMonth: false },
                    { date: '2024-10-01', events: ['ev001'], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-02', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-03', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-04', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-05', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-06', events: [], isCurrentMonth: true, isToday: false }
                  ]
                },
                {
                  weekNumber: 41,
                  days: [
                    { date: '2024-10-07', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-08', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-09', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-10', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-11', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-12', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-13', events: [], isCurrentMonth: true, isToday: false }
                  ]
                },
                {
                  weekNumber: 42,
                  days: [
                    { date: '2024-10-14', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-15', events: ['ev001', 'ev004'], isCurrentMonth: true, isToday: true },
                    { date: '2024-10-16', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-17', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-18', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-19', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-20', events: [], isCurrentMonth: true, isToday: false }
                  ]
                },
                {
                  weekNumber: 43,
                  days: [
                    { date: '2024-10-21', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-22', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-23', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-24', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-25', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-26', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-27', events: [], isCurrentMonth: true, isToday: false }
                  ]
                },
                {
                  weekNumber: 44,
                  days: [
                    { date: '2024-10-28', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-29', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-30', events: ['ev001'], isCurrentMonth: true, isToday: false },
                    { date: '2024-10-31', events: [], isCurrentMonth: true, isToday: false },
                    { date: '2024-11-01', events: ['ev005'], isCurrentMonth: false, isToday: false },
                    { date: '2024-11-02', events: [], isCurrentMonth: false, isToday: false },
                    { date: '2024-11-03', events: [], isCurrentMonth: false, isToday: false }
                  ]
                }
              ]
            }
          },
          dependencies: [
            { from: 'ev002', to: 'ev001', type: 'finish_to_start', lag: 0 },
            { from: 'ev003', to: 'ev001', type: 'finish_to_start', lag: 7 },
            { from: 'ev001', to: 'ev005', type: 'finish_to_start', lag: 1 },
            { from: 'ms001', to: 'ms002', type: 'milestone_dependency', lag: 30 }
          ]
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadTimelineData();
    const interval = setInterval(loadTimelineData, 600000); // Refresh every 10 minutes
    return () => clearInterval(interval);
  }, [timeRange, filterCategory, timelineData]);

  const handleEventUpdate = (eventId, updateData) => {
    if (onEventUpdate) {
      onEventUpdate(eventId, updateData);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatDateShort = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in_progress': return '#f59e0b';
      case 'planned': return '#6b7280';
      case 'overdue': return '#ef4444';
      case 'cancelled': return '#9ca3af';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#ef4444';
      case 'high': return '#f59e0b';
      case 'medium': return '#3b82f6';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'product': return '🚀';
      case 'marketing': return '📢';
      case 'compliance': return '📋';
      case 'meeting': return '📅';
      case 'customer': return '👥';
      case 'team': return '🎉';
      case 'finance': return '💰';
      case 'growth': return '📈';
      case 'business': return '🌍';
      default: return '📌';
    }
  };

  const getProgressColor = (progress) => {
    if (progress >= 80) return '#10b981';
    if (progress >= 60) return '#f59e0b';
    if (progress >= 40) return '#3b82f6';
    return '#ef4444';
  };

  if (loading) {
    return (
      <div className="business-timeline-calendar loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading timeline data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="business-timeline-calendar error">
        <div className="error-message">
          <h3>Error Loading Timeline Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="business-timeline-calendar">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Business Timeline & Calendar</h2>
          <p>Comprehensive timeline and milestone tracking for strategic planning</p>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
            <option value="all">All Time</option>
          </select>
          <select 
            value={filterCategory} 
            onChange={(e) => setFilterCategory(e.target.value)}
            className="category-filter"
          >
            <option value="all">All Categories</option>
            <option value="product">Product</option>
            <option value="marketing">Marketing</option>
            <option value="compliance">Compliance</option>
            <option value="meeting">Meetings</option>
            <option value="customer">Customer</option>
            <option value="team">Team</option>
            <option value="finance">Finance</option>
          </select>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="timeline">Timeline View</option>
            <option value="calendar">Calendar View</option>
            <option value="gantt">Gantt Chart</option>
            <option value="milestones">Milestones View</option>
          </select>
        </div>
      </div>

      {/* Timeline View */}
      {viewMode === 'timeline' && (
        <div className="timeline-view">
          <div className="timeline-container">
            <div className="timeline-header">
              <h3>Business Timeline</h3>
              <div className="timeline-legend">
                <div className="legend-item">
                  <div className="legend-dot completed"></div>
                  <span>Completed</span>
                </div>
                <div className="legend-item">
                  <div className="legend-dot in-progress"></div>
                  <span>In Progress</span>
                </div>
                <div className="legend-item">
                  <div className="legend-dot planned"></div>
                  <span>Planned</span>
                </div>
              </div>
            </div>
            <div className="timeline-content">
              <div className="timeline-line"></div>
              {data.events?.map((event, index) => (
                <div 
                  key={event.id} 
                  className={`timeline-item ${event.status}`}
                  onClick={() => setSelectedEvent(event)}
                >
                  <div className="timeline-marker">
                    <div className={`timeline-dot ${event.status}`}></div>
                    <div className="timeline-date">{formatDateShort(event.startDate)}</div>
                  </div>
                  <div className="timeline-content-item">
                    <div className="timeline-item-header">
                      <div className="item-category-icon">{getCategoryIcon(event.category)}</div>
                      <div className="item-title">{event.title}</div>
                      <div className={`item-priority ${event.priority}`}>
                        {event.priority.toUpperCase()}
                      </div>
                    </div>
                    <div className="item-description">{event.description}</div>
                    <div className="item-details">
                      <div className="detail-item">
                        <span className="detail-label">Owner:</span>
                        <span className="detail-value">{event.owner}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Budget:</span>
                        <span className="detail-value">${event.budget?.toLocaleString()}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Progress:</span>
                        <div className="progress-bar">
                          <div 
                            className="progress-fill"
                            style={{ 
                              width: `${event.progress}%`,
                              backgroundColor: getProgressColor(event.progress)
                            }}
                          ></div>
                        </div>
                        <span className="progress-text">{event.progress}%</span>
                      </div>
                    </div>
                    <div className="item-tags">
                      {event.tags?.map((tag, tagIndex) => (
                        <span key={tagIndex} className="tag">{tag}</span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quarter Overview */}
          <div className="quarter-overview">
            <h3>Quarterly Overview</h3>
            <div className="quarter-grid">
              {data.timeline?.quarters?.map((quarter, index) => (
                <div key={index} className={`quarter-card ${quarter.status}`}>
                  <div className="quarter-header">
                    <div className="quarter-name">{quarter.name}</div>
                    <div className="quarter-period">{quarter.period}</div>
                  </div>
                  <div className="quarter-stats">
                    <div className="stat-item">
                      <div className="stat-value">{quarter.achievements}</div>
                      <div className="stat-label">Achievements</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">{quarter.events}</div>
                      <div className="stat-label">Events</div>
                    </div>
                    <div className="stat-item">
                      <div className="stat-value">${quarter.budget?.toLocaleString()}</div>
                      <div className="stat-label">Budget</div>
                    </div>
                  </div>
                  <div className="quarter-highlights">
                    <div className="highlights-label">Key Highlights:</div>
                    <ul>
                      {quarter.highlights?.map((highlight, hIndex) => (
                        <li key={hIndex}>{highlight}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Calendar View */}
      {viewMode === 'calendar' && (
        <div className="calendar-view">
          <div className="calendar-header">
            <h3>{data.calendar?.currentMonth?.name}</h3>
            <div className="calendar-navigation">
              <button className="nav-button">‹ Previous</button>
              <button className="nav-button">Today</button>
              <button className="nav-button">Next ›</button>
            </div>
          </div>
          <div className="calendar-grid">
            <div className="calendar-weekdays">
              {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                <div key={day} className="weekday">{day}</div>
              ))}
            </div>
            <div className="calendar-weeks">
              {data.calendar?.currentMonth?.weeks?.map((week, weekIndex) => (
                <div key={weekIndex} className="calendar-week">
                  {week.days.map((day, dayIndex) => (
                    <div 
                      key={dayIndex} 
                      className={`calendar-day ${day.isCurrentMonth ? 'current-month' : 'other-month'} ${day.isToday ? 'today' : ''}`}
                    >
                      <div className="day-number">{new Date(day.date).getDate()}</div>
                      <div className="day-events">
                        {day.events?.map((eventId, eventIndex) => {
                          const event = data.events?.find(e => e.id === eventId);
                          return event ? (
                            <div 
                              key={eventIndex} 
                              className={`event-dot ${event.category}`}
                              title={event.title}
                              onClick={() => setSelectedEvent(event)}
                            ></div>
                          ) : null;
                        })}
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Gantt Chart View */}
      {viewMode === 'gantt' && (
        <div className="gantt-view">
          <div className="gantt-header">
            <h3>Project Gantt Chart</h3>
            <div className="gantt-controls">
              <button className="zoom-button">Zoom In</button>
              <button className="zoom-button">Zoom Out</button>
              <button className="zoom-button">Fit to Screen</button>
            </div>
          </div>
          <div className="gantt-chart">
            <div className="gantt-sidebar">
              <div className="gantt-sidebar-header">Projects</div>
              {data.projects?.map((project, index) => (
                <div key={index} className="gantt-project-row">
                  <div className="project-name">{project.name}</div>
                  <div className="project-team">{project.team}</div>
                  <div className="project-progress">{project.progress}%</div>
                </div>
              ))}
            </div>
            <div className="gantt-timeline">
              <div className="gantt-timeline-header">
                <div className="timeline-months">
                  {['Jul 2024', 'Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025'].map(month => (
                    <div key={month} className="timeline-month">{month}</div>
                  ))}
                </div>
              </div>
              <div className="gantt-bars">
                {data.projects?.map((project, index) => (
                  <div key={index} className="gantt-bar-row">
                    <div 
                      className={`gantt-bar ${project.status}`}
                      style={{
                        left: '10%',
                        width: '60%'
                      }}
                    >
                      <div 
                        className="gantt-progress"
                        style={{ width: `${project.progress}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Milestones View */}
      {viewMode === 'milestones' && (
        <div className="milestones-view">
          <div className="milestones-header">
            <h3>Key Milestones</h3>
            <div className="milestones-stats">
              <div className="milestone-stat">
                <div className="stat-value">{data.milestones?.filter(m => m.status === 'completed').length}</div>
                <div className="stat-label">Completed</div>
              </div>
              <div className="milestone-stat">
                <div className="stat-value">{data.milestones?.filter(m => m.status === 'in_progress').length}</div>
                <div className="stat-label">In Progress</div>
              </div>
              <div className="milestone-stat">
                <div className="stat-value">{data.milestones?.filter(m => m.status === 'planned').length}</div>
                <div className="stat-label">Planned</div>
              </div>
            </div>
          </div>
          <div className="milestones-grid">
            {data.milestones?.map((milestone, index) => (
              <div key={index} className={`milestone-card ${milestone.status}`}>
                <div className="milestone-header">
                  <div className="milestone-category-icon">{getCategoryIcon(milestone.category)}</div>
                  <div className="milestone-title">{milestone.title}</div>
                  <div className={`milestone-impact ${milestone.impact}`}>
                    {milestone.impact?.toUpperCase()}
                  </div>
                </div>
                <div className="milestone-date">
                  <span className="date-label">Target Date:</span>
                  <span className="date-value">{formatDate(milestone.date)}</span>
                </div>
                <div className="milestone-description">{milestone.description}</div>
                <div className="milestone-owner">
                  <span className="owner-label">Owner:</span>
                  <span className="owner-value">{milestone.owner}</span>
                </div>
                {milestone.achievements && milestone.achievements.length > 0 && (
                  <div className="milestone-achievements">
                    <div className="achievements-label">Achievements:</div>
                    <ul>
                      {milestone.achievements.map((achievement, aIndex) => (
                        <li key={aIndex}>{achievement}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className={`milestone-status ${milestone.status}`}>
                  {milestone.status.replace('_', ' ').toUpperCase()}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Event Details Modal */}
      {selectedEvent && (
        <div className="event-details-modal">
          <div className="modal-overlay" onClick={() => setSelectedEvent(null)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <div className="modal-title">
                <span className="event-icon">{getCategoryIcon(selectedEvent.category)}</span>
                <h2>{selectedEvent.title}</h2>
              </div>
              <button 
                className="close-button"
                onClick={() => setSelectedEvent(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="event-details">
                <div className="detail-section">
                  <h4>Description</h4>
                  <p>{selectedEvent.description}</p>
                </div>
                <div className="detail-section">
                  <h4>Timeline</h4>
                  <div className="timeline-details">
                    <div className="timeline-detail">
                      <span className="label">Start Date:</span>
                      <span className="value">{formatDate(selectedEvent.startDate)}</span>
                    </div>
                    <div className="timeline-detail">
                      <span className="label">End Date:</span>
                      <span className="value">{formatDate(selectedEvent.endDate)}</span>
                    </div>
                    <div className="timeline-detail">
                      <span className="label">Duration:</span>
                      <span className="value">
                        {Math.ceil((new Date(selectedEvent.endDate) - new Date(selectedEvent.startDate)) / (1000 * 60 * 60 * 24))} days
                      </span>
                    </div>
                  </div>
                </div>
                <div className="detail-section">
                  <h4>Project Details</h4>
                  <div className="project-details">
                    <div className="project-detail">
                      <span className="label">Owner:</span>
                      <span className="value">{selectedEvent.owner}</span>
                    </div>
                    <div className="project-detail">
                      <span className="label">Department:</span>
                      <span className="value">{selectedEvent.department}</span>
                    </div>
                    <div className="project-detail">
                      <span className="label">Priority:</span>
                      <span className={`value priority ${selectedEvent.priority}`}>
                        {selectedEvent.priority?.toUpperCase()}
                      </span>
                    </div>
                    <div className="project-detail">
                      <span className="label">Budget:</span>
                      <span className="value">${selectedEvent.budget?.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div className="detail-section">
                  <h4>Progress</h4>
                  <div className="progress-section">
                    <div className="progress-bar-large">
                      <div 
                        className="progress-fill-large"
                        style={{ 
                          width: `${selectedEvent.progress}%`,
                          backgroundColor: getProgressColor(selectedEvent.progress)
                        }}
                      ></div>
                    </div>
                    <div className="progress-text-large">{selectedEvent.progress}% Complete</div>
                  </div>
                </div>
                <div className="detail-section">
                  <h4>Team Members</h4>
                  <div className="attendees-list">
                    {selectedEvent.attendees?.map((attendee, index) => (
                      <span key={index} className="attendee-tag">{attendee}</span>
                    ))}
                  </div>
                </div>
                <div className="detail-section">
                  <h4>Tags</h4>
                  <div className="tags-list">
                    {selectedEvent.tags?.map((tag, index) => (
                      <span key={index} className="detail-tag">{tag}</span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BusinessTimelineCalendar;
