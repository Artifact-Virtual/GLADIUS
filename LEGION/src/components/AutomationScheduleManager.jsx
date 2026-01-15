import React, { useState, useEffect, useCallback } from 'react';

const AutomationScheduleManager = () => {
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('calendar'); // calendar, list, timeline
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [selectedSchedule, setSelectedSchedule] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    frequency: 'all'
  });
  const [calendarData, setCalendarData] = useState({});
  const [newSchedule, setNewSchedule] = useState({
    name: '',
    description: '',
    type: 'workflow',
    frequency: 'daily',
    startTime: '09:00',
    timezone: 'UTC',
    enabled: true,
    workflow: '',
    parameters: ''
  });

  const generateSchedules = useCallback(() => {
    const scheduleTypes = ['workflow', 'report', 'backup', 'sync', 'cleanup', 'analysis'];
    const frequencies = ['once', 'daily', 'weekly', 'monthly', 'hourly', 'custom'];
    const statuses = ['active', 'paused', 'completed', 'failed', 'scheduled'];
    const timezones = ['UTC', 'EST', 'PST', 'CET', 'JST'];
    
    const scheduleNames = [
      'Daily Sales Report Generation', 'Weekly Performance Analysis', 'Monthly Financial Backup',
      'Customer Data Synchronization', 'System Log Cleanup', 'Inventory Level Check',
      'Marketing Campaign Analysis', 'Database Maintenance', 'Security Scan',
      'User Activity Report', 'Revenue Dashboard Update', 'Compliance Check',
      'Lead Generation Report', 'Product Catalog Sync', 'Email Campaign Send',
      'Data Quality Validation', 'Performance Optimization', 'Automated Backup',
      'Market Research Analysis', 'Customer Feedback Processing'
    ];

    return Array.from({ length: 20 }, (_, index) => {
      const startDate = new Date();
      startDate.setDate(startDate.getDate() + Math.floor(Math.random() * 30) - 15);
      const nextRun = new Date();
      nextRun.setDate(nextRun.getDate() + Math.floor(Math.random() * 7));
      
      return {
        id: `schedule-${index + 1}`,
        name: scheduleNames[index] || `Schedule ${index + 1}`,
        description: `Automated ${scheduleTypes[Math.floor(Math.random() * scheduleTypes.length)]} schedule for business operations`,
        type: scheduleTypes[Math.floor(Math.random() * scheduleTypes.length)],
        frequency: frequencies[Math.floor(Math.random() * frequencies.length)],
        status: statuses[Math.floor(Math.random() * statuses.length)],
        enabled: Math.random() > 0.3,
        startTime: `${Math.floor(Math.random() * 24).toString().padStart(2, '0')}:${['00', '15', '30', '45'][Math.floor(Math.random() * 4)]}`,
        timezone: timezones[Math.floor(Math.random() * timezones.length)],
        startDate: startDate.toISOString(),
        endDate: index % 5 === 0 ? null : new Date(Date.now() + (Math.random() * 365 + 30) * 86400000).toISOString(),
        nextRun: nextRun.toISOString(),
        lastRun: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
        executionCount: Math.floor(Math.random() * 500) + 10,
        successCount: Math.floor(Math.random() * 450) + 8,
        failureCount: Math.floor(Math.random() * 50) + 2,
        avgDuration: Math.floor(Math.random() * 300000) + 30000, // milliseconds
        maxDuration: Math.floor(Math.random() * 600000) + 60000,
        workflow: {
          id: `workflow-${Math.floor(Math.random() * 10) + 1}`,
          name: `Workflow ${Math.floor(Math.random() * 10) + 1}`,
          version: `v${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 10)}`
        },
        parameters: {
          timeout: Math.floor(Math.random() * 3600) + 300,
          retryAttempts: Math.floor(Math.random() * 5) + 1,
          priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
          notifications: Math.random() > 0.5,
          environment: ['production', 'staging', 'development'][Math.floor(Math.random() * 3)]
        },
        cronExpression: index % 3 === 0 ? '0 9 * * 1-5' : index % 3 === 1 ? '0 */6 * * *' : '0 2 1 * *',
        tags: Array.from({ length: Math.floor(Math.random() * 4) + 1 }, () => 
          ['automated', 'critical', 'reporting', 'maintenance', 'sync', 'analysis'][Math.floor(Math.random() * 6)]
        ),
        owner: ['System Admin', 'Operations Team', 'Business Analyst', 'Development Team'][Math.floor(Math.random() * 4)],
        createdBy: ['admin', 'user123', 'scheduler', 'system'][Math.floor(Math.random() * 4)],
        createdAt: new Date(Date.now() - Math.random() * 90 * 86400000).toISOString(),
        updatedAt: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
        dependencies: Array.from({ length: Math.floor(Math.random() * 3) }, () => 
          `schedule-${Math.floor(Math.random() * 20) + 1}`
        ).filter(dep => dep !== `schedule-${index + 1}`),
        notifications: {
          onSuccess: Math.random() > 0.7,
          onFailure: Math.random() > 0.3,
          onStart: Math.random() > 0.8,
          recipients: ['admin@company.com', 'ops@company.com']
        },
        monitoring: {
          healthScore: Math.floor(Math.random() * 40) + 60,
          reliability: (Math.random() * 20 + 80).toFixed(1),
          performance: (Math.random() * 30 + 70).toFixed(1)
        }
      };
    });
  }, []);

  const generateCalendarData = useCallback((schedules) => {
    const calendarData = {};
    const today = new Date();
    
    // Generate calendar data for current month ± 2 months
    for (let monthOffset = -2; monthOffset <= 2; monthOffset++) {
      const currentDate = new Date(today.getFullYear(), today.getMonth() + monthOffset, 1);
      const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
      
      for (let day = 1; day <= daysInMonth; day++) {
        const dateKey = `${currentDate.getFullYear()}-${(currentDate.getMonth() + 1).toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;
        calendarData[dateKey] = [];
        
        // Add some random scheduled items for demo
        schedules.forEach(schedule => {
          if (schedule.enabled && schedule.status === 'active') {
            // Simple logic to determine if schedule runs on this day
            const probability = schedule.frequency === 'daily' ? 1.0 : 
                               schedule.frequency === 'weekly' ? 0.14 : 
                               schedule.frequency === 'monthly' ? 0.03 : 0.1;
            
            if (Math.random() < probability) {
              calendarData[dateKey].push({
                id: schedule.id,
                name: schedule.name,
                time: schedule.startTime,
                type: schedule.type,
                status: 'scheduled'
              });
            }
          }
        });
      }
    }
    
    return calendarData;
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1200));
        const generatedSchedules = generateSchedules();
        setSchedules(generatedSchedules);
        setCalendarData(generateCalendarData(generatedSchedules));
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading schedule data:', error);
      }
    };

    loadData();
  }, [generateSchedules, generateCalendarData]);

  const filteredSchedules = schedules.filter(schedule => {
    return (filters.status === 'all' || schedule.status === filters.status) &&
           (filters.type === 'all' || schedule.type === filters.type) &&
           (filters.frequency === 'all' || schedule.frequency === filters.frequency);
  });

  const handleCreateSchedule = () => {
    const schedule = {
      ...newSchedule,
      id: `schedule-${schedules.length + 1}`,
      status: 'scheduled',
      executionCount: 0,
      successCount: 0,
      failureCount: 0,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      nextRun: new Date(Date.now() + 86400000).toISOString(),
      lastRun: null,
      owner: 'Current User',
      monitoring: { healthScore: 100, reliability: 100, performance: 100 }
    };
    
    setSchedules([...schedules, schedule]);
    setCalendarData(generateCalendarData([...schedules, schedule]));
    setShowCreateModal(false);
    setNewSchedule({
      name: '',
      description: '',
      type: 'workflow',
      frequency: 'daily',
      startTime: '09:00',
      timezone: 'UTC',
      enabled: true,
      workflow: '',
      parameters: ''
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#28a745';
      case 'paused': return '#ffc107';
      case 'completed': return '#17a2b8';
      case 'failed': return '#dc3545';
      case 'scheduled': return '#6f42c1';
      default: return '#6c757d';
    }
  };

  const getTypeColor = (type) => {
    switch (type) {
      case 'workflow': return '#667eea';
      case 'report': return '#764ba2';
      case 'backup': return '#f093fb';
      case 'sync': return '#4facfe';
      case 'cleanup': return '#43e97b';
      case 'analysis': return '#fa709a';
      default: return '#666';
    }
  };

  const renderCalendarView = () => {
    const today = new Date();
    const currentMonth = selectedDate.getMonth();
    const currentYear = selectedDate.getFullYear();
    const firstDay = new Date(currentYear, currentMonth, 1);
    const lastDay = new Date(currentYear, currentMonth + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startDate = new Date(firstDay);
    startDate.setDate(startDate.getDate() - firstDay.getDay());

    const calendarDays = [];
    for (let i = 0; i < 42; i++) {
      const date = new Date(startDate);
      date.setDate(startDate.getDate() + i);
      const dateKey = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
      const schedulesForDay = calendarData[dateKey] || [];
      
      calendarDays.push({
        date: date,
        dateKey: dateKey,
        isCurrentMonth: date.getMonth() === currentMonth,
        isToday: date.toDateString() === today.toDateString(),
        schedules: schedulesForDay
      });
    }

    return (
      <div className="calendar-view">
        <div className="calendar-header">
          <div className="month-navigation">
            <button onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setMonth(newDate.getMonth() - 1);
              setSelectedDate(newDate);
            }}>
              <i className="fas fa-chevron-left"></i>
            </button>
            <h3>
              {selectedDate.toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
            </h3>
            <button onClick={() => {
              const newDate = new Date(selectedDate);
              newDate.setMonth(newDate.getMonth() + 1);
              setSelectedDate(newDate);
            }}>
              <i className="fas fa-chevron-right"></i>
            </button>
          </div>
          <button className="today-btn" onClick={() => setSelectedDate(new Date())}>
            Today
          </button>
        </div>

        <div className="calendar-grid">
          <div className="weekday-headers">
            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
              <div key={day} className="weekday-header">{day}</div>
            ))}
          </div>
          <div className="calendar-days">
            {calendarDays.map((day, index) => (
              <div 
                key={index} 
                className={`calendar-day ${day.isCurrentMonth ? 'current-month' : 'other-month'} ${day.isToday ? 'today' : ''}`}
              >
                <div className="day-number">{day.date.getDate()}</div>
                <div className="day-schedules">
                  {day.schedules.slice(0, 3).map(schedule => (
                    <div 
                      key={schedule.id}
                      className="schedule-indicator"
                      style={{backgroundColor: getTypeColor(schedule.type)}}
                      title={`${schedule.name} at ${schedule.time}`}
                    >
                      <span className="schedule-time">{schedule.time}</span>
                      <span className="schedule-name">{schedule.name.substring(0, 15)}...</span>
                    </div>
                  ))}
                  {day.schedules.length > 3 && (
                    <div className="more-schedules">+{day.schedules.length - 3} more</div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderListView = () => (
    <div className="schedules-list">
      {filteredSchedules.map(schedule => (
        <div key={schedule.id} className="schedule-item">
          <div className="schedule-header">
            <div className="schedule-title">
              <h3>{schedule.name}</h3>
              <span className="schedule-type" style={{backgroundColor: getTypeColor(schedule.type)}}>
                {schedule.type}
              </span>
            </div>
            <div className="schedule-status">
              <span className="status-badge" style={{backgroundColor: getStatusColor(schedule.status)}}>
                {schedule.status}
              </span>
              <label className="toggle-switch">
                <input 
                  type="checkbox" 
                  checked={schedule.enabled}
                  onChange={() => {
                    const updatedSchedules = schedules.map(s => 
                      s.id === schedule.id ? {...s, enabled: !s.enabled} : s
                    );
                    setSchedules(updatedSchedules);
                  }}
                />
                <span className="slider"></span>
              </label>
            </div>
          </div>

          <div className="schedule-details">
            <p className="schedule-description">{schedule.description}</p>
            <div className="schedule-meta">
              <div className="meta-item">
                <i className="fas fa-clock"></i>
                <span>{schedule.frequency} at {schedule.startTime} {schedule.timezone}</span>
              </div>
              <div className="meta-item">
                <i className="fas fa-calendar"></i>
                <span>Next: {new Date(schedule.nextRun).toLocaleString()}</span>
              </div>
              <div className="meta-item">
                <i className="fas fa-user"></i>
                <span>{schedule.owner}</span>
              </div>
            </div>
          </div>

          <div className="schedule-stats">
            <div className="stat-item">
              <div className="stat-value">{schedule.executionCount}</div>
              <div className="stat-label">Executions</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{((schedule.successCount / schedule.executionCount) * 100 || 0).toFixed(1)}%</div>
              <div className="stat-label">Success Rate</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{Math.floor(schedule.avgDuration / 1000)}s</div>
              <div className="stat-label">Avg Duration</div>
            </div>
            <div className="stat-item">
              <div className="stat-value">{schedule.monitoring.healthScore}</div>
              <div className="stat-label">Health Score</div>
            </div>
          </div>

          <div className="schedule-actions">
            <button className="action-btn run">
              <i className="fas fa-play"></i>
              Run Now
            </button>
            <button className="action-btn edit">
              <i className="fas fa-edit"></i>
              Edit
            </button>
            <button 
              className="action-btn details"
              onClick={() => setSelectedSchedule(schedule)}
            >
              <i className="fas fa-info-circle"></i>
              Details
            </button>
            <button className="action-btn delete">
              <i className="fas fa-trash"></i>
              Delete
            </button>
          </div>
        </div>
      ))}
    </div>
  );

  const renderTimelineView = () => {
    const timelineData = filteredSchedules
      .filter(s => s.enabled && s.status === 'active')
      .sort((a, b) => new Date(a.nextRun) - new Date(b.nextRun))
      .slice(0, 10);

    return (
      <div className="timeline-view">
        <div className="timeline-container">
          {timelineData.map((schedule, index) => (
            <div key={schedule.id} className="timeline-item">
              <div className="timeline-marker" style={{backgroundColor: getTypeColor(schedule.type)}}></div>
              <div className="timeline-content">
                <div className="timeline-time">
                  {new Date(schedule.nextRun).toLocaleDateString()} at {schedule.startTime}
                </div>
                <div className="timeline-schedule">
                  <h4>{schedule.name}</h4>
                  <p>{schedule.description}</p>
                </div>
                <div className="timeline-meta">
                  <span className="timeline-type">{schedule.type}</span>
                  <span className="timeline-frequency">{schedule.frequency}</span>
                  <span className="timeline-owner">{schedule.owner}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="automation-schedule-manager loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading automation schedules...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="automation-schedule-manager">
      <div className="manager-header">
        <div className="header-left">
          <h2>Automation Schedule Manager</h2>
          <p>Manage and monitor automated workflow schedules</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'calendar' ? 'active' : ''}`}
              onClick={() => setViewMode('calendar')}
            >
              <i className="fas fa-calendar"></i>
              Calendar
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <i className="fas fa-list"></i>
              List
            </button>
            <button 
              className={`view-btn ${viewMode === 'timeline' ? 'active' : ''}`}
              onClick={() => setViewMode('timeline')}
            >
              <i className="fas fa-stream"></i>
              Timeline
            </button>
          </div>
          <button 
            className="create-schedule-btn"
            onClick={() => setShowCreateModal(true)}
          >
            <i className="fas fa-plus"></i>
            Create Schedule
          </button>
        </div>
      </div>

      {(viewMode === 'list' || viewMode === 'timeline') && (
        <div className="manager-controls">
          <div className="filter-controls">
            <select value={filters.status} onChange={(e) => setFilters({...filters, status: e.target.value})}>
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>

            <select value={filters.type} onChange={(e) => setFilters({...filters, type: e.target.value})}>
              <option value="all">All Types</option>
              <option value="workflow">Workflow</option>
              <option value="report">Report</option>
              <option value="backup">Backup</option>
              <option value="sync">Sync</option>
            </select>

            <select value={filters.frequency} onChange={(e) => setFilters({...filters, frequency: e.target.value})}>
              <option value="all">All Frequencies</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="hourly">Hourly</option>
            </select>
          </div>
        </div>
      )}

      <div className="manager-content">
        {viewMode === 'calendar' && renderCalendarView()}
        {viewMode === 'list' && renderListView()}
        {viewMode === 'timeline' && renderTimelineView()}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="create-schedule-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Create New Schedule</h3>
              <button className="close-btn" onClick={() => setShowCreateModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="form-group">
                <label>Schedule Name</label>
                <input 
                  type="text"
                  value={newSchedule.name}
                  onChange={(e) => setNewSchedule({...newSchedule, name: e.target.value})}
                  placeholder="Enter schedule name"
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newSchedule.description}
                  onChange={(e) => setNewSchedule({...newSchedule, description: e.target.value})}
                  placeholder="Enter description"
                  rows="3"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Type</label>
                  <select 
                    value={newSchedule.type}
                    onChange={(e) => setNewSchedule({...newSchedule, type: e.target.value})}
                  >
                    <option value="workflow">Workflow</option>
                    <option value="report">Report</option>
                    <option value="backup">Backup</option>
                    <option value="sync">Sync</option>
                    <option value="cleanup">Cleanup</option>
                    <option value="analysis">Analysis</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Frequency</label>
                  <select 
                    value={newSchedule.frequency}
                    onChange={(e) => setNewSchedule({...newSchedule, frequency: e.target.value})}
                  >
                    <option value="once">Once</option>
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                    <option value="custom">Custom</option>
                  </select>
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>Start Time</label>
                  <input 
                    type="time"
                    value={newSchedule.startTime}
                    onChange={(e) => setNewSchedule({...newSchedule, startTime: e.target.value})}
                  />
                </div>

                <div className="form-group">
                  <label>Timezone</label>
                  <select 
                    value={newSchedule.timezone}
                    onChange={(e) => setNewSchedule({...newSchedule, timezone: e.target.value})}
                  >
                    <option value="UTC">UTC</option>
                    <option value="EST">EST</option>
                    <option value="PST">PST</option>
                    <option value="CET">CET</option>
                    <option value="JST">JST</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label className="checkbox-label">
                  <input 
                    type="checkbox"
                    checked={newSchedule.enabled}
                    onChange={(e) => setNewSchedule({...newSchedule, enabled: e.target.checked})}
                  />
                  Enable immediately
                </label>
              </div>

              <div className="modal-actions">
                <button 
                  className="cancel-btn"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancel
                </button>
                <button 
                  className="create-btn"
                  onClick={handleCreateSchedule}
                  disabled={!newSchedule.name || !newSchedule.description}
                >
                  Create Schedule
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {selectedSchedule && (
        <div className="modal-overlay" onClick={() => setSelectedSchedule(null)}>
          <div className="schedule-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedSchedule.name}</h3>
              <button className="close-btn" onClick={() => setSelectedSchedule(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="detail-section">
                <h4>Schedule Information</h4>
                <div className="info-grid">
                  <div className="info-item">
                    <span className="label">Type:</span>
                    <span className="value">{selectedSchedule.type}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Frequency:</span>
                    <span className="value">{selectedSchedule.frequency}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Start Time:</span>
                    <span className="value">{selectedSchedule.startTime} {selectedSchedule.timezone}</span>
                  </div>
                  <div className="info-item">
                    <span className="label">Next Run:</span>
                    <span className="value">{new Date(selectedSchedule.nextRun).toLocaleString()}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Performance Metrics</h4>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <div className="metric-value">{selectedSchedule.executionCount}</div>
                    <div className="metric-label">Total Executions</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{selectedSchedule.successCount}</div>
                    <div className="metric-label">Successful</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{selectedSchedule.failureCount}</div>
                    <div className="metric-label">Failed</div>
                  </div>
                  <div className="metric-card">
                    <div className="metric-value">{selectedSchedule.monitoring.healthScore}%</div>
                    <div className="metric-label">Health Score</div>
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

export default AutomationScheduleManager;
