import React, { useState, useEffect } from 'react';

const RevenueVisualizationPanel = ({ revenueData, onTargetUpdate }) => {
  const [timeRange, setTimeRange] = useState('quarter');
  const [viewMode, setViewMode] = useState('comparison'); // 'comparison', 'trends', 'breakdown'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState({
    current: 0,
    target: 0,
    monthly: [],
    quarterly: [],
    projections: [],
    breakdown: {},
    trends: {}
  });

  useEffect(() => {
    const loadRevenueData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided revenueData or fetch from API
        if (revenueData) {
          setData(revenueData);
        } else {
          const response = await fetch(`/api/enterprise/revenue-analytics?timeRange=${timeRange}`);
          if (!response.ok) throw new Error('Failed to load revenue data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading revenue data:', err);
        setError(err.message);
        
        // Mock data for development
        const mockData = {
          current: 987500,
          target: 1250000,
          monthly: [
            { month: 'Jan', actual: 95000, target: 104167, budget: 100000 },
            { month: 'Feb', actual: 102000, target: 104167, budget: 100000 },
            { month: 'Mar', actual: 118000, target: 104167, budget: 100000 },
            { month: 'Apr', actual: 99000, target: 104167, budget: 100000 },
            { month: 'May', actual: 115000, target: 104167, budget: 100000 },
            { month: 'Jun', actual: 108000, target: 104167, budget: 100000 },
            { month: 'Jul', actual: 94000, target: 104167, budget: 100000 },
            { month: 'Aug', actual: 121000, target: 104167, budget: 100000 },
            { month: 'Sep', actual: 135000, target: 104167, budget: 100000 },
            { month: 'Oct', actual: 0, target: 104167, budget: 100000 }
          ],
          quarterly: [
            { quarter: 'Q1', actual: 315000, target: 312500, budget: 300000, year: 2024 },
            { quarter: 'Q2', actual: 322000, target: 312500, budget: 300000, year: 2024 },
            { quarter: 'Q3', actual: 350000, target: 312500, budget: 300000, year: 2024 },
            { quarter: 'Q4', actual: 0, target: 312500, budget: 300000, year: 2024 }
          ],
          projections: [
            { month: 'Oct', projected: 110000, confidence: 85 },
            { month: 'Nov', projected: 125000, confidence: 78 },
            { month: 'Dec', projected: 135000, confidence: 72 }
          ],
          breakdown: {
            byProduct: [
              { name: 'Enterprise Solutions', revenue: 425000, percentage: 43 },
              { name: 'Consultation Services', revenue: 298000, percentage: 30 },
              { name: 'Support & Maintenance', revenue: 189000, percentage: 19 },
              { name: 'Training & Certification', revenue: 75500, percentage: 8 }
            ],
            byRegion: [
              { name: 'North America', revenue: 492000, percentage: 50 },
              { name: 'Europe', revenue: 295000, percentage: 30 },
              { name: 'Asia Pacific', revenue: 148000, percentage: 15 },
              { name: 'Other', revenue: 52500, percentage: 5 }
            ],
            byChannel: [
              { name: 'Direct Sales', revenue: 592500, percentage: 60 },
              { name: 'Partner Channel', revenue: 296000, percentage: 30 },
              { name: 'Online Sales', revenue: 99000, percentage: 10 }
            ]
          },
          trends: {
            growthRate: 15.7,
            yearOverYear: 23.4,
            quarterOverQuarter: 8.7,
            monthOverMonth: 11.6,
            seasonality: {
              Q1: -5,
              Q2: 0,
              Q3: 12,
              Q4: 18
            }
          }
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadRevenueData();
    const interval = setInterval(loadRevenueData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [timeRange, revenueData]);

  const calculateProgress = () => {
    if (!data.target || data.target === 0) return 0;
    return Math.min((data.current / data.target) * 100, 100);
  };

  const calculateVariance = () => {
    return data.current - data.target;
  };

  const getProgressColor = (progress) => {
    if (progress >= 95) return '#48bb78';
    if (progress >= 80) return '#4299e1';
    if (progress >= 60) return '#ed8936';
    return '#e53e3e';
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
    return `${value.toFixed(1)}%`;
  };

  if (loading) {
    return (
      <div className="revenue-visualization-panel loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading revenue data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="revenue-visualization-panel error">
        <div className="error-message">
          <h3>Error Loading Revenue Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const progress = calculateProgress();
  const variance = calculateVariance();

  return (
    <div className="revenue-visualization-panel">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Revenue Target vs Actual</h2>
          <p>Track revenue performance against targets and projections</p>
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
          </select>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="comparison">Target vs Actual</option>
            <option value="trends">Trends Analysis</option>
            <option value="breakdown">Revenue Breakdown</option>
          </select>
        </div>
      </div>

      {/* Main Metrics */}
      <div className="main-metrics">
        <div className="metric-card primary">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <div className="metric-label">Current Revenue</div>
            <div className="metric-value">{formatCurrency(data.current)}</div>
            <div className="metric-progress">
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ 
                    width: `${progress}%`,
                    backgroundColor: getProgressColor(progress)
                  }}
                ></div>
              </div>
              <span className="progress-text">{formatPercentage(progress)} of target</span>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">🎯</div>
          <div className="metric-content">
            <div className="metric-label">Target Revenue</div>
            <div className="metric-value">{formatCurrency(data.target)}</div>
            <div className="metric-info">
              <span className={`variance ${variance >= 0 ? 'positive' : 'negative'}`}>
                {variance >= 0 ? '+' : ''}{formatCurrency(variance)}
              </span>
            </div>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-label">Growth Rate</div>
            <div className="metric-value">{formatPercentage(data.trends?.growthRate || 0)}</div>
            <div className="metric-info">
              <span className="trend-indicator positive">
                ↗ {formatPercentage(data.trends?.yearOverYear || 0)} YoY
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Content based on view mode */}
      <div className="panel-content">
        {viewMode === 'comparison' && (
          <div className="comparison-view">
            {/* Monthly Comparison Chart */}
            <div className="chart-section">
              <h3>Monthly Performance</h3>
              <div className="monthly-chart">
                {data.monthly?.map((month, index) => (
                  <div key={index} className="month-bar">
                    <div className="month-label">{month.month}</div>
                    <div className="bar-container">
                      <div 
                        className="bar actual"
                        style={{ 
                          height: `${(month.actual / Math.max(...data.monthly.map(m => m.target))) * 100}%`,
                          backgroundColor: month.actual >= month.target ? '#48bb78' : '#e53e3e'
                        }}
                        title={`Actual: ${formatCurrency(month.actual)}`}
                      ></div>
                      <div 
                        className="bar target"
                        style={{ 
                          height: `${(month.target / Math.max(...data.monthly.map(m => m.target))) * 100}%`
                        }}
                        title={`Target: ${formatCurrency(month.target)}`}
                      ></div>
                    </div>
                    <div className="month-values">
                      <span className="actual-value">{formatCurrency(month.actual)}</span>
                      <span className="target-value">{formatCurrency(month.target)}</span>
                    </div>
                  </div>
                ))}
              </div>
              <div className="chart-legend">
                <div className="legend-item">
                  <div className="legend-color actual"></div>
                  <span>Actual Revenue</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color target"></div>
                  <span>Target Revenue</span>
                </div>
              </div>
            </div>

            {/* Quarterly Summary */}
            <div className="quarterly-summary">
              <h3>Quarterly Summary</h3>
              <div className="quarters-grid">
                {data.quarterly?.map((quarter, index) => (
                  <div key={index} className="quarter-card">
                    <div className="quarter-header">
                      <h4>{quarter.quarter} {quarter.year}</h4>
                      <span className={`status ${quarter.actual >= quarter.target ? 'achieved' : quarter.actual > 0 ? 'in-progress' : 'pending'}`}>
                        {quarter.actual >= quarter.target ? 'Target Achieved' : quarter.actual > 0 ? 'In Progress' : 'Pending'}
                      </span>
                    </div>
                    <div className="quarter-metrics">
                      <div className="quarter-metric">
                        <span className="metric-label">Actual</span>
                        <span className="metric-value">{formatCurrency(quarter.actual)}</span>
                      </div>
                      <div className="quarter-metric">
                        <span className="metric-label">Target</span>
                        <span className="metric-value">{formatCurrency(quarter.target)}</span>
                      </div>
                      <div className="quarter-metric">
                        <span className="metric-label">Performance</span>
                        <span className={`metric-value ${quarter.actual >= quarter.target ? 'positive' : 'negative'}`}>
                          {quarter.target > 0 ? formatPercentage((quarter.actual / quarter.target) * 100) : '0%'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'trends' && (
          <div className="trends-view">
            {/* Growth Trends */}
            <div className="trends-section">
              <h3>Growth Trends</h3>
              <div className="trends-grid">
                <div className="trend-card">
                  <div className="trend-icon">📈</div>
                  <div className="trend-content">
                    <div className="trend-label">Month over Month</div>
                    <div className="trend-value positive">{formatPercentage(data.trends?.monthOverMonth || 0)}</div>
                  </div>
                </div>
                <div className="trend-card">
                  <div className="trend-icon">📊</div>
                  <div className="trend-content">
                    <div className="trend-label">Quarter over Quarter</div>
                    <div className="trend-value positive">{formatPercentage(data.trends?.quarterOverQuarter || 0)}</div>
                  </div>
                </div>
                <div className="trend-card">
                  <div className="trend-icon">📅</div>
                  <div className="trend-content">
                    <div className="trend-label">Year over Year</div>
                    <div className="trend-value positive">{formatPercentage(data.trends?.yearOverYear || 0)}</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Projections */}
            <div className="projections-section">
              <h3>Revenue Projections</h3>
              <div className="projections-list">
                {data.projections?.map((projection, index) => (
                  <div key={index} className="projection-item">
                    <div className="projection-month">{projection.month}</div>
                    <div className="projection-amount">{formatCurrency(projection.projected)}</div>
                    <div className="projection-confidence">
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill"
                          style={{ width: `${projection.confidence}%` }}
                        ></div>
                      </div>
                      <span>{projection.confidence}% confidence</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Seasonality */}
            <div className="seasonality-section">
              <h3>Seasonal Patterns</h3>
              <div className="seasonality-chart">
                {Object.entries(data.trends?.seasonality || {}).map(([quarter, variance]) => (
                  <div key={quarter} className="season-bar">
                    <div className="season-label">{quarter}</div>
                    <div className="season-bar-container">
                      <div 
                        className={`season-fill ${variance >= 0 ? 'positive' : 'negative'}`}
                        style={{ 
                          height: `${Math.abs(variance) * 2}px`,
                          backgroundColor: variance >= 0 ? '#48bb78' : '#e53e3e'
                        }}
                      ></div>
                    </div>
                    <div className="season-value">{variance >= 0 ? '+' : ''}{variance}%</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {viewMode === 'breakdown' && (
          <div className="breakdown-view">
            {/* By Product */}
            <div className="breakdown-section">
              <h3>Revenue by Product</h3>
              <div className="breakdown-chart">
                {data.breakdown?.byProduct?.map((product, index) => (
                  <div key={index} className="breakdown-item">
                    <div className="breakdown-label">
                      <span className="label-text">{product.name}</span>
                      <span className="label-percentage">{product.percentage}%</span>
                    </div>
                    <div className="breakdown-bar">
                      <div 
                        className="breakdown-fill"
                        style={{ 
                          width: `${product.percentage}%`,
                          backgroundColor: `hsl(${index * 60}, 70%, 50%)`
                        }}
                      ></div>
                    </div>
                    <div className="breakdown-value">{formatCurrency(product.revenue)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* By Region */}
            <div className="breakdown-section">
              <h3>Revenue by Region</h3>
              <div className="breakdown-chart">
                {data.breakdown?.byRegion?.map((region, index) => (
                  <div key={index} className="breakdown-item">
                    <div className="breakdown-label">
                      <span className="label-text">{region.name}</span>
                      <span className="label-percentage">{region.percentage}%</span>
                    </div>
                    <div className="breakdown-bar">
                      <div 
                        className="breakdown-fill"
                        style={{ 
                          width: `${region.percentage}%`,
                          backgroundColor: `hsl(${index * 90}, 70%, 50%)`
                        }}
                      ></div>
                    </div>
                    <div className="breakdown-value">{formatCurrency(region.revenue)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* By Channel */}
            <div className="breakdown-section">
              <h3>Revenue by Channel</h3>
              <div className="breakdown-chart">
                {data.breakdown?.byChannel?.map((channel, index) => (
                  <div key={index} className="breakdown-item">
                    <div className="breakdown-label">
                      <span className="label-text">{channel.name}</span>
                      <span className="label-percentage">{channel.percentage}%</span>
                    </div>
                    <div className="breakdown-bar">
                      <div 
                        className="breakdown-fill"
                        style={{ 
                          width: `${channel.percentage}%`,
                          backgroundColor: `hsl(${index * 120}, 70%, 50%)`
                        }}
                      ></div>
                    </div>
                    <div className="breakdown-value">{formatCurrency(channel.revenue)}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RevenueVisualizationPanel;
