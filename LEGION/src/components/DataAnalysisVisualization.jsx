import React, { useState, useEffect, useCallback } from 'react';

const DataAnalysisVisualization = () => {
  const [activeView, setActiveView] = useState('dashboard');
  const [analyses, setAnalyses] = useState([]);
  const [visualizations, setVisualizations] = useState([]);
  const [datasets, setDatasets] = useState([]);
  const [reports, setReports] = useState([]);
  const [models, setModels] = useState([]);
  const [experiments, setExperiments] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);
  const [selectedVisualization, setSelectedVisualization] = useState(null);
  const [analysisFilters, setAnalysisFilters] = useState({
    type: 'all',
    status: 'all',
    complexity: 'all',
    department: 'all',
    timeframe: 'all',
    accuracy: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('created');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [analysisModal, setAnalysisModal] = useState(false);
  const [visualizationModal, setVisualizationModal] = useState(false);
  const [newAnalysisModal, setNewAnalysisModal] = useState(false);
  const [exportModal, setExportModal] = useState(false);
  const [compareModal, setCompareModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  // Mock data generators
  const generateAnalyses = useCallback(() => {
    const analysisTypes = ['statistical', 'predictive', 'descriptive', 'prescriptive', 'diagnostic', 'exploratory'];
    const statuses = ['completed', 'running', 'queued', 'failed', 'cancelled'];
    const complexities = ['low', 'medium', 'high', 'very-high'];
    const departments = ['marketing', 'sales', 'finance', 'operations', 'hr', 'research'];
    const accuracies = ['excellent', 'good', 'fair', 'poor'];
    
    const analysisTitles = [
      'Customer Behavior Analysis', 'Sales Forecasting Model', 'Market Trend Prediction', 'Revenue Optimization Study',
      'Customer Churn Analysis', 'Product Performance Review', 'Competitive Analysis', 'Risk Assessment Model',
      'Operational Efficiency Study', 'Customer Segmentation Analysis', 'Price Sensitivity Analysis', 'Demand Forecasting',
      'A/B Test Results Analysis', 'Customer Lifetime Value', 'Market Share Analysis', 'Brand Sentiment Analysis',
      'Supply Chain Optimization', 'Financial Performance Analysis', 'Employee Satisfaction Study', 'Process Improvement Analysis'
    ];

    return Array.from({ length: 16 }, (_, index) => ({
      id: `analysis-${index + 1}`,
      title: analysisTitles[index] || `Analysis ${index + 1}`,
      type: analysisTypes[Math.floor(Math.random() * analysisTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      complexity: complexities[Math.floor(Math.random() * complexities.length)],
      department: departments[Math.floor(Math.random() * departments.length)],
      accuracy: accuracies[Math.floor(Math.random() * accuracies.length)],
      progress: Math.floor(Math.random() * 100),
      duration: `${Math.floor(Math.random() * 120) + 30} minutes`,
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      completedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      dataPoints: Math.floor(Math.random() * 1000000) + 10000,
      features: Math.floor(Math.random() * 50) + 5,
      algorithms: Math.floor(Math.random() * 5) + 1,
      confidence: Math.floor(Math.random() * 30) + 70,
      rSquared: (Math.random() * 0.4 + 0.6).toFixed(3),
      mape: (Math.random() * 10 + 2).toFixed(2),
      rmse: (Math.random() * 100 + 50).toFixed(2),
      author: ['Dr. Sarah Chen', 'Michael Rodriguez', 'Emma Thompson', 'David Kim'][Math.floor(Math.random() * 4)],
      description: `Comprehensive ${analysisTypes[Math.floor(Math.random() * analysisTypes.length)]} analysis providing actionable insights for business decision-making and strategic planning.`,
      keyFindings: [
        `${Math.floor(Math.random() * 30) + 15}% improvement in key metrics identified`,
        `${Math.floor(Math.random() * 25) + 10} significant patterns discovered`,
        `${Math.floor(Math.random() * 40) + 60}% prediction accuracy achieved`,
        `$${(Math.random() * 500 + 100).toFixed(0)}K potential business impact`
      ],
      visualizations: Math.floor(Math.random() * 8) + 3,
      datasets: Math.floor(Math.random() * 5) + 1,
      models: Math.floor(Math.random() * 3) + 1,
      exports: Math.floor(Math.random() * 10) + 2,
      views: Math.floor(Math.random() * 500) + 50,
      tags: ['data-science', 'machine-learning', 'business-intelligence', 'predictive', 'statistical'].slice(0, Math.floor(Math.random() * 3) + 2),
      priority: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)],
      computeTime: Math.floor(Math.random() * 3600) + 300,
      memoryUsage: (Math.random() * 8 + 2).toFixed(1) + ' GB',
      cpuUsage: Math.floor(Math.random() * 80) + 20
    }));
  }, []);

  const generateVisualizations = useCallback(() => {
    const vizTypes = ['line-chart', 'bar-chart', 'scatter-plot', 'heatmap', 'pie-chart', 'histogram', 'box-plot', 'correlation-matrix'];
    const formats = ['interactive', 'static', 'animated', 'real-time'];
    const themes = ['light', 'dark', 'corporate', 'colorful'];
    
    const vizTitles = [
      'Revenue Trend Analysis', 'Customer Segmentation Plot', 'Sales Performance Dashboard', 'Market Share Distribution',
      'Customer Behavior Heatmap', 'Product Performance Chart', 'Seasonal Trends Analysis', 'Geographic Distribution',
      'Conversion Funnel Analysis', 'Cohort Analysis Chart', 'A/B Test Results', 'Correlation Matrix',
      'Predictive Model Output', 'Risk Distribution Analysis', 'Performance Benchmarks', 'Time Series Forecasting'
    ];

    return Array.from({ length: 12 }, (_, index) => ({
      id: `viz-${index + 1}`,
      title: vizTitles[index] || `Visualization ${index + 1}`,
      type: vizTypes[Math.floor(Math.random() * vizTypes.length)],
      format: formats[Math.floor(Math.random() * formats.length)],
      theme: themes[Math.floor(Math.random() * themes.length)],
      width: Math.floor(Math.random() * 800) + 400,
      height: Math.floor(Math.random() * 600) + 300,
      dataPoints: Math.floor(Math.random() * 10000) + 100,
      series: Math.floor(Math.random() * 8) + 1,
      createdAt: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      views: Math.floor(Math.random() * 200) + 20,
      downloads: Math.floor(Math.random() * 50) + 5,
      shares: Math.floor(Math.random() * 15) + 2,
      rating: (Math.random() * 2 + 3).toFixed(1),
      analysisId: `analysis-${Math.floor(Math.random() * 16) + 1}`,
      description: `Interactive ${vizTypes[Math.floor(Math.random() * vizTypes.length)]} visualization providing clear insights into business data and trends.`,
      insights: [
        `Clear trend identification with ${Math.floor(Math.random() * 95) + 85}% pattern recognition`,
        `${Math.floor(Math.random() * 5) + 3} key anomalies highlighted`,
        `Seasonal patterns detected with ${Math.floor(Math.random() * 30) + 70}% confidence`,
        `${Math.floor(Math.random() * 8) + 2} actionable recommendations generated`
      ],
      config: {
        responsive: true,
        interactive: Math.random() > 0.3,
        exportable: Math.random() > 0.2,
        realTime: Math.random() > 0.7
      },
      performance: {
        loadTime: (Math.random() * 2 + 0.5).toFixed(2) + 's',
        renderTime: (Math.random() * 500 + 100).toFixed(0) + 'ms',
        memoryUsage: (Math.random() * 50 + 20).toFixed(1) + 'MB'
      }
    }));
  }, []);

  const generateDatasets = useCallback(() => {
    const dataTypes = ['structured', 'unstructured', 'time-series', 'geospatial', 'text', 'image'];
    const sources = ['database', 'api', 'file-upload', 'streaming', 'web-scraping', 'survey'];
    const qualities = ['excellent', 'good', 'fair', 'poor'];
    
    const datasetNames = [
      'Customer Transaction Data', 'Product Catalog Information', 'Marketing Campaign Results', 'Website Analytics Data',
      'Sales Performance Metrics', 'Customer Feedback Surveys', 'Market Research Data', 'Financial Records',
      'Social Media Interactions', 'Support Ticket Data', 'Inventory Management Data', 'Employee Performance Data'
    ];

    return Array.from({ length: 10 }, (_, index) => ({
      id: `dataset-${index + 1}`,
      name: datasetNames[index] || `Dataset ${index + 1}`,
      type: dataTypes[Math.floor(Math.random() * dataTypes.length)],
      source: sources[Math.floor(Math.random() * sources.length)],
      quality: qualities[Math.floor(Math.random() * qualities.length)],
      size: (Math.random() * 1000 + 10).toFixed(1) + ' MB',
      records: Math.floor(Math.random() * 1000000) + 1000,
      columns: Math.floor(Math.random() * 50) + 10,
      completeness: Math.floor(Math.random() * 20) + 80,
      accuracy: Math.floor(Math.random() * 25) + 75,
      timeliness: Math.floor(Math.random() * 30) + 70,
      createdAt: new Date(Date.now() - Math.random() * 120 * 24 * 60 * 60 * 1000).toISOString(),
      lastUpdated: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      usageCount: Math.floor(Math.random() * 100) + 10,
      description: `Comprehensive ${dataTypes[Math.floor(Math.random() * dataTypes.length)]} dataset containing valuable business information for analysis and insights.`,
      schema: {
        primaryKey: Math.random() > 0.7,
        foreignKeys: Math.floor(Math.random() * 5),
        indexes: Math.floor(Math.random() * 8) + 2,
        nullValues: Math.floor(Math.random() * 15) + 2
      },
      metadata: {
        owner: ['Data Team', 'Analytics Team', 'Business Intelligence'][Math.floor(Math.random() * 3)],
        category: ['customer', 'product', 'financial', 'operational'][Math.floor(Math.random() * 4)],
        tags: ['current', 'historical', 'real-time', 'validated'].slice(0, Math.floor(Math.random() * 3) + 1)
      }
    }));
  }, []);

  const generateReports = useCallback(() => {
    const reportTypes = ['executive-summary', 'detailed-analysis', 'technical-report', 'dashboard-export', 'presentation'];
    const formats = ['pdf', 'html', 'excel', 'powerpoint', 'json'];
    
    const reportTitles = [
      'Q4 2024 Analytics Summary', 'Customer Behavior Insights Report', 'Sales Performance Analysis',
      'Market Trends Executive Brief', 'Predictive Model Results', 'Risk Assessment Report',
      'Operational Efficiency Analysis', 'Customer Segmentation Study', 'Revenue Optimization Report'
    ];

    return Array.from({ length: 9 }, (_, index) => ({
      id: `report-${index + 1}`,
      title: reportTitles[index] || `Report ${index + 1}`,
      type: reportTypes[Math.floor(Math.random() * reportTypes.length)],
      format: formats[Math.floor(Math.random() * formats.length)],
      size: (Math.random() * 20 + 1).toFixed(1) + ' MB',
      pages: Math.floor(Math.random() * 100) + 10,
      generatedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      downloads: Math.floor(Math.random() * 50) + 5,
      views: Math.floor(Math.random() * 200) + 20,
      author: 'Analytics Engine',
      analysisId: `analysis-${Math.floor(Math.random() * 16) + 1}`,
      description: `Comprehensive ${reportTypes[Math.floor(Math.random() * reportTypes.length)]} containing detailed insights and recommendations.`,
      sections: Math.floor(Math.random() * 8) + 4,
      charts: Math.floor(Math.random() * 15) + 5,
      tables: Math.floor(Math.random() * 10) + 3,
      status: ['ready', 'generating', 'error'][Math.floor(Math.random() * 3)]
    }));
  }, []);

  const generateModels = useCallback(() => {
    const modelTypes = ['linear-regression', 'random-forest', 'neural-network', 'svm', 'clustering', 'time-series'];
    const algorithms = ['sklearn', 'tensorflow', 'pytorch', 'xgboost', 'statsmodels'];
    const statuses = ['trained', 'training', 'validating', 'deployed', 'failed'];
    
    const modelNames = [
      'Customer Churn Predictor', 'Sales Forecasting Model', 'Price Optimization Engine', 'Demand Prediction Model',
      'Fraud Detection System', 'Recommendation Engine', 'Sentiment Analysis Model', 'Risk Assessment Model'
    ];

    return Array.from({ length: 8 }, (_, index) => ({
      id: `model-${index + 1}`,
      name: modelNames[index] || `Model ${index + 1}`,
      type: modelTypes[Math.floor(Math.random() * modelTypes.length)],
      algorithm: algorithms[Math.floor(Math.random() * algorithms.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
      accuracy: (Math.random() * 0.3 + 0.7).toFixed(3),
      precision: (Math.random() * 0.3 + 0.7).toFixed(3),
      recall: (Math.random() * 0.3 + 0.7).toFixed(3),
      f1Score: (Math.random() * 0.3 + 0.7).toFixed(3),
      trainedAt: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString(),
      trainingTime: `${Math.floor(Math.random() * 180) + 30} minutes`,
      datasetSize: Math.floor(Math.random() * 500000) + 10000,
      features: Math.floor(Math.random() * 30) + 10,
      parameters: Math.floor(Math.random() * 1000000) + 10000,
      deployments: Math.floor(Math.random() * 5) + 1,
      predictions: Math.floor(Math.random() * 10000) + 100,
      description: `Advanced ${modelTypes[Math.floor(Math.random() * modelTypes.length)]} model for accurate business predictions and insights.`,
      hyperparameters: {
        learningRate: (Math.random() * 0.01 + 0.001).toFixed(4),
        epochs: Math.floor(Math.random() * 500) + 100,
        batchSize: [32, 64, 128, 256][Math.floor(Math.random() * 4)],
        regularization: (Math.random() * 0.1 + 0.01).toFixed(3)
      }
    }));
  }, []);

  const generateExperiments = useCallback(() => {
    const experimentTypes = ['a-b-test', 'multivariate', 'holdout', 'cross-validation', 'time-split'];
    const objectives = ['conversion', 'revenue', 'engagement', 'retention', 'satisfaction'];
    
    const experimentNames = [
      'Email Campaign Optimization', 'Landing Page A/B Test', 'Pricing Strategy Test', 'Feature Release Experiment',
      'User Interface Optimization', 'Product Recommendation Test', 'Onboarding Flow Experiment'
    ];

    return Array.from({ length: 7 }, (_, index) => ({
      id: `experiment-${index + 1}`,
      name: experimentNames[index] || `Experiment ${index + 1}`,
      type: experimentTypes[Math.floor(Math.random() * experimentTypes.length)],
      objective: objectives[Math.floor(Math.random() * objectives.length)],
      status: ['running', 'completed', 'paused', 'draft'][Math.floor(Math.random() * 4)],
      startDate: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      endDate: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      participants: Math.floor(Math.random() * 10000) + 1000,
      variants: Math.floor(Math.random() * 4) + 2,
      confidence: (Math.random() * 0.4 + 0.6).toFixed(3),
      significance: Math.random() > 0.5,
      lift: (Math.random() * 20 - 10).toFixed(2) + '%',
      pValue: (Math.random() * 0.1).toFixed(4),
      description: `Statistical experiment testing ${objectives[Math.floor(Math.random() * objectives.length)]} optimization strategies.`,
      metrics: {
        primaryMetric: objectives[Math.floor(Math.random() * objectives.length)],
        secondaryMetrics: objectives.slice(0, Math.floor(Math.random() * 3) + 2)
      },
      results: {
        winner: Math.random() > 0.5 ? 'variant-a' : 'variant-b',
        improvement: (Math.random() * 25 + 5).toFixed(1) + '%',
        significance: Math.random() > 0.2
      }
    }));
  }, []);

  const generatePredictions = useCallback(() => {
    const predictionTypes = ['forecast', 'classification', 'regression', 'anomaly-detection', 'clustering'];
    const horizons = ['1-week', '1-month', '3-months', '6-months', '1-year'];
    
    const predictionNames = [
      'Revenue Forecast Q1 2025', 'Customer Churn Risk Prediction', 'Demand Forecasting Model',
      'Market Trend Prediction', 'Sales Performance Forecast', 'Customer Lifetime Value Prediction'
    ];

    return Array.from({ length: 6 }, (_, index) => ({
      id: `prediction-${index + 1}`,
      name: predictionNames[index] || `Prediction ${index + 1}`,
      type: predictionTypes[Math.floor(Math.random() * predictionTypes.length)],
      horizon: horizons[Math.floor(Math.random() * horizons.length)],
      confidence: (Math.random() * 0.3 + 0.7).toFixed(3),
      accuracy: (Math.random() * 0.25 + 0.75).toFixed(3),
      createdAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      validUntil: new Date(Date.now() + Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      predictions: Math.floor(Math.random() * 1000) + 100,
      modelId: `model-${Math.floor(Math.random() * 8) + 1}`,
      description: `AI-generated predictions providing forward-looking insights for strategic business planning.`,
      dataPoints: Math.floor(Math.random() * 10000) + 1000,
      features: Math.floor(Math.random() * 20) + 5,
      uncertaintyBounds: {
        lower: (Math.random() * 0.1 + 0.05).toFixed(3),
        upper: (Math.random() * 0.1 + 0.05).toFixed(3)
      },
      businessImpact: {
        potential: (Math.random() * 500 + 100).toFixed(0) + 'K',
        confidence: Math.floor(Math.random() * 30) + 70,
        timeframe: horizons[Math.floor(Math.random() * horizons.length)]
      }
    }));
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API calls with realistic delays
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setAnalyses(generateAnalyses());
        setVisualizations(generateVisualizations());
        setDatasets(generateDatasets());
        setReports(generateReports());
        setModels(generateModels());
        setExperiments(generateExperiments());
        setPredictions(generatePredictions());
        
      } catch (error) {
        console.error('Error loading data analysis data:', error);
        setError('Failed to load data analysis data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateAnalyses, generateVisualizations, generateDatasets, generateReports, generateModels, generateExperiments, generatePredictions]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setAnalyses(generateAnalyses());
    setVisualizations(generateVisualizations());
    setDatasets(generateDatasets());
    setReports(generateReports());
    setModels(generateModels());
    setExperiments(generateExperiments());
    setPredictions(generatePredictions());
    
    setRefreshing(false);
  };

  // Filter and search logic
  const filteredAnalyses = analyses.filter(analysis => {
    const matchesFilters = 
      (analysisFilters.type === 'all' || analysis.type === analysisFilters.type) &&
      (analysisFilters.status === 'all' || analysis.status === analysisFilters.status) &&
      (analysisFilters.complexity === 'all' || analysis.complexity === analysisFilters.complexity) &&
      (analysisFilters.department === 'all' || analysis.department === analysisFilters.department) &&
      (analysisFilters.accuracy === 'all' || analysis.accuracy === analysisFilters.accuracy);
    
    const matchesSearch = !searchQuery || 
      analysis.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      analysis.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilters && matchesSearch;
  });

  const sortData = (data) => {
    return data.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'created':
          aValue = new Date(a.createdAt);
          bValue = new Date(b.createdAt);
          break;
        case 'completed':
          aValue = new Date(a.completedAt || a.updatedAt);
          bValue = new Date(b.completedAt || b.updatedAt);
          break;
        case 'accuracy':
          aValue = parseFloat(a.accuracy || a.confidence || 0);
          bValue = parseFloat(b.accuracy || b.confidence || 0);
          break;
        case 'name':
          aValue = a.title || a.name;
          bValue = b.title || b.name;
          break;
        default:
          aValue = a.title || a.name;
          bValue = b.title || b.name;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };

  const sortedAnalyses = sortData([...filteredAnalyses]);

  const getStatusColor = (status) => {
    const colors = {
      completed: '#28a745',
      running: '#17a2b8',
      queued: '#ffc107',
      failed: '#dc3545',
      cancelled: '#6c757d',
      ready: '#28a745',
      generating: '#17a2b8',
      error: '#dc3545',
      trained: '#28a745',
      training: '#17a2b8',
      validating: '#ffc107',
      deployed: '#6f42c1',
      paused: '#fd7e14',
      draft: '#6c757d'
    };
    return colors[status] || '#666';
  };

  const getComplexityColor = (complexity) => {
    const colors = {
      low: '#28a745',
      medium: '#ffc107',
      high: '#fd7e14',
      'very-high': '#dc3545'
    };
    return colors[complexity] || '#666';
  };

  const getAccuracyColor = (accuracy) => {
    const colors = {
      excellent: '#28a745',
      good: '#17a2b8',
      fair: '#ffc107',
      poor: '#dc3545'
    };
    return colors[accuracy] || '#666';
  };

  const renderDashboardView = () => (
    <div className="dashboard-content">
      <div className="dashboard-overview">
        <div className="overview-cards">
          <div className="overview-card">
            <div className="card-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="card-content">
              <h3>{analyses.length}</h3>
              <p>Total Analyses</p>
              <span className="trend up">+{Math.floor(Math.random() * 15) + 5}% this month</span>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">
              <i className="fas fa-eye"></i>
            </div>
            <div className="card-content">
              <h3>{visualizations.length}</h3>
              <p>Visualizations</p>
              <span className="trend up">+{Math.floor(Math.random() * 20) + 8}% this week</span>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">
              <i className="fas fa-database"></i>
            </div>
            <div className="card-content">
              <h3>{datasets.length}</h3>
              <p>Active Datasets</p>
              <span className="trend stable">{Math.floor(Math.random() * 10) + 2} updated today</span>
            </div>
          </div>
          <div className="overview-card">
            <div className="card-icon">
              <i className="fas fa-brain"></i>
            </div>
            <div className="card-content">
              <h3>{models.length}</h3>
              <p>ML Models</p>
              <span className="trend up">+{Math.floor(Math.random() * 12) + 3}% accuracy</span>
            </div>
          </div>
        </div>
      </div>

      <div className="dashboard-charts">
        <div className="chart-section">
          <h3>Analysis Performance Trends</h3>
          <div className="chart-placeholder">
            <div className="chart-content">
              <i className="fas fa-chart-area"></i>
              <p>Interactive performance chart would be displayed here</p>
            </div>
          </div>
        </div>
        <div className="chart-section">
          <h3>Model Accuracy Distribution</h3>
          <div className="chart-placeholder">
            <div className="chart-content">
              <i className="fas fa-chart-pie"></i>
              <p>Model accuracy distribution chart would be displayed here</p>
            </div>
          </div>
        </div>
      </div>

      <div className="recent-activity">
        <h3>Recent Analysis Activity</h3>
        <div className="activity-list">
          {analyses.slice(0, 5).map(analysis => (
            <div key={analysis.id} className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-analytics"></i>
              </div>
              <div className="activity-content">
                <h4>{analysis.title}</h4>
                <p>{analysis.type} • {analysis.department}</p>
                <span className="activity-time">{new Date(analysis.createdAt).toLocaleDateString()}</span>
              </div>
              <div className="activity-status">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(analysis.status) }}>
                  {analysis.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderAnalysesView = () => (
    <div className="analyses-content">
      <div className="analyses-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search analyses..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="sort-controls">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="created">Sort by Created</option>
              <option value="completed">Sort by Completed</option>
              <option value="accuracy">Sort by Accuracy</option>
              <option value="name">Sort by Name</option>
            </select>
            <button 
              className="sort-order"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              <i className={`fas fa-sort-${sortOrder === 'asc' ? 'up' : 'down'}`}></i>
            </button>
          </div>
        </div>

        <div className="filter-section">
          <select value={analysisFilters.type} onChange={(e) => setAnalysisFilters({...analysisFilters, type: e.target.value})}>
            <option value="all">All Types</option>
            <option value="statistical">Statistical</option>
            <option value="predictive">Predictive</option>
            <option value="descriptive">Descriptive</option>
            <option value="prescriptive">Prescriptive</option>
            <option value="diagnostic">Diagnostic</option>
          </select>
          <select value={analysisFilters.status} onChange={(e) => setAnalysisFilters({...analysisFilters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="completed">Completed</option>
            <option value="running">Running</option>
            <option value="queued">Queued</option>
            <option value="failed">Failed</option>
          </select>
          <select value={analysisFilters.complexity} onChange={(e) => setAnalysisFilters({...analysisFilters, complexity: e.target.value})}>
            <option value="all">All Complexities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
            <option value="very-high">Very High</option>
          </select>
          <select value={analysisFilters.department} onChange={(e) => setAnalysisFilters({...analysisFilters, department: e.target.value})}>
            <option value="all">All Departments</option>
            <option value="marketing">Marketing</option>
            <option value="sales">Sales</option>
            <option value="finance">Finance</option>
            <option value="operations">Operations</option>
            <option value="hr">HR</option>
          </select>
        </div>
      </div>

      <div className="analyses-grid">
        {sortedAnalyses.map(analysis => (
          <div key={analysis.id} className="analysis-card" onClick={() => {setSelectedAnalysis(analysis); setAnalysisModal(true);}}>
            <div className="analysis-header">
              <h3>{analysis.title}</h3>
              <div className="analysis-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(analysis.status) }}>
                  {analysis.status}
                </span>
                <span className="complexity-badge" style={{ backgroundColor: getComplexityColor(analysis.complexity) }}>
                  {analysis.complexity}
                </span>
              </div>
            </div>
            <div className="analysis-meta">
              <span className="analysis-type">{analysis.type}</span>
              <span className="analysis-department">{analysis.department}</span>
            </div>
            <p className="analysis-description">{analysis.description}</p>
            <div className="analysis-metrics">
              <div className="metric">
                <span className="metric-label">Confidence:</span>
                <span className="metric-value">{analysis.confidence}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${analysis.confidence}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Progress:</span>
                <span className="metric-value">{analysis.progress}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${analysis.progress}%` }}></div>
                </div>
              </div>
            </div>
            <div className="analysis-stats">
              <div className="stat">
                <i className="fas fa-chart-line"></i>
                <span>{analysis.visualizations} charts</span>
              </div>
              <div className="stat">
                <i className="fas fa-database"></i>
                <span>{analysis.dataPoints.toLocaleString()} points</span>
              </div>
              <div className="stat">
                <i className="fas fa-eye"></i>
                <span>{analysis.views} views</span>
              </div>
            </div>
            <div className="analysis-footer">
              <div className="analysis-author">
                <span>{analysis.author}</span>
              </div>
              <div className="analysis-date">
                <span>{new Date(analysis.createdAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderVisualizationsView = () => (
    <div className="visualizations-content">
      <div className="viz-header">
        <h3>Data Visualizations</h3>
        <button className="new-viz-btn" onClick={() => setNewAnalysisModal(true)}>
          <i className="fas fa-plus"></i>
          Create Visualization
        </button>
      </div>
      <div className="viz-grid">
        {visualizations.map(viz => (
          <div key={viz.id} className="viz-card" onClick={() => {setSelectedVisualization(viz); setVisualizationModal(true);}}>
            <div className="viz-preview">
              <div className="preview-placeholder">
                <i className="fas fa-chart-bar"></i>
                <span>{viz.type}</span>
              </div>
            </div>
            <div className="viz-info">
              <h4>{viz.title}</h4>
              <div className="viz-meta">
                <span className="viz-type">{viz.type}</span>
                <span className="viz-format">{viz.format}</span>
              </div>
              <div className="viz-stats">
                <div className="stat">
                  <span className="stat-value">{viz.views}</span>
                  <span className="stat-label">Views</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{viz.downloads}</span>
                  <span className="stat-label">Downloads</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{viz.rating}</span>
                  <span className="stat-label">Rating</span>
                </div>
              </div>
              <div className="viz-details">
                <span>{viz.dataPoints.toLocaleString()} data points</span>
                <span>{viz.series} series</span>
                <span>{new Date(viz.updatedAt).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDatasetsView = () => (
    <div className="datasets-content">
      <div className="datasets-header">
        <h3>Data Sources</h3>
        <button className="upload-dataset-btn">
          <i className="fas fa-upload"></i>
          Upload Dataset
        </button>
      </div>
      <div className="datasets-grid">
        {datasets.map(dataset => (
          <div key={dataset.id} className="dataset-card">
            <div className="dataset-header">
              <h4>{dataset.name}</h4>
              <span className="dataset-type">{dataset.type}</span>
            </div>
            <div className="dataset-quality">
              <div className="quality-metrics">
                <div className="quality-metric">
                  <span className="metric-label">Completeness:</span>
                  <span className="metric-value">{dataset.completeness}%</span>
                  <div className="quality-bar">
                    <div className="quality-fill" style={{ width: `${dataset.completeness}%` }}></div>
                  </div>
                </div>
                <div className="quality-metric">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">{dataset.accuracy}%</span>
                  <div className="quality-bar">
                    <div className="quality-fill" style={{ width: `${dataset.accuracy}%` }}></div>
                  </div>
                </div>
              </div>
            </div>
            <div className="dataset-stats">
              <div className="stat">
                <span className="stat-value">{dataset.records.toLocaleString()}</span>
                <span className="stat-label">Records</span>
              </div>
              <div className="stat">
                <span className="stat-value">{dataset.columns}</span>
                <span className="stat-label">Columns</span>
              </div>
              <div className="stat">
                <span className="stat-value">{dataset.size}</span>
                <span className="stat-label">Size</span>
              </div>
            </div>
            <div className="dataset-meta">
              <span className="dataset-source">{dataset.source}</span>
              <span className="dataset-owner">{dataset.metadata.owner}</span>
              <span className="dataset-updated">{new Date(dataset.lastUpdated).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderReportsView = () => (
    <div className="reports-content">
      <div className="reports-header">
        <h3>Analysis Reports</h3>
        <button className="generate-report-btn">
          <i className="fas fa-file-alt"></i>
          Generate Report
        </button>
      </div>
      <div className="reports-grid">
        {reports.map(report => (
          <div key={report.id} className="report-card">
            <div className="report-header">
              <h4>{report.title}</h4>
              <span className="status-badge" style={{ backgroundColor: getStatusColor(report.status) }}>
                {report.status}
              </span>
            </div>
            <div className="report-meta">
              <span className="report-type">{report.type}</span>
              <span className="report-format">{report.format}</span>
              <span className="report-size">{report.size}</span>
            </div>
            <div className="report-stats">
              <div className="stat">
                <span className="stat-value">{report.pages}</span>
                <span className="stat-label">Pages</span>
              </div>
              <div className="stat">
                <span className="stat-value">{report.charts}</span>
                <span className="stat-label">Charts</span>
              </div>
              <div className="stat">
                <span className="stat-value">{report.downloads}</span>
                <span className="stat-label">Downloads</span>
              </div>
            </div>
            <div className="report-actions">
              <button className="download-btn">
                <i className="fas fa-download"></i>
                Download
              </button>
              <button className="preview-btn">
                <i className="fas fa-eye"></i>
                Preview
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderModelsView = () => (
    <div className="models-content">
      <div className="models-header">
        <h3>Machine Learning Models</h3>
        <button className="train-model-btn">
          <i className="fas fa-brain"></i>
          Train New Model
        </button>
      </div>
      <div className="models-grid">
        {models.map(model => (
          <div key={model.id} className="model-card">
            <div className="model-header">
              <h4>{model.name}</h4>
              <div className="model-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(model.status) }}>
                  {model.status}
                </span>
                <span className="version-badge">{model.version}</span>
              </div>
            </div>
            <div className="model-meta">
              <span className="model-type">{model.type}</span>
              <span className="model-algorithm">{model.algorithm}</span>
            </div>
            <div className="model-metrics">
              <div className="metric-grid">
                <div className="metric-item">
                  <span className="metric-label">Accuracy:</span>
                  <span className="metric-value">{(parseFloat(model.accuracy) * 100).toFixed(1)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Precision:</span>
                  <span className="metric-value">{(parseFloat(model.precision) * 100).toFixed(1)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">Recall:</span>
                  <span className="metric-value">{(parseFloat(model.recall) * 100).toFixed(1)}%</span>
                </div>
                <div className="metric-item">
                  <span className="metric-label">F1 Score:</span>
                  <span className="metric-value">{(parseFloat(model.f1Score) * 100).toFixed(1)}%</span>
                </div>
              </div>
            </div>
            <div className="model-stats">
              <div className="stat">
                <span className="stat-value">{model.features}</span>
                <span className="stat-label">Features</span>
              </div>
              <div className="stat">
                <span className="stat-value">{model.parameters.toLocaleString()}</span>
                <span className="stat-label">Parameters</span>
              </div>
              <div className="stat">
                <span className="stat-value">{model.predictions.toLocaleString()}</span>
                <span className="stat-label">Predictions</span>
              </div>
            </div>
            <div className="model-footer">
              <span className="model-trained">Trained: {new Date(model.trainedAt).toLocaleDateString()}</span>
              <div className="model-actions">
                <button className="deploy-btn">Deploy</button>
                <button className="evaluate-btn">Evaluate</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderExperimentsView = () => (
    <div className="experiments-content">
      <div className="experiments-header">
        <h3>Statistical Experiments</h3>
        <button className="new-experiment-btn">
          <i className="fas fa-flask"></i>
          New Experiment
        </button>
      </div>
      <div className="experiments-grid">
        {experiments.map(experiment => (
          <div key={experiment.id} className="experiment-card">
            <div className="experiment-header">
              <h4>{experiment.name}</h4>
              <span className="status-badge" style={{ backgroundColor: getStatusColor(experiment.status) }}>
                {experiment.status}
              </span>
            </div>
            <div className="experiment-meta">
              <span className="experiment-type">{experiment.type}</span>
              <span className="experiment-objective">{experiment.objective}</span>
            </div>
            <div className="experiment-progress">
              <div className="progress-info">
                <span>Confidence: {(parseFloat(experiment.confidence) * 100).toFixed(1)}%</span>
                <span className={`significance ${experiment.significance ? 'significant' : 'not-significant'}`}>
                  {experiment.significance ? 'Significant' : 'Not Significant'}
                </span>
              </div>
              <div className="lift-indicator">
                <span className="lift-label">Lift:</span>
                <span className={`lift-value ${parseFloat(experiment.lift) >= 0 ? 'positive' : 'negative'}`}>
                  {experiment.lift}
                </span>
              </div>
            </div>
            <div className="experiment-stats">
              <div className="stat">
                <span className="stat-value">{experiment.participants.toLocaleString()}</span>
                <span className="stat-label">Participants</span>
              </div>
              <div className="stat">
                <span className="stat-value">{experiment.variants}</span>
                <span className="stat-label">Variants</span>
              </div>
              <div className="stat">
                <span className="stat-value">{experiment.pValue}</span>
                <span className="stat-label">P-Value</span>
              </div>
            </div>
            <div className="experiment-timeline">
              <span>Started: {new Date(experiment.startDate).toLocaleDateString()}</span>
              <span>Ends: {new Date(experiment.endDate).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPredictionsView = () => (
    <div className="predictions-content">
      <div className="predictions-header">
        <h3>AI Predictions</h3>
        <button className="generate-predictions-btn">
          <i className="fas fa-crystal-ball"></i>
          Generate Predictions
        </button>
      </div>
      <div className="predictions-grid">
        {predictions.map(prediction => (
          <div key={prediction.id} className="prediction-card">
            <div className="prediction-header">
              <h4>{prediction.name}</h4>
              <span className="prediction-type">{prediction.type}</span>
            </div>
            <div className="prediction-confidence">
              <div className="confidence-meter">
                <span className="confidence-label">Confidence:</span>
                <span className="confidence-value">{(parseFloat(prediction.confidence) * 100).toFixed(1)}%</span>
                <div className="confidence-bar">
                  <div 
                    className="confidence-fill" 
                    style={{ width: `${parseFloat(prediction.confidence) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
            <div className="prediction-metrics">
              <div className="metric">
                <span className="metric-label">Accuracy:</span>
                <span className="metric-value">{(parseFloat(prediction.accuracy) * 100).toFixed(1)}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Horizon:</span>
                <span className="metric-value">{prediction.horizon}</span>
              </div>
            </div>
            <div className="prediction-impact">
              <div className="impact-item">
                <span className="impact-label">Business Impact:</span>
                <span className="impact-value">${prediction.businessImpact.potential}</span>
              </div>
              <div className="impact-confidence">
                <span>{prediction.businessImpact.confidence}% confidence</span>
              </div>
            </div>
            <div className="prediction-validity">
              <span>Valid until: {new Date(prediction.validUntil).toLocaleDateString()}</span>
              <span>{prediction.predictions.toLocaleString()} predictions made</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'dashboard':
        return renderDashboardView();
      case 'analyses':
        return renderAnalysesView();
      case 'visualizations':
        return renderVisualizationsView();
      case 'datasets':
        return renderDatasetsView();
      case 'reports':
        return renderReportsView();
      case 'models':
        return renderModelsView();
      case 'experiments':
        return renderExperimentsView();
      case 'predictions':
        return renderPredictionsView();
      default:
        return renderDashboardView();
    }
  };

  if (loading) {
    return (
      <div className="data-analysis-visualization loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading data analysis results...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="data-analysis-visualization error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="data-analysis-visualization">
      <div className="analysis-header">
        <div className="header-left">
          <h1>Data Analysis & Visualization</h1>
          <p>Comprehensive analytics platform with AI-powered insights and visualizations</p>
        </div>
        <div className="header-right">
          <button 
            className={`refresh-btn ${refreshing ? 'refreshing' : ''}`}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <i className="fas fa-sync-alt"></i>
            {refreshing ? 'Refreshing...' : 'Refresh'}
          </button>
          <button className="export-all-btn" onClick={() => setExportModal(true)}>
            <i className="fas fa-download"></i>
            Export All
          </button>
        </div>
      </div>

      <div className="analysis-navigation">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeView === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveView('dashboard')}
          >
            <i className="fas fa-tachometer-alt"></i>
            Dashboard
          </button>
          <button 
            className={`nav-tab ${activeView === 'analyses' ? 'active' : ''}`}
            onClick={() => setActiveView('analyses')}
          >
            <i className="fas fa-chart-line"></i>
            Analyses
            <span className="count">{analyses.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'visualizations' ? 'active' : ''}`}
            onClick={() => setActiveView('visualizations')}
          >
            <i className="fas fa-chart-bar"></i>
            Visualizations
            <span className="count">{visualizations.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'datasets' ? 'active' : ''}`}
            onClick={() => setActiveView('datasets')}
          >
            <i className="fas fa-database"></i>
            Datasets
            <span className="count">{datasets.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'reports' ? 'active' : ''}`}
            onClick={() => setActiveView('reports')}
          >
            <i className="fas fa-file-alt"></i>
            Reports
            <span className="count">{reports.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'models' ? 'active' : ''}`}
            onClick={() => setActiveView('models')}
          >
            <i className="fas fa-brain"></i>
            Models
            <span className="count">{models.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'experiments' ? 'active' : ''}`}
            onClick={() => setActiveView('experiments')}
          >
            <i className="fas fa-flask"></i>
            Experiments
            <span className="count">{experiments.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'predictions' ? 'active' : ''}`}
            onClick={() => setActiveView('predictions')}
          >
            <i className="fas fa-crystal-ball"></i>
            Predictions
            <span className="count">{predictions.length}</span>
          </button>
        </div>
      </div>

      <div className="analysis-main">
        {renderContent()}
      </div>

      {/* Modals would be rendered here */}
      {analysisModal && selectedAnalysis && (
        <div className="modal-overlay" onClick={() => setAnalysisModal(false)}>
          <div className="analysis-modal" onClick={(e) => e.stopPropagation()}>
            {/* Detailed analysis modal content */}
          </div>
        </div>
      )}
    </div>
  );
};

export default DataAnalysisVisualization;
