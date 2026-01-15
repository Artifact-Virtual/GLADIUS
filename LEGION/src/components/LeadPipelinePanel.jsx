import React, { useState, useEffect } from 'react';

const LeadPipelinePanel = ({ pipelineData, onStageUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('pipeline'); // 'pipeline', 'analytics', 'forecast'
  const [selectedLead, setSelectedLead] = useState(null);
  const [timeRange, setTimeRange] = useState('month');
  const [data, setData] = useState({
    stages: [],
    leads: [],
    metrics: {},
    forecast: {},
    conversion: {}
  });

  useEffect(() => {
    const loadPipelineData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided pipelineData or fetch from API
        if (pipelineData) {
          setData(pipelineData);
        } else {
          const response = await fetch(`/api/enterprise/lead-pipeline?timeRange=${timeRange}`);
          if (!response.ok) throw new Error('Failed to load pipeline data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading pipeline data:', err);
        setError(err.message);
        
        // Mock data for development
        const mockData = {
          stages: [
            {
              id: 'awareness',
              name: 'Awareness',
              description: 'Initial contact and awareness generation',
              order: 1,
              color: '#4facfe',
              targetDays: 7,
              conversionRate: 45,
              leads: 23,
              value: 115000
            },
            {
              id: 'interest',
              name: 'Interest',
              description: 'Demonstrated interest and engagement',
              order: 2,
              color: '#00f2fe',
              targetDays: 14,
              conversionRate: 65,
              leads: 18,
              value: 162000
            },
            {
              id: 'consideration',
              name: 'Consideration',
              description: 'Active evaluation and consideration',
              order: 3,
              color: '#48bb78',
              targetDays: 21,
              conversionRate: 75,
              leads: 12,
              value: 180000
            },
            {
              id: 'intent',
              name: 'Intent',
              description: 'Strong purchase intent and qualification',
              order: 4,
              color: '#ed8936',
              targetDays: 30,
              conversionRate: 85,
              leads: 8,
              value: 160000
            },
            {
              id: 'purchase',
              name: 'Purchase',
              description: 'Active purchase process and negotiation',
              order: 5,
              color: '#9f7aea',
              targetDays: 45,
              conversionRate: 92,
              leads: 5,
              value: 125000
            },
            {
              id: 'retention',
              name: 'Retention',
              description: 'Customer retention and expansion',
              order: 6,
              color: '#38b2ac',
              targetDays: 365,
              conversionRate: 88,
              leads: 15,
              value: 450000
            }
          ],
          leads: [
            {
              id: 'lead_001',
              name: 'TechCorp Solutions',
              contact: 'Sarah Johnson',
              email: 'sarah.j@techcorp.com',
              phone: '+1-555-0123',
              company: 'TechCorp Solutions',
              industry: 'Technology',
              size: 'Enterprise',
              stage: 'intent',
              value: 25000,
              probability: 85,
              source: 'LinkedIn',
              assignedTo: 'Sales Agent Alpha',
              createdDate: '2024-06-15',
              lastContact: '2024-07-20',
              nextAction: 'Send proposal presentation',
              nextActionDate: '2024-07-25',
              notes: 'Very interested in AI consulting services for digital transformation project',
              tags: ['AI Consulting', 'Digital Transformation', 'Enterprise'],
              activities: [
                { date: '2024-07-20', type: 'call', description: 'Discovery call completed', agent: 'Sales Agent Alpha' },
                { date: '2024-07-18', type: 'email', description: 'Sent technical overview', agent: 'Marketing Agent' },
                { date: '2024-07-15', type: 'meeting', description: 'Initial consultation', agent: 'Sales Agent Alpha' }
              ],
              score: 92
            },
            {
              id: 'lead_002',
              name: 'Innovation Labs',
              contact: 'Michael Chen',
              email: 'mchen@innovationlabs.io',
              phone: '+1-555-0456',
              company: 'Innovation Labs',
              industry: 'Research',
              size: 'Mid-Market',
              stage: 'consideration',
              value: 18000,
              probability: 70,
              source: 'Website',
              assignedTo: 'Sales Agent Beta',
              createdDate: '2024-06-20',
              lastContact: '2024-07-19',
              nextAction: 'Schedule technical demo',
              nextActionDate: '2024-07-24',
              notes: 'Looking for AI research assistance and automation solutions',
              tags: ['AI Research', 'Automation', 'Mid-Market'],
              activities: [
                { date: '2024-07-19', type: 'email', description: 'Follow-up after demo', agent: 'Sales Agent Beta' },
                { date: '2024-07-17', type: 'demo', description: 'Product demonstration', agent: 'Technical Agent' },
                { date: '2024-07-10', type: 'call', description: 'Initial inquiry call', agent: 'Sales Agent Beta' }
              ],
              score: 78
            },
            {
              id: 'lead_003',
              name: 'Global Industries',
              contact: 'Emily Rodriguez',
              email: 'e.rodriguez@globalind.com',
              phone: '+1-555-0789',
              company: 'Global Industries',
              industry: 'Manufacturing',
              size: 'Enterprise',
              stage: 'purchase',
              value: 35000,
              probability: 95,
              source: 'Referral',
              assignedTo: 'Sales Agent Alpha',
              createdDate: '2024-05-10',
              lastContact: '2024-07-21',
              nextAction: 'Contract review meeting',
              nextActionDate: '2024-07-23',
              notes: 'Ready to sign contract pending final legal review',
              tags: ['Manufacturing', 'Process Optimization', 'Enterprise'],
              activities: [
                { date: '2024-07-21', type: 'meeting', description: 'Contract discussion', agent: 'Sales Agent Alpha' },
                { date: '2024-07-18', type: 'proposal', description: 'Final proposal sent', agent: 'Sales Agent Alpha' },
                { date: '2024-07-15', type: 'negotiation', description: 'Price negotiation', agent: 'Sales Manager' }
              ],
              score: 98
            },
            {
              id: 'lead_004',
              name: 'StartupXYZ',
              contact: 'David Kim',
              email: 'david@startupxyz.com',
              phone: '+1-555-0321',
              company: 'StartupXYZ',
              industry: 'Fintech',
              size: 'Small Business',
              stage: 'interest',
              value: 8000,
              probability: 55,
              source: 'Social Media',
              assignedTo: 'Sales Agent Gamma',
              createdDate: '2024-07-01',
              lastContact: '2024-07-20',
              nextAction: 'Send pricing information',
              nextActionDate: '2024-07-24',
              notes: 'Startup looking for AI integration in financial services',
              tags: ['Fintech', 'AI Integration', 'Startup'],
              activities: [
                { date: '2024-07-20', type: 'call', description: 'Needs assessment call', agent: 'Sales Agent Gamma' },
                { date: '2024-07-15', type: 'email', description: 'Initial contact response', agent: 'Marketing Agent' },
                { date: '2024-07-08', type: 'inquiry', description: 'Website inquiry received', agent: 'Lead Agent' }
              ],
              score: 65
            }
          ],
          metrics: {
            totalValue: 1192000,
            weightedValue: 987000,
            conversionRate: 72,
            averageDealSize: 21500,
            salesCycle: 42,
            leadsThisMonth: 23,
            leadsLastMonth: 19,
            conversionThisMonth: 8,
            conversionLastMonth: 6,
            velocity: 12.5,
            winRate: 68
          },
          forecast: {
            thisQuarter: {
              conservative: 285000,
              likely: 425000,
              optimistic: 650000,
              confidence: 78
            },
            nextQuarter: {
              conservative: 320000,
              likely: 480000,
              optimistic: 720000,
              confidence: 65
            },
            trends: {
              velocity: 15,
              volume: 8,
              value: 12,
              conversion: -3
            }
          },
          conversion: {
            byStage: {
              awareness: { rate: 45, change: 5 },
              interest: { rate: 65, change: -2 },
              consideration: { rate: 75, change: 3 },
              intent: { rate: 85, change: 7 },
              purchase: { rate: 92, change: 1 },
              retention: { rate: 88, change: 4 }
            },
            bySource: {
              linkedin: { rate: 78, volume: 35 },
              website: { rate: 65, volume: 28 },
              referral: { rate: 92, volume: 15 },
              social: { rate: 45, volume: 22 }
            },
            byIndustry: {
              technology: { rate: 82, volume: 45 },
              manufacturing: { rate: 75, volume: 25 },
              fintech: { rate: 68, volume: 20 },
              research: { rate: 71, volume: 10 }
            }
          }
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadPipelineData();
    const interval = setInterval(loadPipelineData, 120000); // Refresh every 2 minutes
    return () => clearInterval(interval);
  }, [timeRange, pipelineData]);

  const handleStageUpdate = (leadId, newStage) => {
    if (onStageUpdate) {
      onStageUpdate(newStage, { leadId, newStage });
    }
    // Update local data
    setData(prev => ({
      ...prev,
      leads: prev.leads.map(lead => 
        lead.id === leadId ? { ...lead, stage: newStage } : lead
      )
    }));
  };

  const handleLeadClick = (lead) => {
    setSelectedLead(lead);
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value}%`;
  };

  const getStageLeads = (stageId) => {
    return data.leads.filter(lead => lead.stage === stageId);
  };

  const getActivityIcon = (type) => {
    const icons = {
      call: '📞',
      email: '📧',
      meeting: '🤝',
      demo: '💻',
      proposal: '📋',
      negotiation: '💰',
      inquiry: '❓'
    };
    return icons[type] || '📌';
  };

  if (loading) {
    return (
      <div className="lead-pipeline-panel loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading pipeline data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lead-pipeline-panel error">
        <div className="error-message">
          <h3>Error Loading Pipeline Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="lead-pipeline-panel">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Lead Pipeline Progression</h2>
          <p>Track leads through the sales funnel and optimize conversion rates</p>
        </div>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-selector"
          >
            <option value="week">This Week</option>
            <option value="month">This Month</option>
            <option value="quarter">This Quarter</option>
            <option value="year">This Year</option>
          </select>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="pipeline">Pipeline View</option>
            <option value="analytics">Analytics View</option>
            <option value="forecast">Forecast View</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="pipeline-metrics">
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.metrics.totalValue)}</div>
            <div className="metric-label">Total Pipeline Value</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.metrics.weightedValue)}</div>
            <div className="metric-label">Weighted Value</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-value">{formatPercentage(data.metrics.conversionRate)}</div>
            <div className="metric-label">Conversion Rate</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">⏱️</div>
          <div className="metric-content">
            <div className="metric-value">{data.metrics.salesCycle} days</div>
            <div className="metric-label">Avg Sales Cycle</div>
          </div>
        </div>
      </div>

      {/* Pipeline View */}
      {viewMode === 'pipeline' && (
        <div className="pipeline-view">
          <div className="pipeline-stages">
            {data.stages.map((stage) => {
              const stageLeads = getStageLeads(stage.id);
              return (
                <div key={stage.id} className="pipeline-stage" style={{ borderTopColor: stage.color }}>
                  <div className="stage-header">
                    <h3>{stage.name}</h3>
                    <div className="stage-stats">
                      <span className="lead-count">{stageLeads.length} leads</span>
                      <span className="stage-value">{formatCurrency(stage.value)}</span>
                    </div>
                  </div>
                  
                  <div className="stage-metrics">
                    <div className="stage-metric">
                      <span className="metric-label">Conversion Rate</span>
                      <span className="metric-value">{formatPercentage(stage.conversionRate)}</span>
                    </div>
                    <div className="stage-metric">
                      <span className="metric-label">Target Days</span>
                      <span className="metric-value">{stage.targetDays}d</span>
                    </div>
                  </div>

                  <div className="stage-leads">
                    {stageLeads.map((lead) => (
                      <div 
                        key={lead.id} 
                        className="lead-card"
                        onClick={() => handleLeadClick(lead)}
                      >
                        <div className="lead-header">
                          <div className="lead-name">{lead.name}</div>
                          <div className="lead-value">{formatCurrency(lead.value)}</div>
                        </div>
                        <div className="lead-details">
                          <div className="lead-contact">{lead.contact}</div>
                          <div className="lead-company">{lead.company}</div>
                        </div>
                        <div className="lead-meta">
                          <span className="lead-probability">{formatPercentage(lead.probability)}</span>
                          <span className="lead-score">Score: {lead.score}</span>
                        </div>
                        <div className="lead-actions">
                          <select 
                            value={lead.stage}
                            onChange={(e) => handleStageUpdate(lead.id, e.target.value)}
                            className="stage-selector"
                            onClick={(e) => e.stopPropagation()}
                          >
                            {data.stages.map(s => (
                              <option key={s.id} value={s.id}>{s.name}</option>
                            ))}
                          </select>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Analytics View */}
      {viewMode === 'analytics' && (
        <div className="analytics-view">
          <div className="analytics-grid">
            {/* Conversion by Stage */}
            <div className="analytics-section">
              <h3>Conversion by Stage</h3>
              <div className="conversion-chart">
                {Object.entries(data.conversion.byStage).map(([stage, stats]) => (
                  <div key={stage} className="conversion-item">
                    <div className="conversion-label">{stage.charAt(0).toUpperCase() + stage.slice(1)}</div>
                    <div className="conversion-bar">
                      <div 
                        className="conversion-fill"
                        style={{ width: `${stats.rate}%` }}
                      ></div>
                    </div>
                    <div className="conversion-stats">
                      <span className="conversion-rate">{formatPercentage(stats.rate)}</span>
                      <span className={`conversion-change ${stats.change >= 0 ? 'positive' : 'negative'}`}>
                        {stats.change >= 0 ? '+' : ''}{stats.change}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Conversion by Source */}
            <div className="analytics-section">
              <h3>Performance by Source</h3>
              <div className="source-chart">
                {Object.entries(data.conversion.bySource).map(([source, stats]) => (
                  <div key={source} className="source-item">
                    <div className="source-header">
                      <span className="source-name">{source.charAt(0).toUpperCase() + source.slice(1)}</span>
                      <span className="source-volume">{stats.volume} leads</span>
                    </div>
                    <div className="source-rate">{formatPercentage(stats.rate)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Conversion by Industry */}
            <div className="analytics-section">
              <h3>Performance by Industry</h3>
              <div className="industry-chart">
                {Object.entries(data.conversion.byIndustry).map(([industry, stats]) => (
                  <div key={industry} className="industry-item">
                    <div className="industry-header">
                      <span className="industry-name">{industry.charAt(0).toUpperCase() + industry.slice(1)}</span>
                      <span className="industry-volume">{stats.volume} leads</span>
                    </div>
                    <div className="industry-rate">{formatPercentage(stats.rate)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Monthly Trends */}
            <div className="analytics-section">
              <h3>Monthly Performance</h3>
              <div className="monthly-stats">
                <div className="monthly-item">
                  <div className="monthly-label">Leads This Month</div>
                  <div className="monthly-value">{data.metrics.leadsThisMonth}</div>
                  <div className={`monthly-change ${data.metrics.leadsThisMonth >= data.metrics.leadsLastMonth ? 'positive' : 'negative'}`}>
                    {data.metrics.leadsThisMonth >= data.metrics.leadsLastMonth ? '+' : ''}
                    {((data.metrics.leadsThisMonth - data.metrics.leadsLastMonth) / data.metrics.leadsLastMonth * 100).toFixed(1)}%
                  </div>
                </div>
                <div className="monthly-item">
                  <div className="monthly-label">Conversions This Month</div>
                  <div className="monthly-value">{data.metrics.conversionThisMonth}</div>
                  <div className={`monthly-change ${data.metrics.conversionThisMonth >= data.metrics.conversionLastMonth ? 'positive' : 'negative'}`}>
                    {data.metrics.conversionThisMonth >= data.metrics.conversionLastMonth ? '+' : ''}
                    {((data.metrics.conversionThisMonth - data.metrics.conversionLastMonth) / data.metrics.conversionLastMonth * 100).toFixed(1)}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Forecast View */}
      {viewMode === 'forecast' && (
        <div className="forecast-view">
          <div className="forecast-grid">
            {/* Quarterly Forecast */}
            <div className="forecast-section">
              <h3>Quarterly Revenue Forecast</h3>
              <div className="forecast-quarters">
                <div className="quarter-forecast">
                  <h4>This Quarter</h4>
                  <div className="forecast-scenarios">
                    <div className="scenario conservative">
                      <span className="scenario-label">Conservative</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.thisQuarter.conservative)}</span>
                    </div>
                    <div className="scenario likely">
                      <span className="scenario-label">Likely</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.thisQuarter.likely)}</span>
                    </div>
                    <div className="scenario optimistic">
                      <span className="scenario-label">Optimistic</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.thisQuarter.optimistic)}</span>
                    </div>
                  </div>
                  <div className="forecast-confidence">
                    <span>Confidence: {data.forecast.thisQuarter.confidence}%</span>
                  </div>
                </div>

                <div className="quarter-forecast">
                  <h4>Next Quarter</h4>
                  <div className="forecast-scenarios">
                    <div className="scenario conservative">
                      <span className="scenario-label">Conservative</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.nextQuarter.conservative)}</span>
                    </div>
                    <div className="scenario likely">
                      <span className="scenario-label">Likely</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.nextQuarter.likely)}</span>
                    </div>
                    <div className="scenario optimistic">
                      <span className="scenario-label">Optimistic</span>
                      <span className="scenario-value">{formatCurrency(data.forecast.nextQuarter.optimistic)}</span>
                    </div>
                  </div>
                  <div className="forecast-confidence">
                    <span>Confidence: {data.forecast.nextQuarter.confidence}%</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Trend Analysis */}
            <div className="forecast-section">
              <h3>Trend Analysis</h3>
              <div className="trends-grid">
                <div className="trend-item">
                  <div className="trend-label">Pipeline Velocity</div>
                  <div className={`trend-value ${data.forecast.trends.velocity >= 0 ? 'positive' : 'negative'}`}>
                    {data.forecast.trends.velocity >= 0 ? '+' : ''}{data.forecast.trends.velocity}%
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-label">Lead Volume</div>
                  <div className={`trend-value ${data.forecast.trends.volume >= 0 ? 'positive' : 'negative'}`}>
                    {data.forecast.trends.volume >= 0 ? '+' : ''}{data.forecast.trends.volume}%
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-label">Deal Value</div>
                  <div className={`trend-value ${data.forecast.trends.value >= 0 ? 'positive' : 'negative'}`}>
                    {data.forecast.trends.value >= 0 ? '+' : ''}{data.forecast.trends.value}%
                  </div>
                </div>
                <div className="trend-item">
                  <div className="trend-label">Conversion Rate</div>
                  <div className={`trend-value ${data.forecast.trends.conversion >= 0 ? 'positive' : 'negative'}`}>
                    {data.forecast.trends.conversion >= 0 ? '+' : ''}{data.forecast.trends.conversion}%
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Lead Details Modal */}
      {selectedLead && (
        <div className="lead-details-modal">
          <div className="modal-overlay" onClick={() => setSelectedLead(null)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <h2>{selectedLead.name}</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedLead(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="lead-info-grid">
                <div className="info-section">
                  <h3>Contact Information</h3>
                  <div className="info-details">
                    <div className="info-item">
                      <label>Contact:</label>
                      <span>{selectedLead.contact}</span>
                    </div>
                    <div className="info-item">
                      <label>Email:</label>
                      <span>{selectedLead.email}</span>
                    </div>
                    <div className="info-item">
                      <label>Phone:</label>
                      <span>{selectedLead.phone}</span>
                    </div>
                    <div className="info-item">
                      <label>Company:</label>
                      <span>{selectedLead.company}</span>
                    </div>
                  </div>
                </div>

                <div className="info-section">
                  <h3>Lead Details</h3>
                  <div className="info-details">
                    <div className="info-item">
                      <label>Industry:</label>
                      <span>{selectedLead.industry}</span>
                    </div>
                    <div className="info-item">
                      <label>Company Size:</label>
                      <span>{selectedLead.size}</span>
                    </div>
                    <div className="info-item">
                      <label>Source:</label>
                      <span>{selectedLead.source}</span>
                    </div>
                    <div className="info-item">
                      <label>Assigned To:</label>
                      <span>{selectedLead.assignedTo}</span>
                    </div>
                  </div>
                </div>

                <div className="info-section">
                  <h3>Sales Metrics</h3>
                  <div className="info-details">
                    <div className="info-item">
                      <label>Deal Value:</label>
                      <span>{formatCurrency(selectedLead.value)}</span>
                    </div>
                    <div className="info-item">
                      <label>Probability:</label>
                      <span>{formatPercentage(selectedLead.probability)}</span>
                    </div>
                    <div className="info-item">
                      <label>Lead Score:</label>
                      <span>{selectedLead.score}</span>
                    </div>
                    <div className="info-item">
                      <label>Stage:</label>
                      <span>{data.stages.find(s => s.id === selectedLead.stage)?.name}</span>
                    </div>
                  </div>
                </div>

                <div className="info-section full-width">
                  <h3>Next Actions</h3>
                  <div className="next-action">
                    <div className="action-item">
                      <label>Next Action:</label>
                      <span>{selectedLead.nextAction}</span>
                    </div>
                    <div className="action-item">
                      <label>Due Date:</label>
                      <span>{new Date(selectedLead.nextActionDate).toLocaleDateString()}</span>
                    </div>
                  </div>
                </div>

                <div className="info-section full-width">
                  <h3>Activity History</h3>
                  <div className="activity-history">
                    {selectedLead.activities.map((activity, index) => (
                      <div key={index} className="activity-entry">
                        <div className="activity-icon">{getActivityIcon(activity.type)}</div>
                        <div className="activity-details">
                          <div className="activity-description">{activity.description}</div>
                          <div className="activity-meta">
                            <span>{new Date(activity.date).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>{activity.agent}</span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="info-section full-width">
                  <h3>Notes</h3>
                  <div className="lead-notes">
                    <p>{selectedLead.notes}</p>
                  </div>
                </div>

                <div className="info-section full-width">
                  <h3>Tags</h3>
                  <div className="lead-tags">
                    {selectedLead.tags.map((tag, index) => (
                      <span key={index} className="tag">{tag}</span>
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

export default LeadPipelinePanel;
