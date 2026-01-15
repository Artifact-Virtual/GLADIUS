import React, { useState, useEffect, useCallback } from 'react';

const ResearchQueryManagement = () => {
  const [activeView, setActiveView] = useState('queries');
  const [queries, setQueries] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [projects, setProjects] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [insights, setInsights] = useState([]);
  const [selectedQuery, setSelectedQuery] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [queryFilters, setQueryFilters] = useState({
    status: 'all',
    priority: 'all',
    type: 'all',
    department: 'all',
    complexity: 'all',
    assignee: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('created');
  const [sortOrder, setSortOrder] = useState('desc');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [newQueryModal, setNewQueryModal] = useState(false);
  const [taskModal, setTaskModal] = useState(false);
  const [projectModal, setProjectModal] = useState(false);
  const [workflowModal, setWorkflowModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);

  // Mock data generators
  const generateQueries = useCallback(() => {
    const queryTypes = ['data-analysis', 'market-research', 'competitive-intel', 'customer-insight', 'trend-analysis', 'risk-assessment'];
    const statuses = ['active', 'completed', 'on-hold', 'cancelled', 'pending', 'in-review'];
    const priorities = ['urgent', 'high', 'medium', 'low'];
    const complexities = ['simple', 'moderate', 'complex', 'advanced'];
    const departments = ['marketing', 'sales', 'finance', 'operations', 'research', 'strategy'];
    
    const queryTitles = [
      'Customer Satisfaction Analysis for Q4', 'Competitive Pricing Strategy Research', 'Market Expansion Feasibility Study',
      'Brand Perception Analysis', 'Product Feature Demand Research', 'Customer Churn Risk Assessment',
      'Supply Chain Optimization Study', 'Digital Transformation Impact Analysis', 'Employee Engagement Research',
      'Revenue Stream Diversification Study', 'Customer Journey Mapping Research', 'Technology Adoption Trends Analysis',
      'Regulatory Impact Assessment', 'Market Share Analysis by Region', 'Social Media Sentiment Research',
      'Investment ROI Performance Study', 'Operational Efficiency Analysis', 'Innovation Opportunity Research'
    ];

    return Array.from({ length: 18 }, (_, index) => ({
      id: `query-${index + 1}`,
      title: queryTitles[index] || `Research Query ${index + 1}`,
      type: queryTypes[Math.floor(Math.random() * queryTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      complexity: complexities[Math.floor(Math.random() * complexities.length)],
      department: departments[Math.floor(Math.random() * departments.length)],
      assignee: ['Dr. Sarah Chen', 'Michael Rodriguez', 'Emma Thompson', 'David Kim', 'Rachel Adams'][Math.floor(Math.random() * 5)],
      description: `Comprehensive research query focusing on ${queryTypes[Math.floor(Math.random() * queryTypes.length)]} to provide actionable business insights and strategic recommendations.`,
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      dueDate: new Date(Date.now() + Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString(),
      progress: Math.floor(Math.random() * 100),
      estimatedHours: Math.floor(Math.random() * 80) + 20,
      actualHours: Math.floor(Math.random() * 60) + 10,
      budgetAllocated: Math.floor(Math.random() * 50000) + 10000,
      budgetSpent: Math.floor(Math.random() * 30000) + 5000,
      confidence: Math.floor(Math.random() * 30) + 70,
      riskLevel: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
      stakeholders: Math.floor(Math.random() * 8) + 2,
      dataSources: Math.floor(Math.random() * 10) + 3,
      milestones: Math.floor(Math.random() * 6) + 2,
      deliverables: Math.floor(Math.random() * 5) + 2,
      findings: Math.floor(Math.random() * 8) + 3,
      recommendations: Math.floor(Math.random() * 6) + 2,
      tags: ['strategic', 'data-driven', 'customer-focused', 'competitive', 'financial', 'operational'].slice(0, Math.floor(Math.random() * 4) + 2),
      keyInsights: [
        `${Math.floor(Math.random() * 30) + 10}% improvement opportunity identified`,
        `${Math.floor(Math.random() * 25) + 5} actionable recommendations developed`,
        `${Math.floor(Math.random() * 50) + 50}% confidence in strategic direction`,
        `$${(Math.random() * 200 + 50).toFixed(0)}K potential business impact`
      ],
      relatedProjects: Math.floor(Math.random() * 4) + 1,
      collaborators: Math.floor(Math.random() * 6) + 2,
      documents: Math.floor(Math.random() * 15) + 5,
      analyses: Math.floor(Math.random() * 8) + 3,
      lastActivity: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
      methodology: ['quantitative', 'qualitative', 'mixed-methods'][Math.floor(Math.random() * 3)],
      dataQuality: Math.floor(Math.random() * 25) + 75,
      completionRate: Math.floor(Math.random() * 40) + 60
    }));
  }, []);

  const generateTasks = useCallback(() => {
    const taskTypes = ['data-collection', 'analysis', 'report-writing', 'presentation', 'review', 'validation'];
    const statuses = ['to-do', 'in-progress', 'completed', 'blocked', 'cancelled'];
    const priorities = ['urgent', 'high', 'medium', 'low'];
    
    const taskTitles = [
      'Collect customer survey responses', 'Analyze market trends data', 'Write competitive analysis report',
      'Prepare executive presentation', 'Review research methodology', 'Validate data quality',
      'Conduct stakeholder interviews', 'Process statistical analysis', 'Create data visualizations',
      'Draft research findings', 'Perform peer review', 'Update project timeline',
      'Coordinate team meetings', 'Finalize research deliverables', 'Archive project documents'
    ];

    return Array.from({ length: 15 }, (_, index) => ({
      id: `task-${index + 1}`,
      title: taskTitles[index] || `Research Task ${index + 1}`,
      type: taskTypes[Math.floor(Math.random() * taskTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      queryId: `query-${Math.floor(Math.random() * 18) + 1}`,
      assignee: ['Dr. Sarah Chen', 'Michael Rodriguez', 'Emma Thompson', 'David Kim', 'Rachel Adams'][Math.floor(Math.random() * 5)],
      description: `Detailed task focusing on ${taskTypes[Math.floor(Math.random() * taskTypes.length)]} as part of comprehensive research project execution.`,
      createdAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      dueDate: new Date(Date.now() + Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      estimatedHours: Math.floor(Math.random() * 20) + 2,
      actualHours: Math.floor(Math.random() * 15) + 1,
      progress: Math.floor(Math.random() * 100),
      dependencies: Math.floor(Math.random() * 3),
      subtasks: Math.floor(Math.random() * 5) + 1,
      attachments: Math.floor(Math.random() * 8) + 2,
      comments: Math.floor(Math.random() * 10) + 3,
      checklist: Array.from({ length: Math.floor(Math.random() * 6) + 3 }, (_, i) => ({
        id: `check-${i + 1}`,
        text: `Task checkpoint ${i + 1}`,
        completed: Math.random() > 0.4
      })),
      lastUpdated: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      urgency: Math.floor(Math.random() * 10) + 1,
      impact: Math.floor(Math.random() * 10) + 1,
      riskFactors: ['resource-constraints', 'data-availability', 'time-pressure', 'complexity'][Math.floor(Math.random() * 4)],
      deliverables: Math.floor(Math.random() * 3) + 1,
      reviewers: Math.floor(Math.random() * 3) + 1,
      qualityScore: Math.floor(Math.random() * 30) + 70
    }));
  }, []);

  const generateProjects = useCallback(() => {
    const projectTypes = ['research-initiative', 'competitive-analysis', 'market-study', 'customer-research', 'strategic-analysis'];
    const phases = ['planning', 'execution', 'analysis', 'reporting', 'completion'];
    const statuses = ['active', 'on-hold', 'completed', 'cancelled'];
    
    const projectNames = [
      'Q1 2025 Strategic Research Initiative', 'Customer Experience Optimization Study', 'Market Expansion Research Project',
      'Competitive Intelligence Program', 'Digital Transformation Impact Study', 'Brand Positioning Research',
      'Product Development Research Phase II', 'Operational Excellence Research', 'Customer Retention Analysis Program',
      'Innovation Opportunity Assessment', 'Risk Management Research Initiative', 'Revenue Optimization Study'
    ];

    return Array.from({ length: 12 }, (_, index) => ({
      id: `project-${index + 1}`,
      name: projectNames[index] || `Research Project ${index + 1}`,
      type: projectTypes[Math.floor(Math.random() * projectTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      phase: phases[Math.floor(Math.random() * phases.length)],
      manager: ['Dr. Sarah Chen', 'Michael Rodriguez', 'Emma Thompson', 'David Kim'][Math.floor(Math.random() * 4)],
      description: `Comprehensive research project designed to deliver strategic insights and actionable recommendations for business growth.`,
      startDate: new Date(Date.now() - Math.random() * 120 * 24 * 60 * 60 * 1000).toISOString(),
      endDate: new Date(Date.now() + Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      budget: Math.floor(Math.random() * 200000) + 50000,
      spent: Math.floor(Math.random() * 100000) + 20000,
      progress: Math.floor(Math.random() * 100),
      teamSize: Math.floor(Math.random() * 12) + 4,
      queries: Math.floor(Math.random() * 8) + 3,
      tasks: Math.floor(Math.random() * 25) + 10,
      milestones: Math.floor(Math.random() * 8) + 4,
      deliverables: Math.floor(Math.random() * 6) + 3,
      stakeholders: Math.floor(Math.random() * 10) + 5,
      riskScore: Math.floor(Math.random() * 10) + 1,
      qualityScore: Math.floor(Math.random() * 30) + 70,
      objectives: [
        'Identify strategic opportunities for business growth',
        'Analyze competitive positioning and market dynamics',
        'Develop actionable recommendations for stakeholders',
        'Provide data-driven insights for decision-making'
      ],
      keyResults: [
        `${Math.floor(Math.random() * 40) + 60}% completion of research objectives`,
        `${Math.floor(Math.random() * 15) + 10} strategic recommendations delivered`,
        `${Math.floor(Math.random() * 20) + 80}% stakeholder satisfaction rating`,
        `$${(Math.random() * 500 + 200).toFixed(0)}K potential business impact identified`
      ],
      documents: Math.floor(Math.random() * 30) + 15,
      meetings: Math.floor(Math.random() * 20) + 8,
      presentations: Math.floor(Math.random() * 8) + 3,
      reports: Math.floor(Math.random() * 6) + 2
    }));
  }, []);

  const generateTemplates = useCallback(() => {
    const templateTypes = ['query-template', 'task-template', 'project-template', 'report-template'];
    const categories = ['market-research', 'competitive-analysis', 'customer-research', 'strategic-analysis'];
    
    const templateNames = [
      'Standard Market Research Query', 'Competitive Analysis Task Template', 'Customer Survey Project Template',
      'Strategic Analysis Report Format', 'Risk Assessment Query Template', 'Product Research Task Template',
      'Brand Analysis Project Template', 'Financial Research Query Template', 'Operational Analysis Template'
    ];

    return Array.from({ length: 9 }, (_, index) => ({
      id: `template-${index + 1}`,
      name: templateNames[index] || `Template ${index + 1}`,
      type: templateTypes[Math.floor(Math.random() * templateTypes.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      description: `Standardized template for ${categories[Math.floor(Math.random() * categories.length)]} research activities.`,
      createdAt: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      usage: Math.floor(Math.random() * 50) + 5,
      rating: (Math.random() * 2 + 3).toFixed(1),
      author: ['Research Team', 'Strategy Team', 'Analytics Team'][Math.floor(Math.random() * 3)],
      sections: Math.floor(Math.random() * 8) + 4,
      fields: Math.floor(Math.random() * 15) + 8,
      validation: Math.random() > 0.3,
      customizable: Math.random() > 0.2,
      tags: ['standard', 'validated', 'customizable', 'comprehensive'].slice(0, Math.floor(Math.random() * 3) + 2),
      complexity: ['simple', 'moderate', 'advanced'][Math.floor(Math.random() * 3)],
      estimatedTime: Math.floor(Math.random() * 60) + 30,
      successRate: Math.floor(Math.random() * 30) + 70,
      feedbackScore: (Math.random() * 2 + 3).toFixed(1)
    }));
  }, []);

  const generateWorkflows = useCallback(() => {
    const workflowTypes = ['research-approval', 'task-execution', 'quality-review', 'report-generation'];
    const statuses = ['active', 'paused', 'completed', 'error'];
    
    const workflowNames = [
      'Standard Research Query Approval', 'Task Assignment and Tracking', 'Quality Assurance Review Process',
      'Automated Report Generation', 'Stakeholder Notification Workflow', 'Data Validation Pipeline',
      'Project Milestone Tracking', 'Research Documentation Workflow'
    ];

    return Array.from({ length: 8 }, (_, index) => ({
      id: `workflow-${index + 1}`,
      name: workflowNames[index] || `Workflow ${index + 1}`,
      type: workflowTypes[Math.floor(Math.random() * workflowTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      description: `Automated workflow for ${workflowTypes[Math.floor(Math.random() * workflowTypes.length)]} process management.`,
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      lastRun: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      steps: Math.floor(Math.random() * 8) + 4,
      triggers: Math.floor(Math.random() * 5) + 2,
      executions: Math.floor(Math.random() * 100) + 10,
      successRate: Math.floor(Math.random() * 25) + 75,
      avgDuration: (Math.random() * 30 + 5).toFixed(1) + ' minutes',
      owner: ['System Administrator', 'Research Lead', 'Process Manager'][Math.floor(Math.random() * 3)],
      conditions: Math.floor(Math.random() * 6) + 3,
      actions: Math.floor(Math.random() * 8) + 4,
      notifications: Math.floor(Math.random() * 5) + 2,
      errorRate: (Math.random() * 5).toFixed(1) + '%',
      lastError: Math.random() > 0.7 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null,
      automation: Math.random() > 0.3,
      priority: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)]
    }));
  }, []);

  const generateAnalytics = useCallback(() => {
    return {
      queryMetrics: {
        totalQueries: 247,
        activeQueries: 89,
        completedThisMonth: 34,
        avgCompletionTime: '12.5 days',
        successRate: '87%',
        onTimeDelivery: '78%'
      },
      taskMetrics: {
        totalTasks: 1,
        activeTasks: 356,
        completedToday: 23,
        avgTaskDuration: '4.2 hours',
        taskEfficiency: '82%',
        overdueRate: '15%'
      },
      projectMetrics: {
        activeProjects: 28,
        completedProjects: 156,
        budgetUtilization: '73%',
        resourceEfficiency: '85%',
        stakeholderSatisfaction: '4.2/5',
        deliverySuccess: '91%'
      },
      performanceMetrics: {
        teamProductivity: '88%',
        qualityScore: '4.3/5',
        collaborationIndex: '76%',
        innovationScore: '82%',
        knowledgeSharing: '79%',
        processAdherence: '85%'
      }
    };
  }, []);

  const generateInsights = useCallback(() => {
    return [
      {
        id: 'insight-1',
        title: 'Query Completion Acceleration',
        description: 'Implementation of AI-assisted analysis tools has reduced average query completion time by 23% this quarter.',
        impact: 'high',
        category: 'efficiency',
        confidence: 89,
        recommendation: 'Expand AI tool usage to all research teams to maximize productivity gains.',
        metricsBefore: '16.2 days average',
        metricsAfter: '12.5 days average',
        savings: '$127K annually'
      },
      {
        id: 'insight-2',
        title: 'Task Assignment Optimization',
        description: 'Data shows that queries assigned based on expertise matching have 35% higher success rates.',
        impact: 'medium',
        category: 'quality',
        confidence: 92,
        recommendation: 'Implement automated skill-based task assignment system.',
        metricsBefore: '72% success rate',
        metricsAfter: '87% success rate',
        savings: 'Improved quality outcomes'
      },
      {
        id: 'insight-3',
        title: 'Cross-Departmental Collaboration',
        description: 'Projects involving multiple departments show 28% better stakeholder satisfaction ratings.',
        impact: 'high',
        category: 'collaboration',
        confidence: 85,
        recommendation: 'Encourage cross-functional research teams for complex queries.',
        metricsBefore: '3.8/5 satisfaction',
        metricsAfter: '4.2/5 satisfaction',
        savings: 'Enhanced strategic value'
      },
      {
        id: 'insight-4',
        title: 'Template Usage Benefits',
        description: 'Queries using standardized templates complete 40% faster with 25% fewer revisions required.',
        impact: 'medium',
        category: 'standardization',
        confidence: 94,
        recommendation: 'Develop comprehensive template library for all query types.',
        metricsBefore: '20.8 days average',
        metricsAfter: '12.5 days average',
        savings: '$89K in time savings'
      },
      {
        id: 'insight-5',
        title: 'Workflow Automation Impact',
        description: 'Automated workflows have reduced manual processing time by 60% while improving accuracy.',
        impact: 'high',
        category: 'automation',
        confidence: 91,
        recommendation: 'Expand automation to cover all repetitive research processes.',
        metricsBefore: '4.5 hours manual work',
        metricsAfter: '1.8 hours manual work',
        savings: '$156K in operational efficiency'
      }
    ];
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API calls with realistic delays
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        setQueries(generateQueries());
        setTasks(generateTasks());
        setProjects(generateProjects());
        setTemplates(generateTemplates());
        setWorkflows(generateWorkflows());
        setAnalytics(generateAnalytics());
        setInsights(generateInsights());
        
      } catch (error) {
        console.error('Error loading research query data:', error);
        setError('Failed to load research query data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateQueries, generateTasks, generateProjects, generateTemplates, generateWorkflows, generateAnalytics, generateInsights]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setQueries(generateQueries());
    setTasks(generateTasks());
    setProjects(generateProjects());
    setTemplates(generateTemplates());
    setWorkflows(generateWorkflows());
    setAnalytics(generateAnalytics());
    setInsights(generateInsights());
    
    setRefreshing(false);
  };

  // Filter and search logic
  const filteredQueries = queries.filter(query => {
    const matchesFilters = 
      (queryFilters.status === 'all' || query.status === queryFilters.status) &&
      (queryFilters.priority === 'all' || query.priority === queryFilters.priority) &&
      (queryFilters.type === 'all' || query.type === queryFilters.type) &&
      (queryFilters.department === 'all' || query.department === queryFilters.department) &&
      (queryFilters.complexity === 'all' || query.complexity === queryFilters.complexity) &&
      (queryFilters.assignee === 'all' || query.assignee === queryFilters.assignee);
    
    const matchesSearch = !searchQuery || 
      query.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      query.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      query.type.toLowerCase().includes(searchQuery.toLowerCase());
    
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
        case 'updated':
          aValue = new Date(a.updatedAt || a.lastUpdated);
          bValue = new Date(b.updatedAt || b.lastUpdated);
          break;
        case 'priority':
          const priorityOrder = { 'urgent': 4, 'high': 3, 'medium': 2, 'low': 1 };
          aValue = priorityOrder[a.priority] || 0;
          bValue = priorityOrder[b.priority] || 0;
          break;
        case 'progress':
          aValue = a.progress || 0;
          bValue = b.progress || 0;
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

  const sortedQueries = sortData([...filteredQueries]);

  const getStatusColor = (status) => {
    const colors = {
      active: '#17a2b8',
      completed: '#28a745',
      'on-hold': '#ffc107',
      cancelled: '#dc3545',
      pending: '#fd7e14',
      'in-review': '#6f42c1',
      'to-do': '#6c757d',
      'in-progress': '#17a2b8',
      blocked: '#dc3545',
      paused: '#fd7e14',
      error: '#dc3545'
    };
    return colors[status] || '#666';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      urgent: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[priority] || '#666';
  };

  const getComplexityColor = (complexity) => {
    const colors = {
      simple: '#28a745',
      moderate: '#ffc107',
      complex: '#fd7e14',
      advanced: '#dc3545'
    };
    return colors[complexity] || '#666';
  };

  const getRiskColor = (risk) => {
    const colors = {
      low: '#28a745',
      medium: '#ffc107',
      high: '#dc3545'
    };
    return colors[risk] || '#666';
  };

  const renderQueriesView = () => (
    <div className="queries-content">
      <div className="queries-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search research queries..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="sort-controls">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="created">Sort by Created</option>
              <option value="updated">Sort by Updated</option>
              <option value="priority">Sort by Priority</option>
              <option value="progress">Sort by Progress</option>
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
          <select value={queryFilters.status} onChange={(e) => setQueryFilters({...queryFilters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
            <option value="on-hold">On Hold</option>
            <option value="pending">Pending</option>
          </select>
          <select value={queryFilters.priority} onChange={(e) => setQueryFilters({...queryFilters, priority: e.target.value})}>
            <option value="all">All Priorities</option>
            <option value="urgent">Urgent</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select value={queryFilters.type} onChange={(e) => setQueryFilters({...queryFilters, type: e.target.value})}>
            <option value="all">All Types</option>
            <option value="data-analysis">Data Analysis</option>
            <option value="market-research">Market Research</option>
            <option value="competitive-intel">Competitive Intel</option>
            <option value="customer-insight">Customer Insight</option>
          </select>
          <select value={queryFilters.complexity} onChange={(e) => setQueryFilters({...queryFilters, complexity: e.target.value})}>
            <option value="all">All Complexities</option>
            <option value="simple">Simple</option>
            <option value="moderate">Moderate</option>
            <option value="complex">Complex</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div className="queries-grid">
        {sortedQueries.map(query => (
          <div key={query.id} className="query-card" onClick={() => {setSelectedQuery(query); setNewQueryModal(true);}}>
            <div className="query-header">
              <h3>{query.title}</h3>
              <div className="query-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(query.status) }}>
                  {query.status}
                </span>
                <span className="priority-badge" style={{ backgroundColor: getPriorityColor(query.priority) }}>
                  {query.priority}
                </span>
              </div>
            </div>
            <div className="query-meta">
              <span className="query-type">{query.type}</span>
              <span className="query-department">{query.department}</span>
              <span className="query-complexity" style={{ backgroundColor: getComplexityColor(query.complexity) }}>
                {query.complexity}
              </span>
            </div>
            <p className="query-description">{query.description}</p>
            <div className="query-progress">
              <div className="progress-info">
                <span className="progress-label">Progress:</span>
                <span className="progress-value">{query.progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${query.progress}%` }}></div>
              </div>
            </div>
            <div className="query-metrics">
              <div className="metric">
                <span className="metric-label">Confidence:</span>
                <span className="metric-value">{query.confidence}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Risk:</span>
                <span className="risk-badge" style={{ backgroundColor: getRiskColor(query.riskLevel) }}>
                  {query.riskLevel}
                </span>
              </div>
            </div>
            <div className="query-stats">
              <div className="stat">
                <i className="fas fa-tasks"></i>
                <span>{query.deliverables} deliverables</span>
              </div>
              <div className="stat">
                <i className="fas fa-users"></i>
                <span>{query.stakeholders} stakeholders</span>
              </div>
              <div className="stat">
                <i className="fas fa-database"></i>
                <span>{query.dataSources} sources</span>
              </div>
            </div>
            <div className="query-footer">
              <div className="query-assignee">
                <span>{query.assignee}</span>
              </div>
              <div className="query-dates">
                <span>Due: {new Date(query.dueDate).toLocaleDateString()}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTasksView = () => (
    <div className="tasks-content">
      <div className="tasks-header">
        <h3>Research Tasks</h3>
        <button className="new-task-btn" onClick={() => setTaskModal(true)}>
          <i className="fas fa-plus"></i>
          New Task
        </button>
      </div>
      <div className="tasks-grid">
        {tasks.map(task => (
          <div key={task.id} className="task-card" onClick={() => {setSelectedTask(task); setTaskModal(true);}}>
            <div className="task-header">
              <h4>{task.title}</h4>
              <div className="task-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(task.status) }}>
                  {task.status}
                </span>
                <span className="priority-badge" style={{ backgroundColor: getPriorityColor(task.priority) }}>
                  {task.priority}
                </span>
              </div>
            </div>
            <div className="task-meta">
              <span className="task-type">{task.type}</span>
              <span className="task-assignee">{task.assignee}</span>
            </div>
            <p className="task-description">{task.description}</p>
            <div className="task-progress">
              <div className="progress-info">
                <span>Progress: {task.progress}%</span>
                <span>Due: {new Date(task.dueDate).toLocaleDateString()}</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${task.progress}%` }}></div>
              </div>
            </div>
            <div className="task-checklist">
              <span>{task.checklist.filter(item => item.completed).length}/{task.checklist.length} completed</span>
              <div className="checklist-progress">
                <div 
                  className="checklist-fill" 
                  style={{ width: `${(task.checklist.filter(item => item.completed).length / task.checklist.length) * 100}%` }}
                ></div>
              </div>
            </div>
            <div className="task-stats">
              <div className="stat">
                <span className="stat-value">{task.actualHours}</span>
                <span className="stat-label">hrs worked</span>
              </div>
              <div className="stat">
                <span className="stat-value">{task.comments}</span>
                <span className="stat-label">comments</span>
              </div>
              <div className="stat">
                <span className="stat-value">{task.attachments}</span>
                <span className="stat-label">files</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderProjectsView = () => (
    <div className="projects-content">
      <div className="projects-header">
        <h3>Research Projects</h3>
        <button className="new-project-btn" onClick={() => setProjectModal(true)}>
          <i className="fas fa-plus"></i>
          New Project
        </button>
      </div>
      <div className="projects-grid">
        {projects.map(project => (
          <div key={project.id} className="project-card" onClick={() => setProjectModal(true)}>
            <div className="project-header">
              <h4>{project.name}</h4>
              <div className="project-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(project.status) }}>
                  {project.status}
                </span>
                <span className="phase-badge">{project.phase}</span>
              </div>
            </div>
            <div className="project-meta">
              <span className="project-type">{project.type}</span>
              <span className="project-manager">{project.manager}</span>
            </div>
            <p className="project-description">{project.description}</p>
            <div className="project-progress">
              <div className="progress-info">
                <span>Progress: {project.progress}%</span>
                <span>Budget: ${(project.spent / 1000).toFixed(0)}K/${(project.budget / 1000).toFixed(0)}K</span>
              </div>
              <div className="progress-bars">
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${project.progress}%` }}></div>
                </div>
                <div className="budget-bar">
                  <div className="budget-fill" style={{ width: `${(project.spent / project.budget) * 100}%` }}></div>
                </div>
              </div>
            </div>
            <div className="project-stats">
              <div className="stat">
                <span className="stat-value">{project.queries}</span>
                <span className="stat-label">queries</span>
              </div>
              <div className="stat">
                <span className="stat-value">{project.tasks}</span>
                <span className="stat-label">tasks</span>
              </div>
              <div className="stat">
                <span className="stat-value">{project.teamSize}</span>
                <span className="stat-label">team</span>
              </div>
              <div className="stat">
                <span className="stat-value">{project.deliverables}</span>
                <span className="stat-label">deliverables</span>
              </div>
            </div>
            <div className="project-timeline">
              <span>Started: {new Date(project.startDate).toLocaleDateString()}</span>
              <span>Ends: {new Date(project.endDate).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTemplatesView = () => (
    <div className="templates-content">
      <div className="templates-header">
        <h3>Query Templates</h3>
        <button className="new-template-btn">
          <i className="fas fa-plus"></i>
          Create Template
        </button>
      </div>
      <div className="templates-grid">
        {templates.map(template => (
          <div key={template.id} className="template-card">
            <div className="template-header">
              <h4>{template.name}</h4>
              <div className="template-badges">
                <span className="type-badge">{template.type}</span>
                <span className="category-badge">{template.category}</span>
              </div>
            </div>
            <p className="template-description">{template.description}</p>
            <div className="template-stats">
              <div className="stat">
                <span className="stat-value">{template.usage}</span>
                <span className="stat-label">uses</span>
              </div>
              <div className="stat">
                <span className="stat-value">{template.rating}</span>
                <span className="stat-label">rating</span>
              </div>
              <div className="stat">
                <span className="stat-value">{template.sections}</span>
                <span className="stat-label">sections</span>
              </div>
              <div className="stat">
                <span className="stat-value">{template.estimatedTime}m</span>
                <span className="stat-label">est. time</span>
              </div>
            </div>
            <div className="template-features">
              {template.customizable && <span className="feature-badge">Customizable</span>}
              {template.validation && <span className="feature-badge">Validated</span>}
              <span className="complexity-badge" style={{ backgroundColor: getComplexityColor(template.complexity) }}>
                {template.complexity}
              </span>
            </div>
            <div className="template-footer">
              <span className="template-author">{template.author}</span>
              <div className="template-actions">
                <button className="use-btn">Use Template</button>
                <button className="edit-btn">Edit</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderWorkflowsView = () => (
    <div className="workflows-content">
      <div className="workflows-header">
        <h3>Research Workflows</h3>
        <button className="new-workflow-btn" onClick={() => setWorkflowModal(true)}>
          <i className="fas fa-plus"></i>
          Create Workflow
        </button>
      </div>
      <div className="workflows-grid">
        {workflows.map(workflow => (
          <div key={workflow.id} className="workflow-card" onClick={() => setWorkflowModal(true)}>
            <div className="workflow-header">
              <h4>{workflow.name}</h4>
              <div className="workflow-badges">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(workflow.status) }}>
                  {workflow.status}
                </span>
                <span className="type-badge">{workflow.type}</span>
              </div>
            </div>
            <p className="workflow-description">{workflow.description}</p>
            <div className="workflow-metrics">
              <div className="metric">
                <span className="metric-label">Success Rate:</span>
                <span className="metric-value">{workflow.successRate}%</span>
                <div className="metric-bar">
                  <div className="metric-fill" style={{ width: `${workflow.successRate}%` }}></div>
                </div>
              </div>
            </div>
            <div className="workflow-stats">
              <div className="stat">
                <span className="stat-value">{workflow.steps}</span>
                <span className="stat-label">steps</span>
              </div>
              <div className="stat">
                <span className="stat-value">{workflow.executions}</span>
                <span className="stat-label">runs</span>
              </div>
              <div className="stat">
                <span className="stat-value">{workflow.avgDuration}</span>
                <span className="stat-label">avg time</span>
              </div>
              <div className="stat">
                <span className="stat-value">{workflow.errorRate}</span>
                <span className="stat-label">error rate</span>
              </div>
            </div>
            <div className="workflow-footer">
              <span className="workflow-owner">{workflow.owner}</span>
              <span className="workflow-updated">Last run: {new Date(workflow.lastRun).toLocaleDateString()}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="analytics-content">
      <div className="analytics-overview">
        <div className="metrics-grid">
          <div className="metric-section">
            <h3>Query Metrics</h3>
            <div className="metric-cards">
              {Object.entries(analytics.queryMetrics).map(([key, value]) => (
                <div key={key} className="metric-card">
                  <span className="metric-label">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="metric-section">
            <h3>Task Metrics</h3>
            <div className="metric-cards">
              {Object.entries(analytics.taskMetrics).map(([key, value]) => (
                <div key={key} className="metric-card">
                  <span className="metric-label">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="metric-section">
            <h3>Project Metrics</h3>
            <div className="metric-cards">
              {Object.entries(analytics.projectMetrics).map(([key, value]) => (
                <div key={key} className="metric-card">
                  <span className="metric-label">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="metric-section">
            <h3>Performance Metrics</h3>
            <div className="metric-cards">
              {Object.entries(analytics.performanceMetrics).map(([key, value]) => (
                <div key={key} className="metric-card">
                  <span className="metric-label">{key.replace(/([A-Z])/g, ' $1').toLowerCase()}</span>
                  <span className="metric-value">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderInsightsView = () => (
    <div className="insights-content">
      <div className="insights-header">
        <h3>AI-Powered Insights</h3>
        <span className="insights-count">{insights.length} insights available</span>
      </div>
      <div className="insights-grid">
        {insights.map(insight => (
          <div key={insight.id} className="insight-card">
            <div className="insight-header">
              <h4>{insight.title}</h4>
              <div className="insight-badges">
                <span className={`impact-badge ${insight.impact}`}>{insight.impact} impact</span>
                <span className="category-badge">{insight.category}</span>
              </div>
            </div>
            <p className="insight-description">{insight.description}</p>
            <div className="insight-confidence">
              <span className="confidence-label">Confidence:</span>
              <span className="confidence-value">{insight.confidence}%</span>
              <div className="confidence-bar">
                <div className="confidence-fill" style={{ width: `${insight.confidence}%` }}></div>
              </div>
            </div>
            <div className="insight-metrics">
              <div className="before-after">
                <div className="metric-comparison">
                  <span className="before">Before: {insight.metricsBefore}</span>
                  <span className="after">After: {insight.metricsAfter}</span>
                </div>
                <div className="savings">{insight.savings}</div>
              </div>
            </div>
            <div className="insight-recommendation">
              <h5>Recommendation:</h5>
              <p>{insight.recommendation}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'queries':
        return renderQueriesView();
      case 'tasks':
        return renderTasksView();
      case 'projects':
        return renderProjectsView();
      case 'templates':
        return renderTemplatesView();
      case 'workflows':
        return renderWorkflowsView();
      case 'analytics':
        return renderAnalyticsView();
      case 'insights':
        return renderInsightsView();
      default:
        return renderQueriesView();
    }
  };

  if (loading) {
    return (
      <div className="research-query-management loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading research query management...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="research-query-management error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="research-query-management">
      <div className="research-header">
        <div className="header-left">
          <h1>Research Query & Task Management</h1>
          <p>Comprehensive research coordination with AI-powered insights and workflow automation</p>
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
          <button className="new-query-btn" onClick={() => setNewQueryModal(true)}>
            <i className="fas fa-plus"></i>
            New Query
          </button>
        </div>
      </div>

      <div className="research-navigation">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeView === 'queries' ? 'active' : ''}`}
            onClick={() => setActiveView('queries')}
          >
            <i className="fas fa-search"></i>
            Queries
            <span className="count">{queries.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveView('tasks')}
          >
            <i className="fas fa-tasks"></i>
            Tasks
            <span className="count">{tasks.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'projects' ? 'active' : ''}`}
            onClick={() => setActiveView('projects')}
          >
            <i className="fas fa-project-diagram"></i>
            Projects
            <span className="count">{projects.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveView('templates')}
          >
            <i className="fas fa-copy"></i>
            Templates
            <span className="count">{templates.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'workflows' ? 'active' : ''}`}
            onClick={() => setActiveView('workflows')}
          >
            <i className="fas fa-stream"></i>
            Workflows
            <span className="count">{workflows.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveView('analytics')}
          >
            <i className="fas fa-chart-bar"></i>
            Analytics
          </button>
          <button 
            className={`nav-tab ${activeView === 'insights' ? 'active' : ''}`}
            onClick={() => setActiveView('insights')}
          >
            <i className="fas fa-lightbulb"></i>
            Insights
            <span className="count">{insights.length}</span>
          </button>
        </div>
      </div>

      <div className="research-main">
        {renderContent()}
      </div>

      {/* Modals would be rendered here */}
      {newQueryModal && (
        <div className="modal-overlay" onClick={() => setNewQueryModal(false)}>
          <div className="query-modal" onClick={(e) => e.stopPropagation()}>
            {/* Detailed query modal content */}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchQueryManagement;
