import React, { useState, useEffect } from 'react';

const AutomatedReportSystem = ({ onComponentUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeView, setActiveView] = useState('dashboard');
  const [selectedReport, setSelectedReport] = useState(null);
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    priority: 'all',
    agent: 'all',
    dateRange: 'all'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('created_desc');
  const [data, setData] = useState({
    reports: [],
    templates: [],
    schedules: [],
    analytics: {},
    agents: []
  });

  useEffect(() => {
    const loadReportData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Simulate API calls to report services
        const [
          reportsResponse,
          templatesResponse,
          schedulesResponse,
          analyticsResponse,
          agentsResponse
        ] = await Promise.allSettled([
          fetch('/api/enterprise/reports'),
          fetch('/api/enterprise/report-templates'),
          fetch('/api/enterprise/report-schedules'),
          fetch('/api/enterprise/report-analytics'),
          fetch('/api/enterprise/intelligence-agents')
        ]);

        // Process responses or use mock data
        const mockData = {
          reports: [
            {
              id: 'rpt_001',
              title: 'Q4 2024 Market Intelligence Report',
              type: 'market_analysis',
              status: 'completed',
              priority: 'high',
              agent: 'Market Analysis Agent',
              template: 'market_intelligence_template',
              createdAt: '2024-10-15T09:30:00Z',
              completedAt: '2024-10-15T11:45:00Z',
              fileSize: 2.4,
              format: 'PDF',
              pages: 45,
              downloadCount: 23,
              shareCount: 8,
              viewCount: 156,
              rating: 4.8,
              confidence: 94,
              accuracy: 92,
              dataPoints: 1247,
              sources: 12,
              executionTime: 135, // minutes
              summary: 'Comprehensive analysis of Q4 market trends, competitive landscape, and growth opportunities in the AI consulting sector.',
              keyFindings: [
                'AI consulting market grew 18% in Q4 2024',
                'Healthcare and finance sectors show highest adoption rates',
                'Pricing pressure increasing in mid-market segment',
                'Compliance requirements driving premium service demand'
              ],
              tags: ['market', 'trends', 'ai-consulting', 'q4-2024'],
              downloadUrl: '/api/reports/download/rpt_001',
              previewUrl: '/api/reports/preview/rpt_001'
            },
            {
              id: 'rpt_002',
              title: 'Customer Sentiment Analysis - October 2024',
              type: 'customer_analysis',
              status: 'completed',
              priority: 'medium',
              agent: 'Customer Analytics Agent',
              template: 'customer_sentiment_template',
              createdAt: '2024-10-14T14:20:00Z',
              completedAt: '2024-10-14T16:35:00Z',
              fileSize: 1.8,
              format: 'PDF',
              pages: 32,
              downloadCount: 41,
              shareCount: 15,
              viewCount: 234,
              rating: 4.6,
              confidence: 89,
              accuracy: 87,
              dataPoints: 2156,
              sources: 8,
              executionTime: 95,
              summary: 'Monthly customer sentiment analysis showing improved satisfaction scores and identifying key improvement areas.',
              keyFindings: [
                'Overall satisfaction improved from 82% to 87%',
                'Support response time satisfaction up 23%',
                'Product feature requests increased 34%',
                'Referral likelihood increased to 68%'
              ],
              tags: ['customer', 'sentiment', 'satisfaction', 'monthly'],
              downloadUrl: '/api/reports/download/rpt_002',
              previewUrl: '/api/reports/preview/rpt_002'
            },
            {
              id: 'rpt_003',
              title: 'Competitive Intelligence Briefing',
              type: 'competitive_analysis',
              status: 'in_progress',
              priority: 'high',
              agent: 'Competitive Intelligence Agent',
              template: 'competitive_intelligence_template',
              createdAt: '2024-10-15T08:00:00Z',
              estimatedCompletion: '2024-10-15T18:00:00Z',
              progress: 67,
              fileSize: null,
              format: 'PDF',
              pages: null,
              downloadCount: 0,
              shareCount: 0,
              viewCount: 12,
              rating: null,
              confidence: null,
              accuracy: null,
              dataPoints: 894,
              sources: 15,
              executionTime: 380, // current runtime
              summary: 'Real-time analysis of competitor activities, pricing changes, and market positioning strategies.',
              keyFindings: [],
              tags: ['competitive', 'intelligence', 'real-time', 'monitoring'],
              downloadUrl: null,
              previewUrl: null
            },
            {
              id: 'rpt_004',
              title: 'Financial Performance Analytics - Q4 2024',
              type: 'financial_analysis',
              status: 'scheduled',
              priority: 'high',
              agent: 'Financial Analysis Agent',
              template: 'financial_performance_template',
              scheduledFor: '2024-10-16T09:00:00Z',
              createdAt: '2024-10-15T12:00:00Z',
              fileSize: null,
              format: 'PDF',
              pages: null,
              downloadCount: 0,
              shareCount: 0,
              viewCount: 3,
              rating: null,
              confidence: null,
              accuracy: null,
              dataPoints: 0,
              sources: 6,
              executionTime: 0,
              summary: 'Quarterly financial performance analysis with variance reporting and predictive modeling.',
              keyFindings: [],
              tags: ['financial', 'performance', 'quarterly', 'forecasting'],
              downloadUrl: null,
              previewUrl: null
            },
            {
              id: 'rpt_005',
              title: 'Technology Trend Analysis',
              type: 'technology_research',
              status: 'failed',
              priority: 'medium',
              agent: 'Research Agent',
              template: 'technology_trends_template',
              createdAt: '2024-10-13T10:15:00Z',
              failedAt: '2024-10-13T12:45:00Z',
              error: 'Data source temporarily unavailable',
              retry_count: 2,
              nextRetry: '2024-10-15T16:00:00Z',
              fileSize: null,
              format: 'PDF',
              pages: null,
              downloadCount: 0,
              shareCount: 0,
              viewCount: 8,
              rating: null,
              confidence: null,
              accuracy: null,
              dataPoints: 0,
              sources: 8,
              executionTime: 150,
              summary: 'Analysis of emerging technology trends and their potential business impact.',
              keyFindings: [],
              tags: ['technology', 'trends', 'research', 'emerging'],
              downloadUrl: null,
              previewUrl: null
            }
          ],
          templates: [
            {
              id: 'market_intelligence_template',
              name: 'Market Intelligence Report',
              description: 'Comprehensive market analysis with competitor intelligence and trend analysis',
              category: 'market_analysis',
              sections: [
                'Executive Summary',
                'Market Overview',
                'Competitive Landscape',
                'Trend Analysis',
                'Opportunities & Threats',
                'Recommendations'
              ],
              estimatedTime: 120, // minutes
              dataRequirements: ['Market Data', 'Competitor Information', 'Industry Reports'],
              outputFormat: 'PDF',
              customizable: true,
              usage: 45,
              rating: 4.7,
              lastUpdated: '2024-09-15T10:00:00Z'
            },
            {
              id: 'customer_sentiment_template',
              name: 'Customer Sentiment Analysis',
              description: 'Monthly customer feedback analysis with satisfaction metrics and insights',
              category: 'customer_analysis',
              sections: [
                'Summary Dashboard',
                'Sentiment Trends',
                'Satisfaction Metrics',
                'Feedback Categories',
                'Improvement Recommendations',
                'Action Plan'
              ],
              estimatedTime: 90,
              dataRequirements: ['Customer Surveys', 'Support Tickets', 'Reviews', 'NPS Scores'],
              outputFormat: 'PDF',
              customizable: true,
              usage: 38,
              rating: 4.5,
              lastUpdated: '2024-09-10T14:30:00Z'
            },
            {
              id: 'financial_performance_template',
              name: 'Financial Performance Report',
              description: 'Quarterly financial analysis with KPI tracking and variance reporting',
              category: 'financial_analysis',
              sections: [
                'Financial Summary',
                'Revenue Analysis',
                'Cost Analysis',
                'KPI Dashboard',
                'Variance Analysis',
                'Forecasting'
              ],
              estimatedTime: 75,
              dataRequirements: ['Financial Data', 'Budget Data', 'KPI Metrics', 'Market Data'],
              outputFormat: 'PDF',
              customizable: true,
              usage: 28,
              rating: 4.8,
              lastUpdated: '2024-09-20T09:15:00Z'
            }
          ],
          schedules: [
            {
              id: 'sched_001',
              name: 'Weekly Market Intelligence',
              template: 'market_intelligence_template',
              agent: 'Market Analysis Agent',
              frequency: 'weekly',
              dayOfWeek: 'monday',
              time: '09:00',
              timezone: 'UTC',
              status: 'active',
              lastRun: '2024-10-14T09:00:00Z',
              nextRun: '2024-10-21T09:00:00Z',
              successRate: 95,
              averageRunTime: 125,
              createdAt: '2024-08-15T10:00:00Z'
            },
            {
              id: 'sched_002',
              name: 'Monthly Customer Sentiment',
              template: 'customer_sentiment_template',
              agent: 'Customer Analytics Agent',
              frequency: 'monthly',
              dayOfMonth: 1,
              time: '08:00',
              timezone: 'UTC',
              status: 'active',
              lastRun: '2024-10-01T08:00:00Z',
              nextRun: '2024-11-01T08:00:00Z',
              successRate: 88,
              averageRunTime: 95,
              createdAt: '2024-07-20T12:30:00Z'
            },
            {
              id: 'sched_003',
              name: 'Quarterly Financial Analysis',
              template: 'financial_performance_template',
              agent: 'Financial Analysis Agent',
              frequency: 'quarterly',
              monthsOfYear: [1, 4, 7, 10],
              dayOfMonth: 15,
              time: '10:00',
              timezone: 'UTC',
              status: 'paused',
              lastRun: '2024-07-15T10:00:00Z',
              nextRun: '2025-01-15T10:00:00Z',
              successRate: 92,
              averageRunTime: 85,
              createdAt: '2024-01-10T15:45:00Z'
            }
          ],
          analytics: {
            totalReports: 156,
            completedReports: 134,
            failedReports: 8,
            inProgressReports: 14,
            averageCompletionTime: 105, // minutes
            successRate: 91.2,
            totalDownloads: 1247,
            totalViews: 5632,
            averageRating: 4.6,
            topTemplates: [
              { name: 'Market Intelligence', usage: 45, rating: 4.7 },
              { name: 'Customer Sentiment', usage: 38, rating: 4.5 },
              { name: 'Financial Performance', usage: 28, rating: 4.8 }
            ],
            topAgents: [
              { name: 'Market Analysis Agent', reports: 48, successRate: 95.8 },
              { name: 'Customer Analytics Agent', reports: 42, successRate: 88.1 },
              { name: 'Financial Analysis Agent', reports: 31, successRate: 93.5 }
            ]
          },
          agents: [
            { id: 'market_agent', name: 'Market Analysis Agent', status: 'active', reports: 48 },
            { id: 'customer_agent', name: 'Customer Analytics Agent', status: 'active', reports: 42 },
            { id: 'financial_agent', name: 'Financial Analysis Agent', status: 'active', reports: 31 },
            { id: 'research_agent', name: 'Research Agent', status: 'active', reports: 24 },
            { id: 'competitive_agent', name: 'Competitive Intelligence Agent', status: 'active', reports: 19 }
          ]
        };

        setData(mockData);
      } catch (err) {
        console.error('Error loading report data:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    loadReportData();
  }, []);

  const handleComponentUpdate = (component, updateData) => {
    if (onComponentUpdate) {
      onComponentUpdate(component, updateData);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatFileSize = (sizeInMB) => {
    return sizeInMB ? `${sizeInMB.toFixed(1)} MB` : 'N/A';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in_progress': return '#f59e0b';
      case 'scheduled': return '#6b7280';
      case 'failed': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return '#ef4444';
      case 'medium': return '#f59e0b';
      case 'low': return '#10b981';
      default: return '#6b7280';
    }
  };

  const filteredReports = data.reports
    .filter(report => {
      if (filters.status !== 'all' && report.status !== filters.status) return false;
      if (filters.type !== 'all' && report.type !== filters.type) return false;
      if (filters.priority !== 'all' && report.priority !== filters.priority) return false;
      if (filters.agent !== 'all' && report.agent !== filters.agent) return false;
      if (searchTerm && !report.title.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      return true;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'created_desc':
          return new Date(b.createdAt) - new Date(a.createdAt);
        case 'created_asc':
          return new Date(a.createdAt) - new Date(b.createdAt);
        case 'title_asc':
          return a.title.localeCompare(b.title);
        case 'title_desc':
          return b.title.localeCompare(a.title);
        case 'priority':
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          return priorityOrder[b.priority] - priorityOrder[a.priority];
        default:
          return 0;
      }
    });

  if (loading) {
    return (
      <div className="report-system loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading report system...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="report-system error">
        <div className="error-message">
          <h3>Error Loading Report System</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="automated-report-system">
      {/* Header */}
      <div className="system-header">
        <div className="header-content">
          <h1>Automated Report System</h1>
          <p>AI-generated reports, templates, and scheduling management</p>
        </div>
        <div className="header-actions">
          <button className="action-btn primary">📊 New Report</button>
          <button className="action-btn secondary">⚙️ Settings</button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="system-nav">
        {[
          { id: 'dashboard', label: 'Dashboard', icon: '📊' },
          { id: 'reports', label: 'Reports', icon: '📋' },
          { id: 'templates', label: 'Templates', icon: '📄' },
          { id: 'schedules', label: 'Schedules', icon: '⏰' },
          { id: 'analytics', label: 'Analytics', icon: '📈' }
        ].map(tab => (
          <button
            key={tab.id}
            className={`nav-tab ${activeView === tab.id ? 'active' : ''}`}
            onClick={() => setActiveView(tab.id)}
          >
            <span className="tab-icon">{tab.icon}</span>
            <span className="tab-label">{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Dashboard View */}
      {activeView === 'dashboard' && (
        <div className="dashboard-view">
          <div className="dashboard-metrics">
            <div className="metric-card">
              <div className="metric-icon">📋</div>
              <div className="metric-content">
                <div className="metric-value">{data.analytics.totalReports}</div>
                <div className="metric-label">Total Reports</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">✅</div>
              <div className="metric-content">
                <div className="metric-value">{data.analytics.completedReports}</div>
                <div className="metric-label">Completed</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">⏳</div>
              <div className="metric-content">
                <div className="metric-value">{data.analytics.inProgressReports}</div>
                <div className="metric-label">In Progress</div>
              </div>
            </div>
            <div className="metric-card">
              <div className="metric-icon">📈</div>
              <div className="metric-content">
                <div className="metric-value">{data.analytics.successRate}%</div>
                <div className="metric-label">Success Rate</div>
              </div>
            </div>
          </div>

          <div className="dashboard-grid">
            <div className="recent-reports">
              <h3>Recent Reports</h3>
              <div className="report-list">
                {data.reports.slice(0, 5).map(report => (
                  <div key={report.id} className="report-item">
                    <div className="report-info">
                      <div className="report-title">{report.title}</div>
                      <div className="report-meta">
                        <span>{report.agent}</span>
                        <span>•</span>
                        <span>{formatDate(report.createdAt)}</span>
                      </div>
                    </div>
                    <div className={`report-status ${report.status}`}>
                      {report.status.toUpperCase()}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="top-templates">
              <h3>Top Templates</h3>
              <div className="template-list">
                {data.analytics.topTemplates.map(template => (
                  <div key={template.name} className="template-item">
                    <div className="template-info">
                      <div className="template-name">{template.name}</div>
                      <div className="template-stats">
                        <span>Used {template.usage} times</span>
                        <span>Rating: {template.rating}/5</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="agent-performance">
              <h3>Agent Performance</h3>
              <div className="agent-list">
                {data.analytics.topAgents.map(agent => (
                  <div key={agent.name} className="agent-item">
                    <div className="agent-info">
                      <div className="agent-name">{agent.name}</div>
                      <div className="agent-stats">
                        <span>{agent.reports} reports</span>
                        <span>{agent.successRate}% success</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Reports View */}
      {activeView === 'reports' && (
        <div className="reports-view">
          {/* Filters and Search */}
          <div className="reports-controls">
            <div className="search-bar">
              <input
                type="text"
                placeholder="Search reports..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <button className="search-button">🔍</button>
            </div>
            <div className="filters">
              <select
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
                className="filter-select"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="in_progress">In Progress</option>
                <option value="scheduled">Scheduled</option>
                <option value="failed">Failed</option>
              </select>
              <select
                value={filters.type}
                onChange={(e) => setFilters({...filters, type: e.target.value})}
                className="filter-select"
              >
                <option value="all">All Types</option>
                <option value="market_analysis">Market Analysis</option>
                <option value="customer_analysis">Customer Analysis</option>
                <option value="financial_analysis">Financial Analysis</option>
                <option value="competitive_analysis">Competitive Analysis</option>
              </select>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="sort-select"
              >
                <option value="created_desc">Newest First</option>
                <option value="created_asc">Oldest First</option>
                <option value="title_asc">Title A-Z</option>
                <option value="title_desc">Title Z-A</option>
                <option value="priority">Priority</option>
              </select>
            </div>
          </div>

          {/* Reports Grid */}
          <div className="reports-grid">
            {filteredReports.map(report => (
              <div key={report.id} className={`report-card ${report.status}`}>
                <div className="card-header">
                  <div className="card-title">{report.title}</div>
                  <div className={`card-status ${report.status}`}>
                    {report.status.replace('_', ' ').toUpperCase()}
                  </div>
                </div>
                
                <div className="card-meta">
                  <div className="meta-row">
                    <span className="meta-label">Agent:</span>
                    <span className="meta-value">{report.agent}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-label">Type:</span>
                    <span className="meta-value">{report.type.replace('_', ' ')}</span>
                  </div>
                  <div className="meta-row">
                    <span className="meta-label">Priority:</span>
                    <span 
                      className="meta-value priority"
                      style={{ color: getPriorityColor(report.priority) }}
                    >
                      {report.priority.toUpperCase()}
                    </span>
                  </div>
                  {report.confidence && (
                    <div className="meta-row">
                      <span className="meta-label">Confidence:</span>
                      <span className="meta-value">{report.confidence}%</span>
                    </div>
                  )}
                </div>

                <div className="card-summary">{report.summary}</div>

                {report.status === 'in_progress' && (
                  <div className="progress-section">
                    <div className="progress-bar">
                      <div className="progress-fill" style={{ width: `${report.progress}%` }}></div>
                    </div>
                    <div className="progress-text">{report.progress}% Complete</div>
                  </div>
                )}

                <div className="card-stats">
                  <div className="stat-item">
                    <span className="stat-icon">📊</span>
                    <span>{report.dataPoints} data points</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">💾</span>
                    <span>{formatFileSize(report.fileSize)}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-icon">👁️</span>
                    <span>{report.viewCount} views</span>
                  </div>
                </div>

                <div className="card-actions">
                  {report.previewUrl && (
                    <button className="action-btn preview">👁️ Preview</button>
                  )}
                  {report.downloadUrl && (
                    <button className="action-btn download">📥 Download</button>
                  )}
                  <button className="action-btn share">🔗 Share</button>
                  <button className="action-btn more">⋯</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Templates View */}
      {activeView === 'templates' && (
        <div className="templates-view">
          <div className="view-header">
            <h2>Report Templates</h2>
            <button className="action-btn primary">➕ Create Template</button>
          </div>
          
          <div className="templates-grid">
            {data.templates.map(template => (
              <div key={template.id} className="template-card">
                <div className="template-header">
                  <div className="template-name">{template.name}</div>
                  <div className="template-rating">⭐ {template.rating}</div>
                </div>
                
                <div className="template-description">{template.description}</div>
                
                <div className="template-details">
                  <div className="detail-item">
                    <span className="detail-label">Category:</span>
                    <span className="detail-value">{template.category.replace('_', ' ')}</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Est. Time:</span>
                    <span className="detail-value">{template.estimatedTime} min</span>
                  </div>
                  <div className="detail-item">
                    <span className="detail-label">Usage:</span>
                    <span className="detail-value">{template.usage} reports</span>
                  </div>
                </div>

                <div className="template-sections">
                  <h4>Sections:</h4>
                  <ul>
                    {template.sections.slice(0, 4).map((section, index) => (
                      <li key={index}>{section}</li>
                    ))}
                    {template.sections.length > 4 && (
                      <li>+{template.sections.length - 4} more...</li>
                    )}
                  </ul>
                </div>

                <div className="template-actions">
                  <button className="action-btn primary">▶️ Use Template</button>
                  <button className="action-btn secondary">✏️ Edit</button>
                  <button className="action-btn secondary">👁️ Preview</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Continue with schedules and analytics views... */}
      
    </div>
  );
};

export default AutomatedReportSystem;
