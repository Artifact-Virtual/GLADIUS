import React, { useState, useEffect } from 'react';

const FinancialMetricsDashboard = ({ financialData, onMetricUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'cash_flow', 'profitability', 'budget'
  const [timeRange, setTimeRange] = useState('month');
  const [selectedMetric, setSelectedMetric] = useState(null);
  const [data, setData] = useState({
    summary: {},
    revenue: {},
    expenses: {},
    profitability: {},
    cashFlow: {},
    budget: {},
    trends: {},
    forecasts: {},
    kpis: {}
  });

  useEffect(() => {
    const loadFinancialData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided financialData or fetch from API
        if (financialData) {
          setData(financialData);
        } else {
          const response = await fetch(`/api/enterprise/financial-metrics?timeRange=${timeRange}`);
          if (!response.ok) throw new Error('Failed to load financial data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading financial data:', err);
        setError(err.message);
        
        // Mock comprehensive financial data for development
        const mockData = {
          summary: {
            totalRevenue: 387500,
            totalExpenses: 312800,
            netProfit: 74700,
            grossMargin: 68.5,
            netMargin: 19.3,
            ebitda: 98200,
            cashOnHand: 235000,
            burnRate: 28500,
            runway: 8.2, // months
            lastUpdated: '2024-07-22T10:30:00Z'
          },
          revenue: {
            monthly: [
              { month: 'Jan 2024', revenue: 28500, recurring: 18200, oneTime: 10300, growth: 12.5 },
              { month: 'Feb 2024', revenue: 31200, recurring: 19800, oneTime: 11400, growth: 9.5 },
              { month: 'Mar 2024', revenue: 34750, recurring: 22100, oneTime: 12650, growth: 11.4 },
              { month: 'Apr 2024', revenue: 38900, recurring: 24800, oneTime: 14100, growth: 11.9 },
              { month: 'May 2024', revenue: 42300, recurring: 27200, oneTime: 15100, growth: 8.7 },
              { month: 'Jun 2024', revenue: 46800, recurring: 30400, oneTime: 16400, growth: 10.6 },
              { month: 'Jul 2024', revenue: 51200, recurring: 33600, oneTime: 17600, growth: 9.4 }
            ],
            byProduct: [
              { name: 'AI Consulting Services', revenue: 185000, percentage: 47.7, growth: 15.2 },
              { name: 'Platform Subscriptions', revenue: 124500, percentage: 32.1, growth: 22.8 },
              { name: 'Custom Development', revenue: 58000, percentage: 15.0, growth: 8.5 },
              { name: 'Training & Support', revenue: 20000, percentage: 5.2, growth: 35.0 }
            ],
            byRegion: [
              { name: 'North America', revenue: 201250, percentage: 51.9, growth: 18.5 },
              { name: 'Europe', revenue: 116250, percentage: 30.0, growth: 12.3 },
              { name: 'Asia Pacific', revenue: 54000, percentage: 13.9, growth: 28.7 },
              { name: 'Other', revenue: 16000, percentage: 4.1, growth: 5.2 }
            ],
            forecast: {
              nextMonth: { conservative: 48000, likely: 55000, optimistic: 62000 },
              nextQuarter: { conservative: 168000, likely: 192000, optimistic: 220000 },
              confidence: 82
            }
          },
          expenses: {
            monthly: [
              { month: 'Jan 2024', total: 38200, operational: 22800, personnel: 12500, marketing: 2900 },
              { month: 'Feb 2024', total: 41500, operational: 24600, personnel: 13200, marketing: 3700 },
              { month: 'Mar 2024', total: 44300, operational: 26400, personnel: 14100, marketing: 3800 },
              { month: 'Apr 2024', total: 47800, operational: 28200, personnel: 15200, marketing: 4400 },
              { month: 'May 2024', total: 45600, operational: 27100, personnel: 14800, marketing: 3700 },
              { month: 'Jun 2024', total: 48900, operational: 29200, personnel: 15500, marketing: 4200 },
              { month: 'Jul 2024', total: 46500, operational: 27800, personnel: 14900, marketing: 3800 }
            ],
            byCategory: [
              { name: 'Personnel & Benefits', amount: 186500, percentage: 59.6, budget: 195000, variance: -4.4 },
              { name: 'Technology & Infrastructure', amount: 68200, percentage: 21.8, budget: 65000, variance: 4.9 },
              { name: 'Marketing & Sales', amount: 28500, percentage: 9.1, budget: 32000, variance: -10.9 },
              { name: 'Operations & Admin', amount: 18600, percentage: 5.9, budget: 20000, variance: -7.0 },
              { name: 'R&D', amount: 11000, percentage: 3.5, budget: 15000, variance: -26.7 }
            ],
            breakdown: {
              personnel: {
                salaries: 145000,
                benefits: 28500,
                contractors: 13000
              },
              technology: {
                cloudServices: 24500,
                software: 18700,
                hardware: 15200,
                security: 9800
              },
              marketing: {
                digitalAds: 12800,
                contentCreation: 8200,
                events: 4500,
                tools: 3000
              }
            }
          },
          profitability: {
            margins: {
              gross: 68.5,
              operating: 22.8,
              net: 19.3,
              ebitda: 25.3
            },
            trends: [
              { period: 'Q1 2024', gross: 65.2, operating: 18.5, net: 15.8, ebitda: 21.2 },
              { period: 'Q2 2024', gross: 67.8, operating: 21.2, net: 18.5, ebitda: 24.1 },
              { period: 'Q3 2024', gross: 68.5, operating: 22.8, net: 19.3, ebitda: 25.3 }
            ],
            benchmarks: {
              industry: { gross: 62.0, operating: 18.5, net: 12.8 },
              competition: { gross: 58.5, operating: 15.2, net: 10.5 }
            },
            drivers: [
              { factor: 'Service Premium', impact: 8.5, trend: 'positive' },
              { factor: 'Operational Efficiency', impact: 6.2, trend: 'positive' },
              { factor: 'Scale Economics', impact: 4.1, trend: 'positive' },
              { factor: 'Market Competition', impact: -2.8, trend: 'negative' }
            ]
          },
          cashFlow: {
            operating: 89500,
            investing: -24500,
            financing: 12000,
            netChange: 77000,
            beginning: 158000,
            ending: 235000,
            monthly: [
              { month: 'Jan 2024', operating: 8200, investing: -3500, financing: 2000, net: 6700 },
              { month: 'Feb 2024', operating: 9800, investing: -2200, financing: 0, net: 7600 },
              { month: 'Mar 2024', operating: 11200, investing: -4100, financing: 0, net: 7100 },
              { month: 'Apr 2024', operating: 13500, investing: -2800, financing: 0, net: 10700 },
              { month: 'May 2024', operating: 12800, investing: -3200, financing: 5000, net: 14600 },
              { month: 'Jun 2024', operating: 15600, investing: -4500, financing: 0, net: 11100 },
              { month: 'Jul 2024', operating: 18400, investing: -4200, financing: 5000, net: 19200 }
            ],
            projections: {
              nextMonth: 21500,
              nextQuarter: 67800,
              runway: 8.2
            }
          },
          budget: {
            annual: {
              revenue: { budgeted: 620000, actual: 387500, variance: 12.6, ytd: 62.5 },
              expenses: { budgeted: 485000, actual: 312800, variance: -8.2, ytd: 64.5 },
              profit: { budgeted: 135000, actual: 74700, variance: 38.2, ytd: 55.3 }
            },
            quarterly: {
              q1: { revenue: 94500, expenses: 124000, profit: -29500, status: 'completed' },
              q2: { revenue: 128800, expenses: 142200, profit: -13400, status: 'completed' },
              q3: { revenue: 164200, expenses: 146600, profit: 17600, status: 'in_progress' },
              q4: { revenue: 232500, expenses: 172200, profit: 60300, status: 'planned' }
            },
            departments: [
              { name: 'Engineering', budgeted: 180000, actual: 118500, utilized: 65.8, variance: -34.2 },
              { name: 'Sales & Marketing', budgeted: 125000, actual: 89200, utilized: 71.4, variance: -28.6 },
              { name: 'Operations', budgeted: 95000, actual: 67800, utilized: 71.4, variance: -28.6 },
              { name: 'General & Admin', budgeted: 85000, actual: 37300, utilized: 43.9, variance: -56.1 }
            ]
          },
          trends: {
            revenue: {
              growth: 18.5,
              momentum: 'accelerating',
              seasonality: 'Q4 strong',
              predictability: 'high'
            },
            expenses: {
              growth: 12.8,
              efficiency: 'improving',
              control: 'good',
              optimization: 'moderate'
            },
            profitability: {
              direction: 'improving',
              sustainability: 'strong',
              competitive: 'above average',
              outlook: 'positive'
            }
          },
          forecasts: {
            revenue: {
              nextMonth: 55000,
              nextQuarter: 192000,
              nextYear: 850000,
              confidence: 82,
              assumptions: ['Market growth continues', 'No major disruptions', 'Current pricing maintained']
            },
            expenses: {
              nextMonth: 48500,
              nextQuarter: 152000,
              nextYear: 625000,
              confidence: 88,
              drivers: ['Planned headcount growth', 'Technology investments', 'Market expansion']
            },
            profitability: {
              nextMonth: 6500,
              nextQuarter: 40000,
              nextYear: 225000,
              margin: 26.5,
              sustainability: 'high'
            }
          },
          kpis: {
            financial: {
              roa: 18.5, // Return on Assets
              roe: 24.8, // Return on Equity
              roic: 22.3, // Return on Invested Capital
              currentRatio: 2.8,
              quickRatio: 2.1,
              debtToEquity: 0.15,
              interestCoverage: 15.6
            },
            operational: {
              revenuePerEmployee: 155000,
              customerAcquisitionCost: 2800,
              lifetimeValue: 28500,
              churnRate: 3.2,
              grossRevenueRetention: 98.5,
              netRevenueRetention: 125.8
            },
            growth: {
              cagr: 28.5, // Compound Annual Growth Rate
              quarterlyGrowth: 18.5,
              marketShare: 4.2,
              customerGrowth: 22.8,
              aov: 12500 // Average Order Value
            }
          }
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadFinancialData();
    const interval = setInterval(loadFinancialData, 300000); // Refresh every 5 minutes
    return () => clearInterval(interval);
  }, [timeRange, financialData]);

  const handleMetricUpdate = (metricType, metricData) => {
    if (onMetricUpdate) {
      onMetricUpdate(metricType, metricData);
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatPercentage = (value, decimals = 1) => {
    return `${value.toFixed(decimals)}%`;
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('en-US').format(value);
  };

  const getVarianceColor = (variance) => {
    if (variance > 0) return '#10b981';
    if (variance < -10) return '#ef4444';
    return '#f59e0b';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'positive' || trend === 'improving' || trend === 'accelerating') return '📈';
    if (trend === 'negative' || trend === 'declining') return '📉';
    return '➡️';
  };

  if (loading) {
    return (
      <div className="financial-metrics-dashboard loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading financial data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="financial-metrics-dashboard error">
        <div className="error-message">
          <h3>Error Loading Financial Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="financial-metrics-dashboard">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Financial Metrics Dashboard</h2>
          <p>Comprehensive financial performance tracking and analysis</p>
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
            <option value="overview">Overview</option>
            <option value="cash_flow">Cash Flow</option>
            <option value="profitability">Profitability</option>
            <option value="budget">Budget Analysis</option>
          </select>
        </div>
      </div>

      {/* Key Financial Metrics */}
      <div className="financial-metrics">
        <div className="metric-card revenue">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.summary.totalRevenue)}</div>
            <div className="metric-label">Total Revenue</div>
            <div className="metric-trend">
              <span className="trend-icon">📈</span>
              <span className="trend-value">+{data.trends?.revenue?.growth || 0}%</span>
            </div>
          </div>
        </div>
        <div className="metric-card profit">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.summary.netProfit)}</div>
            <div className="metric-label">Net Profit</div>
            <div className="metric-trend">
              <span className="trend-icon">📈</span>
              <span className="trend-value">{formatPercentage(data.summary.netMargin)}</span>
            </div>
          </div>
        </div>
        <div className="metric-card cash">
          <div className="metric-icon">🏦</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.summary.cashOnHand)}</div>
            <div className="metric-label">Cash on Hand</div>
            <div className="metric-trend">
              <span className="trend-icon">⏱️</span>
              <span className="trend-value">{data.summary.runway} mo runway</span>
            </div>
          </div>
        </div>
        <div className="metric-card margin">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-value">{formatPercentage(data.summary.grossMargin)}</div>
            <div className="metric-label">Gross Margin</div>
            <div className="metric-trend">
              <span className="trend-icon">📊</span>
              <span className="trend-value">EBITDA {formatPercentage(data.summary.ebitda / data.summary.totalRevenue * 100)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Overview View */}
      {viewMode === 'overview' && (
        <div className="overview-view">
          <div className="overview-grid">
            {/* Revenue Breakdown */}
            <div className="overview-section revenue-breakdown">
              <h3>Revenue Breakdown</h3>
              <div className="breakdown-chart">
                {data.revenue.byProduct?.map((product, index) => (
                  <div key={index} className="breakdown-item">
                    <div className="item-header">
                      <span className="item-name">{product.name}</span>
                      <span className="item-percentage">{formatPercentage(product.percentage)}</span>
                    </div>
                    <div className="item-bar">
                      <div 
                        className="item-fill"
                        style={{ width: `${product.percentage}%` }}
                      ></div>
                    </div>
                    <div className="item-details">
                      <span className="item-amount">{formatCurrency(product.revenue)}</span>
                      <span className={`item-growth ${product.growth >= 0 ? 'positive' : 'negative'}`}>
                        {product.growth >= 0 ? '+' : ''}{formatPercentage(product.growth)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Expense Categories */}
            <div className="overview-section expense-breakdown">
              <h3>Expense Categories</h3>
              <div className="breakdown-chart">
                {data.expenses.byCategory?.map((category, index) => (
                  <div key={index} className="breakdown-item">
                    <div className="item-header">
                      <span className="item-name">{category.name}</span>
                      <span className="item-percentage">{formatPercentage(category.percentage)}</span>
                    </div>
                    <div className="item-bar">
                      <div 
                        className="item-fill expense"
                        style={{ width: `${category.percentage}%` }}
                      ></div>
                    </div>
                    <div className="item-details">
                      <span className="item-amount">{formatCurrency(category.amount)}</span>
                      <span 
                        className={`item-variance ${category.variance <= 0 ? 'positive' : 'negative'}`}
                        style={{ color: getVarianceColor(category.variance) }}
                      >
                        {category.variance >= 0 ? '+' : ''}{formatPercentage(category.variance)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Profitability Trends */}
            <div className="overview-section profitability-trends">
              <h3>Profitability Trends</h3>
              <div className="trends-chart">
                <div className="trends-grid">
                  <div className="trend-metric">
                    <div className="trend-label">Gross Margin</div>
                    <div className="trend-value">{formatPercentage(data.profitability.margins.gross)}</div>
                    <div className="trend-comparison">
                      vs Industry: {formatPercentage(data.profitability.benchmarks.industry.gross)}
                    </div>
                  </div>
                  <div className="trend-metric">
                    <div className="trend-label">Operating Margin</div>
                    <div className="trend-value">{formatPercentage(data.profitability.margins.operating)}</div>
                    <div className="trend-comparison">
                      vs Industry: {formatPercentage(data.profitability.benchmarks.industry.operating)}
                    </div>
                  </div>
                  <div className="trend-metric">
                    <div className="trend-label">Net Margin</div>
                    <div className="trend-value">{formatPercentage(data.profitability.margins.net)}</div>
                    <div className="trend-comparison">
                      vs Industry: {formatPercentage(data.profitability.benchmarks.industry.net)}
                    </div>
                  </div>
                  <div className="trend-metric">
                    <div className="trend-label">EBITDA Margin</div>
                    <div className="trend-value">{formatPercentage(data.profitability.margins.ebitda)}</div>
                    <div className="trend-comparison">
                      Strong Performance
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Key Performance Indicators */}
            <div className="overview-section kpi-grid">
              <h3>Key Performance Indicators</h3>
              <div className="kpi-categories">
                <div className="kpi-category">
                  <h4>Financial KPIs</h4>
                  <div className="kpi-items">
                    <div className="kpi-item">
                      <span className="kpi-label">ROA</span>
                      <span className="kpi-value">{formatPercentage(data.kpis.financial?.roa || 0)}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">ROE</span>
                      <span className="kpi-value">{formatPercentage(data.kpis.financial?.roe || 0)}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">Current Ratio</span>
                      <span className="kpi-value">{data.kpis.financial?.currentRatio || 0}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">Debt/Equity</span>
                      <span className="kpi-value">{data.kpis.financial?.debtToEquity || 0}</span>
                    </div>
                  </div>
                </div>
                <div className="kpi-category">
                  <h4>Operational KPIs</h4>
                  <div className="kpi-items">
                    <div className="kpi-item">
                      <span className="kpi-label">Revenue/Employee</span>
                      <span className="kpi-value">{formatCurrency(data.kpis.operational?.revenuePerEmployee || 0)}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">CAC</span>
                      <span className="kpi-value">{formatCurrency(data.kpis.operational?.customerAcquisitionCost || 0)}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">LTV</span>
                      <span className="kpi-value">{formatCurrency(data.kpis.operational?.lifetimeValue || 0)}</span>
                    </div>
                    <div className="kpi-item">
                      <span className="kpi-label">Churn Rate</span>
                      <span className="kpi-value">{formatPercentage(data.kpis.operational?.churnRate || 0)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Cash Flow View */}
      {viewMode === 'cash_flow' && (
        <div className="cash-flow-view">
          <div className="cash-flow-grid">
            {/* Cash Flow Summary */}
            <div className="cash-flow-section summary">
              <h3>Cash Flow Summary</h3>
              <div className="cash-flow-items">
                <div className="cash-flow-item operating">
                  <div className="item-label">Operating Cash Flow</div>
                  <div className="item-value positive">{formatCurrency(data.cashFlow.operating)}</div>
                </div>
                <div className="cash-flow-item investing">
                  <div className="item-label">Investing Cash Flow</div>
                  <div className="item-value negative">{formatCurrency(data.cashFlow.investing)}</div>
                </div>
                <div className="cash-flow-item financing">
                  <div className="item-label">Financing Cash Flow</div>
                  <div className="item-value positive">{formatCurrency(data.cashFlow.financing)}</div>
                </div>
                <div className="cash-flow-item net">
                  <div className="item-label">Net Cash Change</div>
                  <div className="item-value positive">{formatCurrency(data.cashFlow.netChange)}</div>
                </div>
              </div>
            </div>

            {/* Monthly Cash Flow */}
            <div className="cash-flow-section monthly">
              <h3>Monthly Cash Flow Trend</h3>
              <div className="monthly-chart">
                {data.cashFlow.monthly?.map((month, index) => (
                  <div key={index} className="monthly-item">
                    <div className="month-label">{month.month}</div>
                    <div className="cash-flow-bars">
                      <div className="bar-item operating">
                        <div className="bar-label">Operating</div>
                        <div className="bar-value">{formatCurrency(month.operating)}</div>
                      </div>
                      <div className="bar-item net">
                        <div className="bar-label">Net</div>
                        <div className={`bar-value ${month.net >= 0 ? 'positive' : 'negative'}`}>
                          {formatCurrency(month.net)}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Cash Position */}
            <div className="cash-flow-section position">
              <h3>Cash Position</h3>
              <div className="position-metrics">
                <div className="position-item">
                  <div className="position-label">Beginning Cash</div>
                  <div className="position-value">{formatCurrency(data.cashFlow.beginning)}</div>
                </div>
                <div className="position-item">
                  <div className="position-label">Net Change</div>
                  <div className="position-value positive">{formatCurrency(data.cashFlow.netChange)}</div>
                </div>
                <div className="position-item">
                  <div className="position-label">Ending Cash</div>
                  <div className="position-value">{formatCurrency(data.cashFlow.ending)}</div>
                </div>
                <div className="position-item">
                  <div className="position-label">Monthly Burn</div>
                  <div className="position-value">{formatCurrency(data.summary.burnRate)}</div>
                </div>
                <div className="position-item highlight">
                  <div className="position-label">Runway</div>
                  <div className="position-value">{data.summary.runway} months</div>
                </div>
              </div>
            </div>

            {/* Cash Flow Projections */}
            <div className="cash-flow-section projections">
              <h3>Cash Flow Projections</h3>
              <div className="projection-items">
                <div className="projection-item">
                  <div className="projection-period">Next Month</div>
                  <div className="projection-value">{formatCurrency(data.cashFlow.projections.nextMonth)}</div>
                </div>
                <div className="projection-item">
                  <div className="projection-period">Next Quarter</div>
                  <div className="projection-value">{formatCurrency(data.cashFlow.projections.nextQuarter)}</div>
                </div>
                <div className="projection-item">
                  <div className="projection-period">Break-even Point</div>
                  <div className="projection-value">Q4 2024</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Profitability View */}
      {viewMode === 'profitability' && (
        <div className="profitability-view">
          <div className="profitability-grid">
            {/* Margin Analysis */}
            <div className="profitability-section margins">
              <h3>Margin Analysis</h3>
              <div className="margin-metrics">
                {Object.entries(data.profitability.margins).map(([key, value]) => (
                  <div key={key} className="margin-item">
                    <div className="margin-label">
                      {key.charAt(0).toUpperCase() + key.slice(1)} Margin
                    </div>
                    <div className="margin-value">{formatPercentage(value)}</div>
                    <div className="margin-bar">
                      <div 
                        className="margin-fill"
                        style={{ width: `${Math.min(value, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Profitability Drivers */}
            <div className="profitability-section drivers">
              <h3>Profitability Drivers</h3>
              <div className="driver-items">
                {data.profitability.drivers?.map((driver, index) => (
                  <div key={index} className="driver-item">
                    <div className="driver-header">
                      <span className="driver-name">{driver.factor}</span>
                      <span className="driver-trend">{getTrendIcon(driver.trend)}</span>
                    </div>
                    <div className="driver-impact">
                      <span className={`impact-value ${driver.impact >= 0 ? 'positive' : 'negative'}`}>
                        {driver.impact >= 0 ? '+' : ''}{formatPercentage(driver.impact)}
                      </span>
                      <span className="impact-label">impact</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Benchmark Comparison */}
            <div className="profitability-section benchmarks">
              <h3>Industry Benchmarks</h3>
              <div className="benchmark-comparison">
                <div className="benchmark-item">
                  <div className="benchmark-metric">Gross Margin</div>
                  <div className="benchmark-values">
                    <div className="value-item our">
                      <span className="value-label">Our Company</span>
                      <span className="value-amount">{formatPercentage(data.profitability.margins.gross)}</span>
                    </div>
                    <div className="value-item industry">
                      <span className="value-label">Industry Avg</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.industry.gross)}</span>
                    </div>
                    <div className="value-item competition">
                      <span className="value-label">Competition</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.competition.gross)}</span>
                    </div>
                  </div>
                </div>
                <div className="benchmark-item">
                  <div className="benchmark-metric">Operating Margin</div>
                  <div className="benchmark-values">
                    <div className="value-item our">
                      <span className="value-label">Our Company</span>
                      <span className="value-amount">{formatPercentage(data.profitability.margins.operating)}</span>
                    </div>
                    <div className="value-item industry">
                      <span className="value-label">Industry Avg</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.industry.operating)}</span>
                    </div>
                    <div className="value-item competition">
                      <span className="value-label">Competition</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.competition.operating)}</span>
                    </div>
                  </div>
                </div>
                <div className="benchmark-item">
                  <div className="benchmark-metric">Net Margin</div>
                  <div className="benchmark-values">
                    <div className="value-item our">
                      <span className="value-label">Our Company</span>
                      <span className="value-amount">{formatPercentage(data.profitability.margins.net)}</span>
                    </div>
                    <div className="value-item industry">
                      <span className="value-label">Industry Avg</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.industry.net)}</span>
                    </div>
                    <div className="value-item competition">
                      <span className="value-label">Competition</span>
                      <span className="value-amount">{formatPercentage(data.profitability.benchmarks.competition.net)}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Margin Trends */}
            <div className="profitability-section trends">
              <h3>Margin Trends</h3>
              <div className="trend-chart">
                {data.profitability.trends?.map((period, index) => (
                  <div key={index} className="trend-period">
                    <div className="period-label">{period.period}</div>
                    <div className="period-margins">
                      <div className="margin-trend gross">
                        <span className="trend-label">Gross</span>
                        <span className="trend-value">{formatPercentage(period.gross)}</span>
                      </div>
                      <div className="margin-trend operating">
                        <span className="trend-label">Operating</span>
                        <span className="trend-value">{formatPercentage(period.operating)}</span>
                      </div>
                      <div className="margin-trend net">
                        <span className="trend-label">Net</span>
                        <span className="trend-value">{formatPercentage(period.net)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Budget Analysis View */}
      {viewMode === 'budget' && (
        <div className="budget-view">
          <div className="budget-grid">
            {/* Annual Budget Overview */}
            <div className="budget-section annual">
              <h3>Annual Budget Overview</h3>
              <div className="annual-items">
                <div className="annual-item revenue">
                  <div className="annual-header">
                    <span className="annual-label">Revenue</span>
                    <span className="annual-status">{formatPercentage(data.budget.annual.revenue.ytd)} YTD</span>
                  </div>
                  <div className="annual-figures">
                    <div className="figure budgeted">
                      <span className="figure-label">Budgeted</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.revenue.budgeted)}</span>
                    </div>
                    <div className="figure actual">
                      <span className="figure-label">Actual</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.revenue.actual)}</span>
                    </div>
                    <div className={`figure variance ${data.budget.annual.revenue.variance >= 0 ? 'positive' : 'negative'}`}>
                      <span className="figure-label">Variance</span>
                      <span className="figure-value">
                        {data.budget.annual.revenue.variance >= 0 ? '+' : ''}{formatPercentage(data.budget.annual.revenue.variance)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="annual-item expenses">
                  <div className="annual-header">
                    <span className="annual-label">Expenses</span>
                    <span className="annual-status">{formatPercentage(data.budget.annual.expenses.ytd)} YTD</span>
                  </div>
                  <div className="annual-figures">
                    <div className="figure budgeted">
                      <span className="figure-label">Budgeted</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.expenses.budgeted)}</span>
                    </div>
                    <div className="figure actual">
                      <span className="figure-label">Actual</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.expenses.actual)}</span>
                    </div>
                    <div className={`figure variance ${data.budget.annual.expenses.variance <= 0 ? 'positive' : 'negative'}`}>
                      <span className="figure-label">Variance</span>
                      <span className="figure-value">
                        {data.budget.annual.expenses.variance >= 0 ? '+' : ''}{formatPercentage(data.budget.annual.expenses.variance)}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="annual-item profit">
                  <div className="annual-header">
                    <span className="annual-label">Net Profit</span>
                    <span className="annual-status">{formatPercentage(data.budget.annual.profit.ytd)} YTD</span>
                  </div>
                  <div className="annual-figures">
                    <div className="figure budgeted">
                      <span className="figure-label">Budgeted</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.profit.budgeted)}</span>
                    </div>
                    <div className="figure actual">
                      <span className="figure-label">Actual</span>
                      <span className="figure-value">{formatCurrency(data.budget.annual.profit.actual)}</span>
                    </div>
                    <div className={`figure variance ${data.budget.annual.profit.variance >= 0 ? 'positive' : 'negative'}`}>
                      <span className="figure-label">Variance</span>
                      <span className="figure-value">
                        {data.budget.annual.profit.variance >= 0 ? '+' : ''}{formatPercentage(data.budget.annual.profit.variance)}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Quarterly Budget */}
            <div className="budget-section quarterly">
              <h3>Quarterly Budget Progress</h3>
              <div className="quarterly-chart">
                {Object.entries(data.budget.quarterly).map(([quarter, data]) => (
                  <div key={quarter} className={`quarterly-item ${data.status}`}>
                    <div className="quarter-header">
                      <span className="quarter-label">{quarter.toUpperCase()}</span>
                      <span className={`quarter-status ${data.status}`}>
                        {data.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="quarter-metrics">
                      <div className="quarter-metric revenue">
                        <span className="metric-label">Revenue</span>
                        <span className="metric-value">{formatCurrency(data.revenue)}</span>
                      </div>
                      <div className="quarter-metric expenses">
                        <span className="metric-label">Expenses</span>
                        <span className="metric-value">{formatCurrency(data.expenses)}</span>
                      </div>
                      <div className={`quarter-metric profit ${data.profit >= 0 ? 'positive' : 'negative'}`}>
                        <span className="metric-label">Profit</span>
                        <span className="metric-value">{formatCurrency(data.profit)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Department Budget Utilization */}
            <div className="budget-section departments">
              <h3>Department Budget Utilization</h3>
              <div className="department-budget">
                {data.budget.departments?.map((dept, index) => (
                  <div key={index} className="department-item">
                    <div className="department-header">
                      <span className="department-name">{dept.name}</span>
                      <span className="department-utilized">{formatPercentage(dept.utilized)} utilized</span>
                    </div>
                    <div className="department-figures">
                      <div className="budget-figure">
                        <span className="figure-label">Budgeted</span>
                        <span className="figure-value">{formatCurrency(dept.budgeted)}</span>
                      </div>
                      <div className="actual-figure">
                        <span className="figure-label">Actual</span>
                        <span className="figure-value">{formatCurrency(dept.actual)}</span>
                      </div>
                      <div className={`variance-figure ${dept.variance <= 0 ? 'positive' : 'negative'}`}>
                        <span className="figure-label">Variance</span>
                        <span className="figure-value">
                          {dept.variance >= 0 ? '+' : ''}{formatPercentage(dept.variance)}
                        </span>
                      </div>
                    </div>
                    <div className="department-bar">
                      <div 
                        className="department-fill"
                        style={{ 
                          width: `${dept.utilized}%`,
                          backgroundColor: dept.utilized > 90 ? '#ef4444' : 
                                          dept.utilized > 75 ? '#f59e0b' : '#10b981'
                        }}
                      ></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Metric Details Modal */}
      {selectedMetric && (
        <div className="metric-details-modal">
          <div className="modal-overlay" onClick={() => setSelectedMetric(null)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <h2>Financial Metric Details</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedMetric(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="metric-details">
                {/* Metric details content would go here */}
                <p>Detailed metric analysis and historical trends</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialMetricsDashboard;
