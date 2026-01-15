import React, { useState, useEffect, useCallback } from 'react';

const BusinessInsightsPanel = () => {
  const [activeView, setActiveView] = useState('insights');
  const [insights, setInsights] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const [strategicPlans, setStrategicPlans] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState([]);
  const [riskAssessments, setRiskAssessments] = useState([]);
  const [opportunityAnalysis, setOpportunityAnalysis] = useState([]);
  const [actionPlans, setActionPlans] = useState([]);
  const [kpiTracking, setKpiTracking] = useState([]);
  const [selectedInsight, setSelectedInsight] = useState(null);
  const [selectedRecommendation, setSelectedRecommendation] = useState(null);
  const [insightFilters, setInsightFilters] = useState({
    priority: 'all',
    category: 'all',
    timeframe: 'all',
    department: 'all',
    status: 'all',
    impact: 'all'
  });
  const [recommendationFilters, setRecommendationFilters] = useState({
    type: 'all',
    urgency: 'all',
    feasibility: 'all',
    resource: 'all',
    timeline: 'all',
    roi: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [insightModal, setInsightModal] = useState(false);
  const [recommendationModal, setRecommendationModal] = useState(false);
  const [newInsightModal, setNewInsightModal] = useState(false);
  const [newRecommendationModal, setNewRecommendationModal] = useState(false);
  const [implementationModal, setImplementationModal] = useState(false);
  const [trackingModal, setTrackingModal] = useState(false);

  // Mock data generators
  const generateInsights = useCallback(() => {
    const insightTypes = ['operational', 'financial', 'strategic', 'market', 'customer', 'competitive', 'risk', 'opportunity'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    const categories = ['performance', 'efficiency', 'growth', 'optimization', 'innovation', 'security', 'compliance', 'sustainability'];
    const departments = ['sales', 'marketing', 'operations', 'finance', 'hr', 'it', 'r&d', 'legal'];
    const statuses = ['new', 'analyzed', 'validated', 'implemented', 'monitoring'];
    const impacts = ['high', 'medium', 'low'];
    
    const insightTitles = [
      'Revenue Growth Opportunity in Q4', 'Customer Retention Strategy Gap', 'Operational Efficiency Bottleneck',
      'Market Share Expansion Potential', 'Cost Reduction Initiative', 'Product Innovation Opportunity',
      'Competitive Advantage Analysis', 'Risk Mitigation Strategy', 'Customer Satisfaction Improvement',
      'Digital Transformation Impact', 'Supply Chain Optimization', 'Employee Productivity Enhancement',
      'Brand Positioning Strategy', 'Technology Investment ROI', 'Regulatory Compliance Gap',
      'Market Trend Analysis', 'Customer Acquisition Cost Optimization', 'Process Automation Benefits',
      'Strategic Partnership Opportunity', 'Data Analytics Implementation'
    ];

    return Array.from({ length: 15 }, (_, index) => ({
      id: `insight-${index + 1}`,
      title: insightTitles[index] || `Business Insight #${index + 1}`,
      type: insightTypes[Math.floor(Math.random() * insightTypes.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      department: departments[Math.floor(Math.random() * departments.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      impact: impacts[Math.floor(Math.random() * impacts.length)],
      confidence: Math.floor(Math.random() * 30) + 70,
      relevance: Math.floor(Math.random() * 40) + 60,
      createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      description: `Comprehensive analysis revealing ${insightTypes[Math.floor(Math.random() * insightTypes.length)]} insights with significant business implications and actionable recommendations for strategic implementation.`,
      keyFindings: [
        `${Math.floor(Math.random() * 30) + 15}% improvement potential identified`,
        `${Math.floor(Math.random() * 50) + 25}% efficiency gain opportunity`,
        `$${(Math.random() * 500 + 100).toFixed(0)}K revenue impact potential`,
        `${Math.floor(Math.random() * 90) + 30} days implementation timeline`
      ],
      dataSource: ['Enterprise Analytics', 'Market Research', 'Customer Feedback', 'Financial Analysis', 'Operational Metrics'][Math.floor(Math.random() * 5)],
      metrics: {
        accuracy: Math.floor(Math.random() * 20) + 80,
        reliability: Math.floor(Math.random() * 25) + 75,
        timeliness: Math.floor(Math.random() * 30) + 70,
        completeness: Math.floor(Math.random() * 35) + 65
      },
      tags: ['ai-generated', 'validated', 'actionable', 'strategic'].slice(0, Math.floor(Math.random() * 3) + 2)
    }));
  }, []);

  const generateRecommendations = useCallback(() => {
    const recommendationTypes = ['strategic', 'operational', 'tactical', 'financial', 'technological', 'organizational'];
    const urgencies = ['immediate', 'high', 'medium', 'low'];
    const feasibilities = ['high', 'medium', 'low'];
    const resources = ['minimal', 'moderate', 'significant', 'extensive'];
    const timelines = ['1-month', '3-months', '6-months', '12-months', '18-months'];
    const roiLevels = ['high', 'medium', 'low', 'break-even'];
    
    const recommendationTitles = [
      'Implement Advanced Analytics Dashboard', 'Optimize Customer Journey Mapping', 'Enhance Digital Marketing Strategy',
      'Streamline Operations Workflow', 'Develop Strategic Partnership Framework', 'Launch Innovation Lab Initiative',
      'Improve Customer Support Systems', 'Implement Risk Management Protocol', 'Enhance Data Security Measures',
      'Optimize Supply Chain Management', 'Develop Talent Acquisition Strategy', 'Launch Sustainability Initiative',
      'Implement Performance Management System', 'Enhance Brand Positioning Strategy', 'Develop Market Expansion Plan',
      'Optimize Financial Planning Process', 'Launch Digital Transformation Initiative', 'Improve Operational Efficiency',
      'Develop Competitive Intelligence Program', 'Implement Quality Assurance Framework'
    ];

    return Array.from({ length: 12 }, (_, index) => ({
      id: `recommendation-${index + 1}`,
      title: recommendationTitles[index] || `Strategic Recommendation #${index + 1}`,
      type: recommendationTypes[Math.floor(Math.random() * recommendationTypes.length)],
      urgency: urgencies[Math.floor(Math.random() * urgencies.length)],
      feasibility: feasibilities[Math.floor(Math.random() * feasibilities.length)],
      resource: resources[Math.floor(Math.random() * resources.length)],
      timeline: timelines[Math.floor(Math.random() * timelines.length)],
      roi: roiLevels[Math.floor(Math.random() * roiLevels.length)],
      priority: Math.floor(Math.random() * 10) + 1,
      confidence: Math.floor(Math.random() * 25) + 75,
      impact: Math.floor(Math.random() * 40) + 60,
      createdAt: new Date(Date.now() - Math.random() * 20 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 5 * 24 * 60 * 60 * 1000).toISOString(),
      description: `Strategic recommendation based on comprehensive analysis with detailed implementation roadmap and expected business outcomes for organizational improvement.`,
      objectives: [
        `Achieve ${Math.floor(Math.random() * 25) + 15}% performance improvement`,
        `Reduce operational costs by ${Math.floor(Math.random() * 20) + 10}%`,
        `Increase efficiency by ${Math.floor(Math.random() * 30) + 20}%`,
        `Enhance customer satisfaction by ${Math.floor(Math.random() * 35) + 15}%`
      ],
      requirements: [
        `Budget allocation: $${(Math.random() * 200 + 50).toFixed(0)}K`,
        `Team resources: ${Math.floor(Math.random() * 8) + 3} specialists`,
        `Implementation time: ${Math.floor(Math.random() * 180) + 30} days`,
        `Technology stack: Modern enterprise solutions`
      ],
      risks: [
        'Implementation complexity challenges',
        'Resource availability constraints',
        'Change management resistance',
        'Technical integration difficulties'
      ].slice(0, Math.floor(Math.random() * 3) + 2),
      benefits: [
        'Improved operational efficiency',
        'Enhanced competitive advantage',
        'Better customer experience',
        'Increased revenue potential',
        'Reduced operational costs',
        'Improved decision making'
      ].slice(0, Math.floor(Math.random() * 4) + 3),
      implementationSteps: [
        'Initial assessment and planning',
        'Stakeholder alignment and approval',
        'Resource allocation and team formation',
        'Pilot program development',
        'Full-scale implementation',
        'Performance monitoring and optimization'
      ],
      successMetrics: [
        `Performance KPI: ${Math.floor(Math.random() * 30) + 70}% target`,
        `Efficiency metric: ${Math.floor(Math.random() * 25) + 15}% improvement`,
        `ROI target: ${Math.floor(Math.random() * 200) + 100}% within 12 months`,
        `Customer satisfaction: ${Math.floor(Math.random() * 20) + 80}% score`
      ],
      status: ['proposed', 'approved', 'in-progress', 'completed', 'on-hold'][Math.floor(Math.random() * 5)],
      tags: ['strategic', 'high-impact', 'data-driven', 'validated'].slice(0, Math.floor(Math.random() * 3) + 2)
    }));
  }, []);

  const generateStrategicPlans = useCallback(() => {
    const planTypes = ['growth', 'optimization', 'transformation', 'innovation', 'expansion', 'sustainability'];
    const phases = ['planning', 'execution', 'monitoring', 'optimization', 'scaling'];
    
    return Array.from({ length: 8 }, (_, index) => ({
      id: `plan-${index + 1}`,
      name: `Strategic Plan ${index + 1}`,
      type: planTypes[Math.floor(Math.random() * planTypes.length)],
      phase: phases[Math.floor(Math.random() * phases.length)],
      progress: Math.floor(Math.random() * 100),
      timeline: `${Math.floor(Math.random() * 18) + 6} months`,
      budget: (Math.random() * 1000 + 200).toFixed(0),
      objectives: Math.floor(Math.random() * 8) + 5,
      milestones: Math.floor(Math.random() * 12) + 8,
      risks: Math.floor(Math.random() * 5) + 2,
      kpis: Math.floor(Math.random() * 10) + 6
    }));
  }, []);

  const generatePerformanceMetrics = useCallback(() => {
    const metricTypes = ['financial', 'operational', 'customer', 'employee', 'market', 'quality'];
    const trends = ['increasing', 'decreasing', 'stable', 'volatile'];
    
    return Array.from({ length: 10 }, (_, index) => ({
      id: `metric-${index + 1}`,
      name: `Performance Metric ${index + 1}`,
      type: metricTypes[Math.floor(Math.random() * metricTypes.length)],
      value: (Math.random() * 100).toFixed(2),
      target: (Math.random() * 120 + 80).toFixed(2),
      variance: (Math.random() * 20 - 10).toFixed(2),
      trend: trends[Math.floor(Math.random() * trends.length)],
      unit: ['%', '$', 'units', 'days', 'score'][Math.floor(Math.random() * 5)],
      frequency: ['daily', 'weekly', 'monthly', 'quarterly'][Math.floor(Math.random() * 4)],
      lastUpdated: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString()
    }));
  }, []);

  const generateRiskAssessments = useCallback(() => {
    const riskTypes = ['operational', 'financial', 'strategic', 'compliance', 'technology', 'market'];
    const severities = ['critical', 'high', 'medium', 'low'];
    const probabilities = ['very-high', 'high', 'medium', 'low', 'very-low'];
    
    return Array.from({ length: 6 }, (_, index) => ({
      id: `risk-${index + 1}`,
      name: `Risk Assessment ${index + 1}`,
      type: riskTypes[Math.floor(Math.random() * riskTypes.length)],
      severity: severities[Math.floor(Math.random() * severities.length)],
      probability: probabilities[Math.floor(Math.random() * probabilities.length)],
      impact: Math.floor(Math.random() * 10) + 1,
      mitigation: Math.floor(Math.random() * 80) + 20,
      status: ['identified', 'analyzing', 'mitigating', 'monitoring', 'resolved'][Math.floor(Math.random() * 5)],
      owner: ['Risk Team', 'Operations', 'Finance', 'IT Security', 'Compliance'][Math.floor(Math.random() * 5)]
    }));
  }, []);

  const generateOpportunityAnalysis = useCallback(() => {
    const opportunityTypes = ['market', 'product', 'technology', 'partnership', 'expansion', 'efficiency'];
    const potentials = ['high', 'medium', 'low'];
    
    return Array.from({ length: 7 }, (_, index) => ({
      id: `opportunity-${index + 1}`,
      name: `Opportunity ${index + 1}`,
      type: opportunityTypes[Math.floor(Math.random() * opportunityTypes.length)],
      potential: potentials[Math.floor(Math.random() * potentials.length)],
      value: (Math.random() * 500 + 100).toFixed(0),
      timeframe: `${Math.floor(Math.random() * 12) + 3} months`,
      probability: Math.floor(Math.random() * 60) + 40,
      investment: (Math.random() * 200 + 50).toFixed(0),
      roi: Math.floor(Math.random() * 300) + 150,
      status: ['identified', 'evaluating', 'planning', 'pursuing', 'realized'][Math.floor(Math.random() * 5)]
    }));
  }, []);

  const generateActionPlans = useCallback(() => {
    const actionTypes = ['implementation', 'optimization', 'expansion', 'improvement', 'transformation'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    
    return Array.from({ length: 9 }, (_, index) => ({
      id: `action-${index + 1}`,
      name: `Action Plan ${index + 1}`,
      type: actionTypes[Math.floor(Math.random() * actionTypes.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      progress: Math.floor(Math.random() * 100),
      dueDate: new Date(Date.now() + Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      assignee: ['Team Alpha', 'Team Beta', 'Team Gamma', 'Team Delta'][Math.floor(Math.random() * 4)],
      tasks: Math.floor(Math.random() * 12) + 5,
      completed: Math.floor(Math.random() * 8) + 2,
      budget: (Math.random() * 150 + 25).toFixed(0),
      resources: Math.floor(Math.random() * 6) + 3
    }));
  }, []);

  const generateKpiTracking = useCallback(() => {
    const kpiCategories = ['revenue', 'growth', 'efficiency', 'quality', 'satisfaction', 'retention'];
    
    return Array.from({ length: 12 }, (_, index) => ({
      id: `kpi-${index + 1}`,
      name: `KPI Metric ${index + 1}`,
      category: kpiCategories[Math.floor(Math.random() * kpiCategories.length)],
      current: (Math.random() * 100).toFixed(1),
      target: (Math.random() * 120 + 80).toFixed(1),
      achievement: Math.floor(Math.random() * 120) + 60,
      trend: Math.random() > 0.5 ? 'up' : 'down',
      change: (Math.random() * 20 - 10).toFixed(1),
      frequency: ['daily', 'weekly', 'monthly'][Math.floor(Math.random() * 3)],
      owner: ['Sales', 'Marketing', 'Operations', 'Finance', 'HR'][Math.floor(Math.random() * 5)]
    }));
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API calls with realistic delays
        await new Promise(resolve => setTimeout(resolve, 800));
        
        setInsights(generateInsights());
        setRecommendations(generateRecommendations());
        setStrategicPlans(generateStrategicPlans());
        setPerformanceMetrics(generatePerformanceMetrics());
        setRiskAssessments(generateRiskAssessments());
        setOpportunityAnalysis(generateOpportunityAnalysis());
        setActionPlans(generateActionPlans());
        setKpiTracking(generateKpiTracking());
        
      } catch (error) {
        console.error('Error loading business insights data:', error);
        setError('Failed to load business insights data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateInsights, generateRecommendations, generateStrategicPlans, generatePerformanceMetrics, generateRiskAssessments, generateOpportunityAnalysis, generateActionPlans, generateKpiTracking]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setInsights(generateInsights());
    setRecommendations(generateRecommendations());
    setStrategicPlans(generateStrategicPlans());
    setPerformanceMetrics(generatePerformanceMetrics());
    setRiskAssessments(generateRiskAssessments());
    setOpportunityAnalysis(generateOpportunityAnalysis());
    setActionPlans(generateActionPlans());
    setKpiTracking(generateKpiTracking());
    
    setRefreshing(false);
  };

  // Filter and search logic
  const filteredInsights = insights.filter(insight => {
    const matchesFilters = 
      (insightFilters.priority === 'all' || insight.priority === insightFilters.priority) &&
      (insightFilters.category === 'all' || insight.category === insightFilters.category) &&
      (insightFilters.department === 'all' || insight.department === insightFilters.department) &&
      (insightFilters.status === 'all' || insight.status === insightFilters.status) &&
      (insightFilters.impact === 'all' || insight.impact === insightFilters.impact);
    
    const matchesSearch = !searchQuery || 
      insight.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      insight.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      insight.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilters && matchesSearch;
  });

  const filteredRecommendations = recommendations.filter(recommendation => {
    const matchesFilters = 
      (recommendationFilters.type === 'all' || recommendation.type === recommendationFilters.type) &&
      (recommendationFilters.urgency === 'all' || recommendation.urgency === recommendationFilters.urgency) &&
      (recommendationFilters.feasibility === 'all' || recommendation.feasibility === recommendationFilters.feasibility) &&
      (recommendationFilters.resource === 'all' || recommendation.resource === recommendationFilters.resource) &&
      (recommendationFilters.timeline === 'all' || recommendation.timeline === recommendationFilters.timeline) &&
      (recommendationFilters.roi === 'all' || recommendation.roi === recommendationFilters.roi);
    
    const matchesSearch = !searchQuery || 
      recommendation.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recommendation.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      recommendation.type.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilters && matchesSearch;
  });

  const sortData = (data, type) => {
    return data.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'relevance':
          aValue = type === 'insights' ? a.relevance : a.impact;
          bValue = type === 'insights' ? b.relevance : b.impact;
          break;
        case 'date':
          aValue = new Date(a.updatedAt || a.createdAt);
          bValue = new Date(b.updatedAt || b.createdAt);
          break;
        case 'priority':
          const priorityOrder = { critical: 4, high: 3, medium: 2, low: 1 };
          aValue = priorityOrder[a.priority] || a.priority || 0;
          bValue = priorityOrder[b.priority] || b.priority || 0;
          break;
        case 'confidence':
          aValue = a.confidence || 0;
          bValue = b.confidence || 0;
          break;
        default:
          aValue = a.title;
          bValue = b.title;
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });
  };

  const sortedInsights = sortData([...filteredInsights], 'insights');
  const sortedRecommendations = sortData([...filteredRecommendations], 'recommendations');

  const getPriorityColor = (priority) => {
    const colors = {
      critical: '#ff4444',
      high: '#ff8800',
      medium: '#ffbb33',
      low: '#00aa00'
    };
    return colors[priority] || '#666';
  };

  const getStatusColor = (status) => {
    const colors = {
      new: '#007bff',
      analyzed: '#17a2b8',
      validated: '#28a745',
      implemented: '#6f42c1',
      monitoring: '#fd7e14',
      proposed: '#007bff',
      approved: '#28a745',
      'in-progress': '#ffc107',
      completed: '#28a745',
      'on-hold': '#6c757d'
    };
    return colors[status] || '#666';
  };

  const getUrgencyColor = (urgency) => {
    const colors = {
      immediate: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[urgency] || '#666';
  };

  const renderInsightsView = () => (
    <div className="insights-content">
      <div className="insights-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search insights..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="sort-controls">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="relevance">Sort by Relevance</option>
              <option value="date">Sort by Date</option>
              <option value="priority">Sort by Priority</option>
              <option value="confidence">Sort by Confidence</option>
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
          <div className="filter-group">
            <label>Priority:</label>
            <select value={insightFilters.priority} onChange={(e) => setInsightFilters({...insightFilters, priority: e.target.value})}>
              <option value="all">All Priorities</option>
              <option value="critical">Critical</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Category:</label>
            <select value={insightFilters.category} onChange={(e) => setInsightFilters({...insightFilters, category: e.target.value})}>
              <option value="all">All Categories</option>
              <option value="performance">Performance</option>
              <option value="efficiency">Efficiency</option>
              <option value="growth">Growth</option>
              <option value="optimization">Optimization</option>
              <option value="innovation">Innovation</option>
              <option value="security">Security</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Department:</label>
            <select value={insightFilters.department} onChange={(e) => setInsightFilters({...insightFilters, department: e.target.value})}>
              <option value="all">All Departments</option>
              <option value="sales">Sales</option>
              <option value="marketing">Marketing</option>
              <option value="operations">Operations</option>
              <option value="finance">Finance</option>
              <option value="hr">HR</option>
              <option value="it">IT</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Status:</label>
            <select value={insightFilters.status} onChange={(e) => setInsightFilters({...insightFilters, status: e.target.value})}>
              <option value="all">All Statuses</option>
              <option value="new">New</option>
              <option value="analyzed">Analyzed</option>
              <option value="validated">Validated</option>
              <option value="implemented">Implemented</option>
              <option value="monitoring">Monitoring</option>
            </select>
          </div>
        </div>
      </div>

      <div className="insights-grid">
        {sortedInsights.map(insight => (
          <div key={insight.id} className="insight-card" onClick={() => {setSelectedInsight(insight); setInsightModal(true);}}>
            <div className="insight-header">
              <h3>{insight.title}</h3>
              <div className="insight-badges">
                <span className="priority-badge" style={{ backgroundColor: getPriorityColor(insight.priority) }}>
                  {insight.priority}
                </span>
                <span className="status-badge" style={{ backgroundColor: getStatusColor(insight.status) }}>
                  {insight.status}
                </span>
              </div>
            </div>
            <div className="insight-meta">
              <span className="insight-type">{insight.type}</span>
              <span className="insight-category">{insight.category}</span>
              <span className="insight-department">{insight.department}</span>
            </div>
            <p className="insight-description">{insight.description}</p>
            <div className="insight-metrics">
              <div className="metric">
                <span className="metric-label">Confidence:</span>
                <span className="metric-value">{insight.confidence}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${insight.confidence}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Relevance:</span>
                <span className="metric-value">{insight.relevance}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${insight.relevance}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Impact:</span>
                <span className="metric-value">{insight.impact}</span>
                <div className="impact-indicator">
                  <div className={`impact-level ${insight.impact}`}></div>
                </div>
              </div>
            </div>
            <div className="insight-footer">
              <span className="insight-source">{insight.dataSource}</span>
              <span className="insight-date">{new Date(insight.updatedAt).toLocaleDateString()}</span>
            </div>
            <div className="insight-tags">
              {insight.tags.map((tag, index) => (
                <span key={index} className="insight-tag">{tag}</span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRecommendationsView = () => (
    <div className="recommendations-content">
      <div className="recommendations-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search recommendations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="sort-controls">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="relevance">Sort by Impact</option>
              <option value="date">Sort by Date</option>
              <option value="priority">Sort by Priority</option>
              <option value="confidence">Sort by Confidence</option>
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
          <div className="filter-group">
            <label>Type:</label>
            <select value={recommendationFilters.type} onChange={(e) => setRecommendationFilters({...recommendationFilters, type: e.target.value})}>
              <option value="all">All Types</option>
              <option value="strategic">Strategic</option>
              <option value="operational">Operational</option>
              <option value="tactical">Tactical</option>
              <option value="financial">Financial</option>
              <option value="technological">Technological</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Urgency:</label>
            <select value={recommendationFilters.urgency} onChange={(e) => setRecommendationFilters({...recommendationFilters, urgency: e.target.value})}>
              <option value="all">All Urgencies</option>
              <option value="immediate">Immediate</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Feasibility:</label>
            <select value={recommendationFilters.feasibility} onChange={(e) => setRecommendationFilters({...recommendationFilters, feasibility: e.target.value})}>
              <option value="all">All Levels</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>
          <div className="filter-group">
            <label>Timeline:</label>
            <select value={recommendationFilters.timeline} onChange={(e) => setRecommendationFilters({...recommendationFilters, timeline: e.target.value})}>
              <option value="all">All Timelines</option>
              <option value="1-month">1 Month</option>
              <option value="3-months">3 Months</option>
              <option value="6-months">6 Months</option>
              <option value="12-months">12 Months</option>
            </select>
          </div>
        </div>
      </div>

      <div className="recommendations-grid">
        {sortedRecommendations.map(recommendation => (
          <div key={recommendation.id} className="recommendation-card" onClick={() => {setSelectedRecommendation(recommendation); setRecommendationModal(true);}}>
            <div className="recommendation-header">
              <h3>{recommendation.title}</h3>
              <div className="recommendation-badges">
                <span className="urgency-badge" style={{ backgroundColor: getUrgencyColor(recommendation.urgency) }}>
                  {recommendation.urgency}
                </span>
                <span className="status-badge" style={{ backgroundColor: getStatusColor(recommendation.status) }}>
                  {recommendation.status}
                </span>
              </div>
            </div>
            <div className="recommendation-meta">
              <span className="recommendation-type">{recommendation.type}</span>
              <span className="recommendation-timeline">{recommendation.timeline}</span>
              <span className="recommendation-feasibility">{recommendation.feasibility} feasibility</span>
            </div>
            <p className="recommendation-description">{recommendation.description}</p>
            <div className="recommendation-metrics">
              <div className="metric">
                <span className="metric-label">Priority:</span>
                <span className="metric-value">{recommendation.priority}/10</span>
                <div className="priority-bar">
                  <div className="priority-fill" style={{ width: `${recommendation.priority * 10}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Impact:</span>
                <span className="metric-value">{recommendation.impact}%</span>
                <div className="impact-bar">
                  <div className="impact-fill" style={{ width: `${recommendation.impact}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Confidence:</span>
                <span className="metric-value">{recommendation.confidence}%</span>
                <div className="confidence-bar">
                  <div className="confidence-fill" style={{ width: `${recommendation.confidence}%` }}></div>
                </div>
              </div>
            </div>
            <div className="recommendation-resources">
              <div className="resource-item">
                <i className="fas fa-clock"></i>
                <span>{recommendation.timeline}</span>
              </div>
              <div className="resource-item">
                <i className="fas fa-users"></i>
                <span>{recommendation.resource} resources</span>
              </div>
              <div className="resource-item">
                <i className="fas fa-chart-line"></i>
                <span>{recommendation.roi} ROI</span>
              </div>
            </div>
            <div className="recommendation-footer">
              <span className="recommendation-date">{new Date(recommendation.updatedAt).toLocaleDateString()}</span>
              <button className="implement-btn">Implement</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderStrategicPlansView = () => (
    <div className="strategic-plans-content">
      <div className="plans-header">
        <h3>Strategic Plans Overview</h3>
        <button className="new-plan-btn" onClick={() => setNewInsightModal(true)}>
          <i className="fas fa-plus"></i>
          New Strategic Plan
        </button>
      </div>
      <div className="plans-grid">
        {strategicPlans.map(plan => (
          <div key={plan.id} className="plan-card">
            <div className="plan-header">
              <h4>{plan.name}</h4>
              <span className="plan-type">{plan.type}</span>
            </div>
            <div className="plan-phase">
              <span className="phase-label">Current Phase:</span>
              <span className="phase-value">{plan.phase}</span>
            </div>
            <div className="plan-progress">
              <div className="progress-header">
                <span>Progress</span>
                <span>{plan.progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${plan.progress}%` }}></div>
              </div>
            </div>
            <div className="plan-stats">
              <div className="stat">
                <span className="stat-label">Timeline:</span>
                <span className="stat-value">{plan.timeline}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Budget:</span>
                <span className="stat-value">${plan.budget}K</span>
              </div>
              <div className="stat">
                <span className="stat-label">Objectives:</span>
                <span className="stat-value">{plan.objectives}</span>
              </div>
              <div className="stat">
                <span className="stat-label">Milestones:</span>
                <span className="stat-value">{plan.milestones}</span>
              </div>
            </div>
            <div className="plan-indicators">
              <div className="indicator">
                <i className="fas fa-exclamation-triangle"></i>
                <span>{plan.risks} risks identified</span>
              </div>
              <div className="indicator">
                <i className="fas fa-chart-bar"></i>
                <span>{plan.kpis} KPIs tracked</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderPerformanceMetricsView = () => (
    <div className="performance-metrics-content">
      <div className="metrics-header">
        <h3>Performance Metrics Dashboard</h3>
        <div className="metrics-controls">
          <select className="time-range">
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="12m">Last 12 Months</option>
          </select>
          <button className="refresh-metrics" onClick={handleRefresh}>
            <i className="fas fa-sync-alt"></i>
          </button>
        </div>
      </div>
      <div className="metrics-grid">
        {performanceMetrics.map(metric => (
          <div key={metric.id} className="metric-card">
            <div className="metric-header">
              <h4>{metric.name}</h4>
              <span className="metric-type">{metric.type}</span>
            </div>
            <div className="metric-value">
              <span className="current-value">{metric.value}{metric.unit}</span>
              <span className="target-value">Target: {metric.target}{metric.unit}</span>
            </div>
            <div className="metric-variance">
              <span className={`variance ${parseFloat(metric.variance) >= 0 ? 'positive' : 'negative'}`}>
                {parseFloat(metric.variance) >= 0 ? '+' : ''}{metric.variance}%
              </span>
              <span className="variance-label">vs target</span>
            </div>
            <div className="metric-trend">
              <div className={`trend-indicator ${metric.trend}`}>
                <i className={`fas fa-arrow-${metric.trend === 'increasing' ? 'up' : metric.trend === 'decreasing' ? 'down' : 'right'}`}></i>
                <span>{metric.trend}</span>
              </div>
            </div>
            <div className="metric-footer">
              <span className="frequency">{metric.frequency}</span>
              <span className="last-updated">{new Date(metric.lastUpdated).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderRiskAssessmentsView = () => (
    <div className="risk-assessments-content">
      <div className="risk-header">
        <h3>Risk Assessments</h3>
        <div className="risk-summary">
          <div className="risk-stat">
            <span className="stat-value">{riskAssessments.filter(r => r.severity === 'critical').length}</span>
            <span className="stat-label">Critical</span>
          </div>
          <div className="risk-stat">
            <span className="stat-value">{riskAssessments.filter(r => r.severity === 'high').length}</span>
            <span className="stat-label">High</span>
          </div>
          <div className="risk-stat">
            <span className="stat-value">{riskAssessments.filter(r => r.status === 'mitigating').length}</span>
            <span className="stat-label">In Progress</span>
          </div>
        </div>
      </div>
      <div className="risk-grid">
        {riskAssessments.map(risk => (
          <div key={risk.id} className="risk-card">
            <div className="risk-header">
              <h4>{risk.name}</h4>
              <div className="risk-badges">
                <span className="severity-badge" style={{ backgroundColor: getPriorityColor(risk.severity) }}>
                  {risk.severity}
                </span>
                <span className="status-badge" style={{ backgroundColor: getStatusColor(risk.status) }}>
                  {risk.status}
                </span>
              </div>
            </div>
            <div className="risk-details">
              <div className="risk-type">{risk.type} risk</div>
              <div className="risk-owner">Owner: {risk.owner}</div>
            </div>
            <div className="risk-metrics">
              <div className="risk-metric">
                <span className="metric-label">Probability:</span>
                <span className="metric-value">{risk.probability}</span>
              </div>
              <div className="risk-metric">
                <span className="metric-label">Impact:</span>
                <span className="metric-value">{risk.impact}/10</span>
              </div>
              <div className="risk-metric">
                <span className="metric-label">Mitigation:</span>
                <span className="metric-value">{risk.mitigation}%</span>
              </div>
            </div>
            <div className="mitigation-progress">
              <div className="progress-header">
                <span>Mitigation Progress</span>
                <span>{risk.mitigation}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${risk.mitigation}%` }}></div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderOpportunityAnalysisView = () => (
    <div className="opportunity-analysis-content">
      <div className="opportunity-header">
        <h3>Opportunity Analysis</h3>
        <div className="opportunity-summary">
          <div className="opportunity-stat">
            <span className="stat-value">${opportunityAnalysis.reduce((sum, opp) => sum + parseFloat(opp.value), 0).toFixed(0)}K</span>
            <span className="stat-label">Total Value</span>
          </div>
          <div className="opportunity-stat">
            <span className="stat-value">{opportunityAnalysis.filter(o => o.potential === 'high').length}</span>
            <span className="stat-label">High Potential</span>
          </div>
          <div className="opportunity-stat">
            <span className="stat-value">{Math.round(opportunityAnalysis.reduce((sum, opp) => sum + opp.probability, 0) / opportunityAnalysis.length)}%</span>
            <span className="stat-label">Avg Probability</span>
          </div>
        </div>
      </div>
      <div className="opportunity-grid">
        {opportunityAnalysis.map(opportunity => (
          <div key={opportunity.id} className="opportunity-card">
            <div className="opportunity-header">
              <h4>{opportunity.name}</h4>
              <span className="opportunity-type">{opportunity.type}</span>
            </div>
            <div className="opportunity-value">
              <div className="value-item">
                <span className="value-label">Potential Value:</span>
                <span className="value-amount">${opportunity.value}K</span>
              </div>
              <div className="value-item">
                <span className="value-label">Investment:</span>
                <span className="value-amount">${opportunity.investment}K</span>
              </div>
              <div className="value-item">
                <span className="value-label">Expected ROI:</span>
                <span className="value-amount">{opportunity.roi}%</span>
              </div>
            </div>
            <div className="opportunity-metrics">
              <div className="metric">
                <span className="metric-label">Probability:</span>
                <span className="metric-value">{opportunity.probability}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${opportunity.probability}%` }}></div>
                </div>
              </div>
              <div className="metric">
                <span className="metric-label">Potential:</span>
                <span className={`potential-level ${opportunity.potential}`}>{opportunity.potential}</span>
              </div>
            </div>
            <div className="opportunity-timeline">
              <i className="fas fa-calendar-alt"></i>
              <span>{opportunity.timeframe}</span>
            </div>
            <div className="opportunity-status">
              <span className="status-badge" style={{ backgroundColor: getStatusColor(opportunity.status) }}>
                {opportunity.status}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderActionPlansView = () => (
    <div className="action-plans-content">
      <div className="action-header">
        <h3>Action Plans</h3>
        <div className="action-summary">
          <div className="action-stat">
            <span className="stat-value">{actionPlans.filter(a => a.priority === 'critical').length}</span>
            <span className="stat-label">Critical</span>
          </div>
          <div className="action-stat">
            <span className="stat-value">{actionPlans.filter(a => a.progress === 100).length}</span>
            <span className="stat-label">Completed</span>
          </div>
          <div className="action-stat">
            <span className="stat-value">{Math.round(actionPlans.reduce((sum, a) => sum + a.progress, 0) / actionPlans.length)}%</span>
            <span className="stat-label">Avg Progress</span>
          </div>
        </div>
      </div>
      <div className="action-grid">
        {actionPlans.map(plan => (
          <div key={plan.id} className="action-card">
            <div className="action-header">
              <h4>{plan.name}</h4>
              <span className="priority-badge" style={{ backgroundColor: getPriorityColor(plan.priority) }}>
                {plan.priority}
              </span>
            </div>
            <div className="action-details">
              <div className="detail-item">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{plan.type}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Assignee:</span>
                <span className="detail-value">{plan.assignee}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">Due Date:</span>
                <span className="detail-value">{new Date(plan.dueDate).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="action-progress">
              <div className="progress-header">
                <span>Progress</span>
                <span>{plan.progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${plan.progress}%` }}></div>
              </div>
            </div>
            <div className="action-tasks">
              <div className="task-summary">
                <span>{plan.completed} of {plan.tasks} tasks completed</span>
              </div>
            </div>
            <div className="action-resources">
              <div className="resource-item">
                <i className="fas fa-dollar-sign"></i>
                <span>${plan.budget}K budget</span>
              </div>
              <div className="resource-item">
                <i className="fas fa-users"></i>
                <span>{plan.resources} resources</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderKpiTrackingView = () => (
    <div className="kpi-tracking-content">
      <div className="kpi-header">
        <h3>KPI Tracking Dashboard</h3>
        <div className="kpi-summary">
          <div className="kpi-stat">
            <span className="stat-value">{kpiTracking.filter(k => k.achievement >= 100).length}</span>
            <span className="stat-label">Targets Met</span>
          </div>
          <div className="kpi-stat">
            <span className="stat-value">{kpiTracking.filter(k => k.trend === 'up').length}</span>
            <span className="stat-label">Trending Up</span>
          </div>
          <div className="kpi-stat">
            <span className="stat-value">{Math.round(kpiTracking.reduce((sum, k) => sum + k.achievement, 0) / kpiTracking.length)}%</span>
            <span className="stat-label">Avg Achievement</span>
          </div>
        </div>
      </div>
      <div className="kpi-grid">
        {kpiTracking.map(kpi => (
          <div key={kpi.id} className="kpi-card">
            <div className="kpi-header">
              <h4>{kpi.name}</h4>
              <span className="kpi-category">{kpi.category}</span>
            </div>
            <div className="kpi-values">
              <div className="value-display">
                <span className="current">{kpi.current}</span>
                <span className="target">/ {kpi.target}</span>
              </div>
              <div className={`trend-indicator ${kpi.trend}`}>
                <i className={`fas fa-arrow-${kpi.trend === 'up' ? 'up' : 'down'}`}></i>
                <span>{kpi.change}%</span>
              </div>
            </div>
            <div className="kpi-achievement">
              <div className="achievement-header">
                <span>Achievement</span>
                <span>{kpi.achievement}%</span>
              </div>
              <div className="achievement-bar">
                <div 
                  className="achievement-fill" 
                  style={{ 
                    width: `${Math.min(kpi.achievement, 100)}%`,
                    backgroundColor: kpi.achievement >= 100 ? '#28a745' : kpi.achievement >= 80 ? '#ffc107' : '#dc3545'
                  }}
                ></div>
              </div>
            </div>
            <div className="kpi-details">
              <div className="detail">
                <span className="label">Owner:</span>
                <span className="value">{kpi.owner}</span>
              </div>
              <div className="detail">
                <span className="label">Frequency:</span>
                <span className="value">{kpi.frequency}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'insights':
        return renderInsightsView();
      case 'recommendations':
        return renderRecommendationsView();
      case 'strategic-plans':
        return renderStrategicPlansView();
      case 'performance-metrics':
        return renderPerformanceMetricsView();
      case 'risk-assessments':
        return renderRiskAssessmentsView();
      case 'opportunity-analysis':
        return renderOpportunityAnalysisView();
      case 'action-plans':
        return renderActionPlansView();
      case 'kpi-tracking':
        return renderKpiTrackingView();
      default:
        return renderInsightsView();
    }
  };

  if (loading) {
    return (
      <div className="business-insights-panel loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading business insights...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="business-insights-panel error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="business-insights-panel">
      <div className="insights-header">
        <div className="header-left">
          <h1>Business Insights & Recommendations</h1>
          <p>AI-powered business intelligence and strategic recommendations</p>
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
          <button className="export-btn">
            <i className="fas fa-download"></i>
            Export
          </button>
        </div>
      </div>

      <div className="insights-navigation">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeView === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveView('insights')}
          >
            <i className="fas fa-lightbulb"></i>
            Insights
            <span className="count">{insights.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'recommendations' ? 'active' : ''}`}
            onClick={() => setActiveView('recommendations')}
          >
            <i className="fas fa-thumbs-up"></i>
            Recommendations
            <span className="count">{recommendations.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'strategic-plans' ? 'active' : ''}`}
            onClick={() => setActiveView('strategic-plans')}
          >
            <i className="fas fa-chess"></i>
            Strategic Plans
            <span className="count">{strategicPlans.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'performance-metrics' ? 'active' : ''}`}
            onClick={() => setActiveView('performance-metrics')}
          >
            <i className="fas fa-chart-line"></i>
            Performance
            <span className="count">{performanceMetrics.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'risk-assessments' ? 'active' : ''}`}
            onClick={() => setActiveView('risk-assessments')}
          >
            <i className="fas fa-shield-alt"></i>
            Risks
            <span className="count">{riskAssessments.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'opportunity-analysis' ? 'active' : ''}`}
            onClick={() => setActiveView('opportunity-analysis')}
          >
            <i className="fas fa-bullseye"></i>
            Opportunities
            <span className="count">{opportunityAnalysis.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'action-plans' ? 'active' : ''}`}
            onClick={() => setActiveView('action-plans')}
          >
            <i className="fas fa-tasks"></i>
            Action Plans
            <span className="count">{actionPlans.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'kpi-tracking' ? 'active' : ''}`}
            onClick={() => setActiveView('kpi-tracking')}
          >
            <i className="fas fa-tachometer-alt"></i>
            KPI Tracking
            <span className="count">{kpiTracking.length}</span>
          </button>
        </div>
      </div>

      <div className="insights-main">
        {renderContent()}
      </div>

      {/* Modals would be rendered here */}
      {insightModal && selectedInsight && (
        <div className="modal-overlay" onClick={() => setInsightModal(false)}>
          <div className="insight-modal" onClick={(e) => e.stopPropagation()}>
            {/* Detailed insight modal content */}
          </div>
        </div>
      )}

      {recommendationModal && selectedRecommendation && (
        <div className="modal-overlay" onClick={() => setRecommendationModal(false)}>
          <div className="recommendation-modal" onClick={(e) => e.stopPropagation()}>
            {/* Detailed recommendation modal content */}
          </div>
        </div>
      )}
    </div>
  );
};

export default BusinessInsightsPanel;
