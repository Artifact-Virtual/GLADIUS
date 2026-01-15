import React, { useState, useEffect } from 'react';

/**
 * FinancialMetricsPanel - Financial KPIs and Metrics Display
 * 
 * Displays key financial metrics including:
 * - Revenue metrics
 * - Expense tracking
 * - Profit margins
 * - Cash flow
 * - Financial forecasting
 */
const FinancialMetricsPanel = ({ 
  className = '', 
  onMetricClick = () => {},
  refreshInterval = 30000 
}) => {
  const [financialData, setFinancialData] = useState({
    totalRevenue: 0,
    monthlyRevenue: 0,
    totalExpenses: 0,
    netProfit: 0,
    cashFlow: 0,
    profitMargin: 0,
    loading: true
  });

  useEffect(() => {
    const fetchFinancialData = async () => {
      try {
        const response = await fetch('/api/financial-metrics');
        if (response.ok) {
          const data = await response.json();
          setFinancialData({ ...data, loading: false });
        }
      } catch (error) {
        console.error('Error fetching financial data:', error);
        setFinancialData(prev => ({ ...prev, loading: false }));
      }
    };

    fetchFinancialData();
    const interval = setInterval(fetchFinancialData, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  if (financialData.loading) {
    return (
      <div className={`financial-metrics-panel loading ${className}`}>
        <div className="panel-header">
          <h3>Financial Metrics</h3>
          <div className="loading-spinner"></div>
        </div>
        <div className="loading-content">Loading financial data...</div>
      </div>
    );
  }

  return (
    <div className={`financial-metrics-panel ${className}`}>
      <div className="panel-header">
        <h3>Financial Metrics</h3>
        <div className="last-updated">
          Updated: {new Date().toLocaleTimeString()}
        </div>
      </div>

      <div className="metrics-grid">
        <div 
          className="metric-card revenue-card"
          onClick={() => onMetricClick('revenue')}
        >
          <div className="metric-label">Total Revenue</div>
          <div className="metric-value">{formatCurrency(financialData.totalRevenue)}</div>
          <div className="metric-change positive">
            +{formatCurrency(financialData.monthlyRevenue)} this month
          </div>
        </div>

        <div 
          className="metric-card expenses-card"
          onClick={() => onMetricClick('expenses')}
        >
          <div className="metric-label">Total Expenses</div>
          <div className="metric-value">{formatCurrency(financialData.totalExpenses)}</div>
          <div className="metric-trend">
            <span className="trend-indicator">📊</span>
            Operational costs
          </div>
        </div>

        <div 
          className="metric-card profit-card"
          onClick={() => onMetricClick('profit')}
        >
          <div className="metric-label">Net Profit</div>
          <div className="metric-value">{formatCurrency(financialData.netProfit)}</div>
          <div className="metric-margin">
            Margin: {formatPercentage(financialData.profitMargin)}
          </div>
        </div>

        <div 
          className="metric-card cashflow-card"
          onClick={() => onMetricClick('cashflow')}
        >
          <div className="metric-label">Cash Flow</div>
          <div className="metric-value">{formatCurrency(financialData.cashFlow)}</div>
          <div className={`metric-status ${financialData.cashFlow >= 0 ? 'positive' : 'negative'}`}>
            {financialData.cashFlow >= 0 ? 'Positive' : 'Negative'}
          </div>
        </div>
      </div>

      <div className="financial-summary">
        <div className="summary-item">
          <span className="summary-label">ROI:</span>
          <span className="summary-value">
            {formatPercentage(financialData.netProfit / Math.max(financialData.totalExpenses, 1))}
          </span>
        </div>
        <div className="summary-item">
          <span className="summary-label">Burn Rate:</span>
          <span className="summary-value">
            {formatCurrency(financialData.totalExpenses / 12)}/month
          </span>
        </div>
      </div>
    </div>
  );
};

export default FinancialMetricsPanel;
