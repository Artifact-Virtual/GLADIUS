import React, { useState, useEffect, useCallback } from 'react';

const TaskDelegationTracking = () => {
  const [activeView, setActiveView] = useState('overview');
  const [tasks, setTasks] = useState([]);
  const [delegations, setDelegations] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [selectedTask, setSelectedTask] = useState(null);
  const [selectedDelegation, setSelectedDelegation] = useState(null);
  const [taskModal, setTaskModal] = useState(false);
  const [delegationModal, setDelegationModal] = useState(false);
  const [workflowModal, setWorkflowModal] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    type: 'all',
    agent: 'all',
    complexity: 'all',
    timeRange: 'all'
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('priority');
  const [sortOrder, setSortOrder] = useState('desc');

  // Generate mock task delegation data
  const generateTasks = useCallback(() => {
    const taskTypes = ['analysis', 'processing', 'communication', 'optimization', 'monitoring', 'reporting', 'automation', 'integration'];
    const statuses = ['assigned', 'in-progress', 'completed', 'failed', 'paused', 'queued', 'delegated', 'reassigned'];
    const priorities = ['critical', 'high', 'medium', 'low'];
    const complexities = ['simple', 'moderate', 'complex', 'advanced'];
    
    const taskTitles = [
      'Market Data Analysis Pipeline', 'Customer Behavior Processing', 'Financial Report Generation',
      'System Performance Optimization', 'Real-time Monitoring Setup', 'Communication Protocol Update',
      'Predictive Analytics Model', 'Data Synchronization Task', 'Workflow Automation Setup',
      'Quality Assurance Validation', 'Security Audit Process', 'Resource Optimization Task',
      'Trend Analysis Report', 'Machine Learning Training', 'Integration Testing Suite',
      'Backup Verification Process', 'Load Balancing Configuration', 'API Performance Testing',
      'Database Migration Task', 'Content Processing Pipeline', 'User Behavior Analysis',
      'Risk Assessment Model', 'Compliance Check Process', 'Performance Benchmarking'
    ];

    return Array.from({ length: 24 }, (_, index) => ({
      id: `task-${index + 1}`,
      title: taskTitles[index] || `Task ${index + 1}`,
      type: taskTypes[Math.floor(Math.random() * taskTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      complexity: complexities[Math.floor(Math.random() * complexities.length)],
      assignedAgent: `agent-${Math.floor(Math.random() * 20) + 1}`,
      delegatedBy: `agent-${Math.floor(Math.random() * 5) + 1}`,
      delegatedTo: `agent-${Math.floor(Math.random() * 20) + 1}`,
      originalAssignee: `agent-${Math.floor(Math.random() * 20) + 1}`,
      description: `Automated task delegation for ${taskTypes[Math.floor(Math.random() * taskTypes.length)]} with enterprise coordination requirements.`,
      createdAt: new Date(Date.now() - Math.random() * 72 * 60 * 60 * 1000).toISOString(),
      assignedAt: new Date(Date.now() - Math.random() * 48 * 60 * 60 * 1000).toISOString(),
      startedAt: Math.random() > 0.3 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null,
      estimatedCompletion: new Date(Date.now() + Math.random() * 48 * 60 * 60 * 1000).toISOString(),
      actualCompletion: Math.random() > 0.6 ? new Date(Date.now() - Math.random() * 12 * 60 * 60 * 1000).toISOString() : null,
      progress: Math.floor(Math.random() * 100),
      delegationReason: [
        'Agent overloaded',
        'Skill specialization match',
        'Geographic optimization',
        'Load balancing',
        'Agent unavailable',
        'Performance optimization',
        'Resource constraints',
        'Workflow efficiency'
      ][Math.floor(Math.random() * 8)],
      resourceRequirements: {
        cpu: Math.floor(Math.random() * 80) + 10,
        memory: Math.floor(Math.random() * 70) + 20,
        network: Math.floor(Math.random() * 50) + 5,
        storage: Math.floor(Math.random() * 100) + 10,
        gpu: Math.random() > 0.7 ? Math.floor(Math.random() * 50) + 10 : 0
      },
      dependencies: Array.from({ length: Math.floor(Math.random() * 4) }, (_, i) => `task-${Math.floor(Math.random() * 24) + 1}`),
      dependents: Array.from({ length: Math.floor(Math.random() * 3) }, (_, i) => `task-${Math.floor(Math.random() * 24) + 1}`),
      retryCount: Math.floor(Math.random() * 3),
      delegationCount: Math.floor(Math.random() * 3),
      executionTime: (Math.random() * 1800 + 300).toFixed(0) + 's',
      waitingTime: (Math.random() * 600 + 60).toFixed(0) + 's',
      queuePosition: Math.floor(Math.random() * 10) + 1,
      successProbability: Math.floor(Math.random() * 30) + 70,
      riskLevel: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
      automationLevel: Math.floor(Math.random() * 100),
      skillRequirements: [
        'Data Analysis',
        'Machine Learning',
        'API Integration',
        'Database Management',
        'Real-time Processing',
        'Natural Language Processing'
      ].slice(0, Math.floor(Math.random() * 4) + 2),
      performanceMetrics: {
        accuracy: Math.floor(Math.random() * 20) + 80,
        efficiency: Math.floor(Math.random() * 25) + 75,
        throughput: (Math.random() * 100 + 10).toFixed(0) + '/min',
        errorRate: (Math.random() * 5).toFixed(2) + '%'
      },
      tags: ['automated', 'delegated', 'enterprise', 'coordination'].slice(0, Math.floor(Math.random() * 3) + 1),
      collaborators: Math.floor(Math.random() * 5) + 1,
      notifications: Math.floor(Math.random() * 15) + 5,
      checkpoints: Math.floor(Math.random() * 8) + 2,
      milestones: Math.floor(Math.random() * 5) + 1,
      escalationLevel: Math.floor(Math.random() * 4),
      delegationHistory: Array.from({ length: Math.floor(Math.random() * 3) + 1 }, (_, i) => ({
        fromAgent: `agent-${Math.floor(Math.random() * 20) + 1}`,
        toAgent: `agent-${Math.floor(Math.random() * 20) + 1}`,
        reason: ['Load balancing', 'Skill match', 'Availability', 'Performance'][Math.floor(Math.random() * 4)],
        timestamp: new Date(Date.now() - Math.random() * 48 * 60 * 60 * 1000).toISOString(),
        success: Math.random() > 0.2
      }))
    }));
  }, []);

  const generateDelegations = useCallback(() => {
    const delegationTypes = ['manual', 'automatic', 'rule-based', 'ai-driven', 'load-balanced', 'skill-matched'];
    const statuses = ['pending', 'accepted', 'rejected', 'completed', 'failed', 'expired'];
    const strategies = ['round-robin', 'weighted', 'priority-based', 'skill-matching', 'load-balancing', 'geographical'];

    return Array.from({ length: 18 }, (_, index) => ({
      id: `delegation-${index + 1}`,
      taskId: `task-${Math.floor(Math.random() * 24) + 1}`,
      type: delegationTypes[Math.floor(Math.random() * delegationTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      strategy: strategies[Math.floor(Math.random() * strategies.length)],
      fromAgent: `agent-${Math.floor(Math.random() * 20) + 1}`,
      toAgent: `agent-${Math.floor(Math.random() * 20) + 1}`,
      initiatedBy: ['System', 'Agent', 'User', 'Scheduler'][Math.floor(Math.random() * 4)],
      initiatedAt: new Date(Date.now() - Math.random() * 48 * 60 * 60 * 1000).toISOString(),
      acceptedAt: Math.random() > 0.3 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null,
      completedAt: Math.random() > 0.5 ? new Date(Date.now() - Math.random() * 12 * 60 * 60 * 1000).toISOString() : null,
      reason: [
        'Agent capacity exceeded',
        'Skill specialization required',
        'Geographic optimization',
        'Load distribution',
        'Performance improvement',
        'Resource availability',
        'Deadline optimization',
        'Quality enhancement'
      ][Math.floor(Math.random() * 8)],
      confidence: Math.floor(Math.random() * 30) + 70,
      priority: ['critical', 'high', 'medium', 'low'][Math.floor(Math.random() * 4)],
      expectedDuration: (Math.random() * 1800 + 600).toFixed(0) + 's',
      actualDuration: Math.random() > 0.4 ? (Math.random() * 2000 + 500).toFixed(0) + 's' : null,
      resourceTransfer: {
        cpu: Math.floor(Math.random() * 50) + 10,
        memory: Math.floor(Math.random() * 40) + 20,
        network: Math.floor(Math.random() * 30) + 5,
        storage: Math.floor(Math.random() * 60) + 10
      },
      skillMatch: Math.floor(Math.random() * 30) + 70,
      workloadFit: Math.floor(Math.random() * 40) + 60,
      successProbability: Math.floor(Math.random() * 25) + 75,
      riskAssessment: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
      alternatives: Math.floor(Math.random() * 5) + 1,
      fallbackPlan: Math.random() > 0.2,
      monitoringLevel: ['basic', 'standard', 'intensive', 'real-time'][Math.floor(Math.random() * 4)],
      notifications: Math.floor(Math.random() * 10) + 3,
      escalationPath: [
        `agent-${Math.floor(Math.random() * 5) + 1}`,
        'supervisor-1',
        'coordinator-1'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      metrics: {
        delegationTime: (Math.random() * 300 + 50).toFixed(0) + 'ms',
        acceptanceRate: Math.floor(Math.random() * 30) + 70,
        completionRate: Math.floor(Math.random() * 25) + 75,
        qualityScore: Math.floor(Math.random() * 20) + 80
      },
      constraints: [
        'Time limit: 2 hours',
        'Memory limit: 8GB',
        'CPU cores: 4',
        'Network: High bandwidth'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      approval: {
        required: Math.random() > 0.6,
        approver: Math.random() > 0.3 ? 'supervisor-1' : null,
        approvedAt: Math.random() > 0.5 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null
      }
    }));
  }, []);

  const generateWorkflows = useCallback(() => {
    const workflowTypes = ['sequential', 'parallel', 'conditional', 'loop', 'hybrid'];
    const statuses = ['active', 'paused', 'completed', 'failed', 'scheduled'];

    return Array.from({ length: 12 }, (_, index) => ({
      id: `workflow-${index + 1}`,
      name: `Delegation Workflow ${index + 1}`,
      type: workflowTypes[Math.floor(Math.random() * workflowTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      description: `Automated delegation workflow for enterprise task coordination and distribution.`,
      tasks: Array.from({ length: Math.floor(Math.random() * 8) + 3 }, (_, i) => `task-${Math.floor(Math.random() * 24) + 1}`),
      delegations: Array.from({ length: Math.floor(Math.random() * 6) + 2 }, (_, i) => `delegation-${Math.floor(Math.random() * 18) + 1}`),
      startedAt: new Date(Date.now() - Math.random() * 72 * 60 * 60 * 1000).toISOString(),
      estimatedCompletion: new Date(Date.now() + Math.random() * 48 * 60 * 60 * 1000).toISOString(),
      actualCompletion: Math.random() > 0.6 ? new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString() : null,
      progress: Math.floor(Math.random() * 100),
      totalSteps: Math.floor(Math.random() * 15) + 5,
      completedSteps: Math.floor(Math.random() * 10) + 2,
      failedSteps: Math.floor(Math.random() * 3),
      skippedSteps: Math.floor(Math.random() * 2),
      parallelBranches: Math.floor(Math.random() * 5) + 1,
      activeBranches: Math.floor(Math.random() * 3) + 1,
      successRate: Math.floor(Math.random() * 25) + 75,
      efficiency: Math.floor(Math.random() * 30) + 70,
      resourceUtilization: Math.floor(Math.random() * 40) + 60,
      bottlenecks: Math.floor(Math.random() * 3),
      optimizations: Math.floor(Math.random() * 5) + 2,
      triggers: [
        'Time-based',
        'Event-driven',
        'Condition-based',
        'Manual'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      rules: [
        'Load balancing rule',
        'Skill matching rule',
        'Priority routing rule',
        'SLA compliance rule'
      ].slice(0, Math.floor(Math.random() * 3) + 1),
      agents: Array.from({ length: Math.floor(Math.random() * 8) + 3 }, (_, i) => `agent-${Math.floor(Math.random() * 20) + 1}`),
      metrics: {
        averageExecutionTime: (Math.random() * 3600 + 1200).toFixed(0) + 's',
        throughput: (Math.random() * 50 + 10).toFixed(0) + '/hour',
        errorRate: (Math.random() * 8).toFixed(2) + '%',
        scalability: Math.floor(Math.random() * 30) + 70
      }
    }));
  }, []);

  const generateAgents = useCallback(() => {
    const agentTypes = ['coordinator', 'processor', 'analyzer', 'monitor'];
    const statuses = ['active', 'idle', 'busy', 'offline'];

    return Array.from({ length: 20 }, (_, index) => ({
      id: `agent-${index + 1}`,
      name: `Agent ${index + 1}`,
      type: agentTypes[Math.floor(Math.random() * agentTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      currentTasks: Math.floor(Math.random() * 10) + 1,
      delegatedTasks: Math.floor(Math.random() * 15) + 5,
      receivedTasks: Math.floor(Math.random() * 12) + 3,
      completionRate: Math.floor(Math.random() * 20) + 80,
      delegationEfficiency: Math.floor(Math.random() * 25) + 75,
      workloadCapacity: Math.floor(Math.random() * 100) + 50,
      currentWorkload: Math.floor(Math.random() * 80) + 10
    }));
  }, []);

  // Load data
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        await new Promise(resolve => setTimeout(resolve, 1200));
        
        setTasks(generateTasks());
        setDelegations(generateDelegations());
        setWorkflows(generateWorkflows());
        setAgents(generateAgents());
        
      } catch (error) {
        console.error('Error loading delegation data:', error);
        setError('Failed to load delegation tracking data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateTasks, generateDelegations, generateWorkflows, generateAgents]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setTasks(generateTasks());
    setDelegations(generateDelegations());
    setWorkflows(generateWorkflows());
    setAgents(generateAgents());
    
    setRefreshing(false);
  };

  // Filter and search logic
  const filteredTasks = tasks.filter(task => {
    const matchesFilters = 
      (filters.status === 'all' || task.status === filters.status) &&
      (filters.priority === 'all' || task.priority === filters.priority) &&
      (filters.type === 'all' || task.type === filters.type) &&
      (filters.complexity === 'all' || task.complexity === filters.complexity) &&
      (filters.agent === 'all' || task.assignedAgent === filters.agent);
    
    const matchesSearch = !searchQuery || 
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.assignedAgent.toLowerCase().includes(searchQuery.toLowerCase());
    
    return matchesFilters && matchesSearch;
  });

  const sortData = (data) => {
    return data.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { 'critical': 4, 'high': 3, 'medium': 2, 'low': 1 };
          aValue = priorityOrder[a.priority] || 0;
          bValue = priorityOrder[b.priority] || 0;
          break;
        case 'status':
          aValue = a.status;
          bValue = b.status;
          break;
        case 'progress':
          aValue = a.progress || 0;
          bValue = b.progress || 0;
          break;
        case 'created':
          aValue = new Date(a.createdAt).getTime();
          bValue = new Date(b.createdAt).getTime();
          break;
        case 'title':
          aValue = a.title;
          bValue = b.title;
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

  const sortedTasks = sortData([...filteredTasks]);

  const getStatusColor = (status) => {
    const colors = {
      assigned: '#17a2b8',
      'in-progress': '#ffc107',
      completed: '#28a745',
      failed: '#dc3545',
      paused: '#fd7e14',
      queued: '#6c757d',
      delegated: '#6f42c1',
      reassigned: '#e83e8c',
      pending: '#6c757d',
      accepted: '#28a745',
      rejected: '#dc3545',
      expired: '#6c757d',
      active: '#28a745',
      scheduled: '#17a2b8'
    };
    return colors[status] || '#666';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      critical: '#dc3545',
      high: '#fd7e14',
      medium: '#ffc107',
      low: '#28a745'
    };
    return colors[priority] || '#666';
  };

  const getRiskColor = (risk) => {
    const colors = {
      low: '#28a745',
      medium: '#ffc107',
      high: '#fd7e14',
      critical: '#dc3545'
    };
    return colors[risk] || '#666';
  };

  const renderOverviewView = () => (
    <div className="overview-content">
      <div className="delegation-overview">
        <div className="overview-metrics">
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-tasks"></i>
            </div>
            <div className="metric-content">
              <h3>{tasks.length}</h3>
              <p>Total Tasks</p>
              <span className="metric-detail">
                {tasks.filter(t => t.status === 'delegated').length} delegated
              </span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-share-alt"></i>
            </div>
            <div className="metric-content">
              <h3>{delegations.length}</h3>
              <p>Delegations</p>
              <span className="metric-detail">
                {delegations.filter(d => d.status === 'accepted').length} accepted
              </span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-project-diagram"></i>
            </div>
            <div className="metric-content">
              <h3>{workflows.length}</h3>
              <p>Workflows</p>
              <span className="metric-detail">
                {workflows.filter(w => w.status === 'active').length} active
              </span>
            </div>
          </div>
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="metric-content">
              <h3>{((delegations.filter(d => d.status === 'completed').length / delegations.length) * 100).toFixed(1)}%</h3>
              <p>Success Rate</p>
              <span className="metric-detail">
                {delegations.filter(d => d.status === 'completed').length} completed
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="delegation-analytics">
        <div className="analytics-section">
          <h3>Delegation Status Distribution</h3>
          <div className="status-chart">
            <div className="status-bars">
              {['pending', 'accepted', 'completed', 'failed', 'rejected'].map(status => {
                const count = delegations.filter(d => d.status === status).length;
                const percentage = delegations.length > 0 ? (count / delegations.length) * 100 : 0;
                return (
                  <div key={status} className="status-bar">
                    <div className="bar-info">
                      <span className="status-name">{status}</span>
                      <span className="status-count">{count}</span>
                    </div>
                    <div className="bar-container">
                      <div 
                        className="bar-fill" 
                        style={{ 
                          width: `${percentage}%`,
                          backgroundColor: getStatusColor(status)
                        }}
                      ></div>
                    </div>
                    <span className="bar-percentage">{percentage.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="analytics-section">
          <h3>Task Complexity Distribution</h3>
          <div className="complexity-chart">
            <div className="complexity-items">
              {['simple', 'moderate', 'complex', 'advanced'].map(complexity => {
                const count = tasks.filter(t => t.complexity === complexity).length;
                const percentage = tasks.length > 0 ? (count / tasks.length) * 100 : 0;
                return (
                  <div key={complexity} className="complexity-item">
                    <div className="complexity-header">
                      <span className="complexity-name">{complexity}</span>
                      <span className="complexity-count">{count}</span>
                    </div>
                    <div className="complexity-bar">
                      <div 
                        className="complexity-fill"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="complexity-percentage">{percentage.toFixed(1)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>

      <div className="delegation-trends">
        <div className="trends-section">
          <h3>Delegation Performance Metrics</h3>
          <div className="performance-grid">
            <div className="performance-metric">
              <span className="metric-label">Average Delegation Time:</span>
              <span className="metric-value">
                {(delegations.reduce((sum, d) => sum + parseInt(d.metrics?.delegationTime || 0), 0) / delegations.length || 0).toFixed(0)}ms
              </span>
            </div>
            <div className="performance-metric">
              <span className="metric-label">Average Acceptance Rate:</span>
              <span className="metric-value">
                {(delegations.reduce((sum, d) => sum + (d.metrics?.acceptanceRate || 0), 0) / delegations.length || 0).toFixed(1)}%
              </span>
            </div>
            <div className="performance-metric">
              <span className="metric-label">Average Quality Score:</span>
              <span className="metric-value">
                {(delegations.reduce((sum, d) => sum + (d.metrics?.qualityScore || 0), 0) / delegations.length || 0).toFixed(1)}
              </span>
            </div>
            <div className="performance-metric">
              <span className="metric-label">Average Skill Match:</span>
              <span className="metric-value">
                {(delegations.reduce((sum, d) => sum + (d.skillMatch || 0), 0) / delegations.length || 0).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="recent-delegations">
        <h3>Recent Delegation Activity</h3>
        <div className="delegation-feed">
          {delegations.slice(0, 8).map(delegation => (
            <div key={delegation.id} className="delegation-item" onClick={() => {setSelectedDelegation(delegation); setDelegationModal(true);}}>
              <div className="delegation-icon">
                <i className="fas fa-exchange-alt"></i>
              </div>
              <div className="delegation-content">
                <div className="delegation-header">
                  <span className="delegation-type">{delegation.type}</span>
                  <span className="delegation-time">{new Date(delegation.initiatedAt).toLocaleTimeString()}</span>
                </div>
                <div className="delegation-details">
                  <span className="from-agent">From: {delegation.fromAgent}</span>
                  <span className="to-agent">To: {delegation.toAgent}</span>
                  <span className="reason">{delegation.reason}</span>
                </div>
                <div className="delegation-status">
                  <span 
                    className="status-indicator" 
                    style={{ backgroundColor: getStatusColor(delegation.status) }}
                  ></span>
                  <span className="status-text">{delegation.status}</span>
                  <span className="confidence">Confidence: {delegation.confidence}%</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderTasksView = () => (
    <div className="tasks-content">
      <div className="tasks-controls">
        <div className="search-section">
          <div className="search-input">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
          <div className="sort-controls">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="priority">Sort by Priority</option>
              <option value="status">Sort by Status</option>
              <option value="progress">Sort by Progress</option>
              <option value="created">Sort by Created Date</option>
              <option value="title">Sort by Title</option>
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
          <select value={filters.status} onChange={(e) => setFilters({...filters, status: e.target.value})}>
            <option value="all">All Statuses</option>
            <option value="assigned">Assigned</option>
            <option value="in-progress">In Progress</option>
            <option value="delegated">Delegated</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
          </select>
          <select value={filters.priority} onChange={(e) => setFilters({...filters, priority: e.target.value})}>
            <option value="all">All Priorities</option>
            <option value="critical">Critical</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
          <select value={filters.complexity} onChange={(e) => setFilters({...filters, complexity: e.target.value})}>
            <option value="all">All Complexities</option>
            <option value="simple">Simple</option>
            <option value="moderate">Moderate</option>
            <option value="complex">Complex</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>
      </div>

      <div className="tasks-grid">
        {sortedTasks.map(task => (
          <div key={task.id} className="task-card" onClick={() => {setSelectedTask(task); setTaskModal(true);}}>
            <div className="task-header">
              <div className="task-info">
                <h3>{task.title}</h3>
                <span className="task-id">{task.id}</span>
              </div>
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
              <span className="task-complexity">{task.complexity}</span>
              <span className="delegation-count">{task.delegationCount} delegations</span>
            </div>

            <div className="task-delegation-info">
              <div className="delegation-flow">
                <span className="from-agent">{task.originalAssignee}</span>
                <i className="fas fa-arrow-right"></i>
                <span className="current-agent">{task.assignedAgent}</span>
              </div>
              <div className="delegation-reason">{task.delegationReason}</div>
            </div>

            <div className="task-progress">
              <div className="progress-header">
                <span className="progress-label">Progress</span>
                <span className="progress-value">{task.progress}%</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill" 
                  style={{ width: `${task.progress}%` }}
                ></div>
              </div>
            </div>

            <div className="task-metrics">
              <div className="metric-row">
                <div className="metric">
                  <span className="metric-label">Success Probability:</span>
                  <span className="metric-value">{task.successProbability}%</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Risk Level:</span>
                  <span className="metric-value risk" style={{ color: getRiskColor(task.riskLevel) }}>
                    {task.riskLevel}
                  </span>
                </div>
              </div>
              <div className="metric-row">
                <div className="metric">
                  <span className="metric-label">Dependencies:</span>
                  <span className="metric-value">{task.dependencies.length}</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Collaborators:</span>
                  <span className="metric-value">{task.collaborators}</span>
                </div>
              </div>
            </div>

            <div className="task-footer">
              <div className="task-times">
                <span className="created-time">
                  Created: {new Date(task.createdAt).toLocaleDateString()}
                </span>
                <span className="execution-time">
                  Est. Time: {task.executionTime}
                </span>
              </div>
              <div className="task-skills">
                <span className="skills-count">{task.skillRequirements.length} skills required</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderDelegationsView = () => (
    <div className="delegations-content">
      <div className="delegations-table">
        <div className="table-header">
          <div className="header-cell">ID</div>
          <div className="header-cell">Type</div>
          <div className="header-cell">Task</div>
          <div className="header-cell">From → To</div>
          <div className="header-cell">Status</div>
          <div className="header-cell">Strategy</div>
          <div className="header-cell">Confidence</div>
          <div className="header-cell">Duration</div>
          <div className="header-cell">Actions</div>
        </div>
        <div className="table-body">
          {delegations.map(delegation => (
            <div key={delegation.id} className="table-row">
              <div className="table-cell">{delegation.id}</div>
              <div className="table-cell">
                <span className="delegation-type">{delegation.type}</span>
              </div>
              <div className="table-cell">
                <span className="task-link">{delegation.taskId}</span>
              </div>
              <div className="table-cell">
                <div className="agent-flow">
                  <span className="from-agent">{delegation.fromAgent}</span>
                  <i className="fas fa-arrow-right"></i>
                  <span className="to-agent">{delegation.toAgent}</span>
                </div>
              </div>
              <div className="table-cell">
                <span 
                  className="status-badge"
                  style={{ backgroundColor: getStatusColor(delegation.status) }}
                >
                  {delegation.status}
                </span>
              </div>
              <div className="table-cell">
                <span className="strategy-tag">{delegation.strategy}</span>
              </div>
              <div className="table-cell">
                <div className="confidence-meter">
                  <span className="confidence-value">{delegation.confidence}%</span>
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${delegation.confidence}%` }}
                    ></div>
                  </div>
                </div>
              </div>
              <div className="table-cell">
                <span className="duration-value">
                  {delegation.actualDuration || delegation.expectedDuration}
                </span>
              </div>
              <div className="table-cell">
                <button 
                  className="action-btn"
                  onClick={() => {setSelectedDelegation(delegation); setDelegationModal(true);}}
                >
                  <i className="fas fa-eye"></i>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderWorkflowsView = () => (
    <div className="workflows-content">
      <div className="workflows-grid">
        {workflows.map(workflow => (
          <div key={workflow.id} className="workflow-card" onClick={() => setWorkflowModal(true)}>
            <div className="workflow-header">
              <div className="workflow-info">
                <h3>{workflow.name}</h3>
                <span className="workflow-type">{workflow.type}</span>
              </div>
              <div className="workflow-status">
                <span 
                  className="status-indicator"
                  style={{ backgroundColor: getStatusColor(workflow.status) }}
                ></span>
                <span className="status-text">{workflow.status}</span>
              </div>
            </div>

            <div className="workflow-description">
              <p>{workflow.description}</p>
            </div>

            <div className="workflow-progress">
              <div className="progress-info">
                <span className="progress-label">Progress</span>
                <span className="progress-steps">{workflow.completedSteps}/{workflow.totalSteps}</span>
              </div>
              <div className="progress-bar">
                <div 
                  className="progress-fill"
                  style={{ width: `${workflow.progress}%` }}
                ></div>
              </div>
            </div>

            <div className="workflow-stats">
              <div className="stat-row">
                <div className="stat">
                  <span className="stat-value">{workflow.tasks.length}</span>
                  <span className="stat-label">Tasks</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{workflow.delegations.length}</span>
                  <span className="stat-label">Delegations</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{workflow.agents.length}</span>
                  <span className="stat-label">Agents</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{workflow.parallelBranches}</span>
                  <span className="stat-label">Branches</span>
                </div>
              </div>
            </div>

            <div className="workflow-metrics">
              <div className="metric">
                <span className="metric-label">Success Rate:</span>
                <span className="metric-value">{workflow.successRate}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Efficiency:</span>
                <span className="metric-value">{workflow.efficiency}%</span>
              </div>
              <div className="metric">
                <span className="metric-label">Resource Utilization:</span>
                <span className="metric-value">{workflow.resourceUtilization}%</span>
              </div>
            </div>

            <div className="workflow-footer">
              <div className="workflow-timing">
                <span className="start-time">
                  Started: {new Date(workflow.startedAt).toLocaleDateString()}
                </span>
                {workflow.actualCompletion && (
                  <span className="end-time">
                    Completed: {new Date(workflow.actualCompletion).toLocaleDateString()}
                  </span>
                )}
              </div>
              <div className="workflow-controls">
                <button className="workflow-action">
                  <i className="fas fa-play"></i>
                </button>
                <button className="workflow-action">
                  <i className="fas fa-pause"></i>
                </button>
                <button className="workflow-action">
                  <i className="fas fa-cog"></i>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'overview':
        return renderOverviewView();
      case 'tasks':
        return renderTasksView();
      case 'delegations':
        return renderDelegationsView();
      case 'workflows':
        return renderWorkflowsView();
      default:
        return renderOverviewView();
    }
  };

  if (loading) {
    return (
      <div className="task-delegation-tracking loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading task delegation tracking...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="task-delegation-tracking error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={handleRefresh}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="task-delegation-tracking">
      <div className="delegation-header">
        <div className="header-left">
          <h2>Task Delegation Tracking</h2>
          <p>Monitor and manage task delegation across enterprise agents</p>
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
        </div>
      </div>

      <div className="delegation-navigation">
        <div className="nav-buttons">
          <button 
            className={`nav-button ${activeView === 'overview' ? 'active' : ''}`}
            onClick={() => setActiveView('overview')}
          >
            <i className="fas fa-tachometer-alt"></i>
            Overview
          </button>
          <button 
            className={`nav-button ${activeView === 'tasks' ? 'active' : ''}`}
            onClick={() => setActiveView('tasks')}
          >
            <i className="fas fa-tasks"></i>
            Tasks
            <span className="count">{tasks.length}</span>
          </button>
          <button 
            className={`nav-button ${activeView === 'delegations' ? 'active' : ''}`}
            onClick={() => setActiveView('delegations')}
          >
            <i className="fas fa-share-alt"></i>
            Delegations
            <span className="count">{delegations.length}</span>
          </button>
          <button 
            className={`nav-button ${activeView === 'workflows' ? 'active' : ''}`}
            onClick={() => setActiveView('workflows')}
          >
            <i className="fas fa-project-diagram"></i>
            Workflows
            <span className="count">{workflows.length}</span>
          </button>
        </div>
      </div>

      <div className="delegation-main">
        {renderContent()}
      </div>

      {/* Task Modal */}
      {taskModal && selectedTask && (
        <div className="modal-overlay" onClick={() => setTaskModal(false)}>
          <div className="task-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Task Details: {selectedTask.title}</h3>
              <button className="close-button" onClick={() => setTaskModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="task-details">
                <div className="detail-section">
                  <h4>Basic Information</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Task ID:</span>
                      <span className="detail-value">{selectedTask.id}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Type:</span>
                      <span className="detail-value">{selectedTask.type}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Status:</span>
                      <span className="detail-value status" style={{ color: getStatusColor(selectedTask.status) }}>
                        {selectedTask.status}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Priority:</span>
                      <span className="detail-value priority" style={{ color: getPriorityColor(selectedTask.priority) }}>
                        {selectedTask.priority}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Complexity:</span>
                      <span className="detail-value">{selectedTask.complexity}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Progress:</span>
                      <span className="detail-value">{selectedTask.progress}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Delegation Information</h4>
                  <div className="delegation-details">
                    <div className="delegation-flow-diagram">
                      <div className="flow-step">
                        <div className="flow-agent">
                          <i className="fas fa-user"></i>
                          <span>Original: {selectedTask.originalAssignee}</span>
                        </div>
                        <i className="fas fa-arrow-right flow-arrow"></i>
                        <div className="flow-agent current">
                          <i className="fas fa-user-check"></i>
                          <span>Current: {selectedTask.assignedAgent}</span>
                        </div>
                      </div>
                      <div className="delegation-reason-box">
                        <strong>Reason:</strong> {selectedTask.delegationReason}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Metrics</h4>
                  <div className="metrics-grid">
                    <div className="metric-item">
                      <span className="metric-label">Success Probability:</span>
                      <span className="metric-value">{selectedTask.successProbability}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Risk Level:</span>
                      <span className="metric-value" style={{ color: getRiskColor(selectedTask.riskLevel) }}>
                        {selectedTask.riskLevel}
                      </span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Automation Level:</span>
                      <span className="metric-value">{selectedTask.automationLevel}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Accuracy:</span>
                      <span className="metric-value">{selectedTask.performanceMetrics.accuracy}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Resource Requirements</h4>
                  <div className="resource-grid">
                    {Object.entries(selectedTask.resourceRequirements).map(([resource, value]) => (
                      <div key={resource} className="resource-item">
                        <span className="resource-label">{resource.toUpperCase()}:</span>
                        <span className="resource-value">{value}{resource === 'gpu' && value === 0 ? ' (Not required)' : '%'}</span>
                        <div className="resource-bar">
                          <div 
                            className="resource-fill"
                            style={{ width: `${Math.min(value, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delegation Modal */}
      {delegationModal && selectedDelegation && (
        <div className="modal-overlay" onClick={() => setDelegationModal(false)}>
          <div className="delegation-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Delegation Details: {selectedDelegation.id}</h3>
              <button className="close-button" onClick={() => setDelegationModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="delegation-details">
                <div className="detail-section">
                  <h4>Delegation Overview</h4>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <span className="detail-label">Type:</span>
                      <span className="detail-value">{selectedDelegation.type}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Status:</span>
                      <span className="detail-value" style={{ color: getStatusColor(selectedDelegation.status) }}>
                        {selectedDelegation.status}
                      </span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Strategy:</span>
                      <span className="detail-value">{selectedDelegation.strategy}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Priority:</span>
                      <span className="detail-value" style={{ color: getPriorityColor(selectedDelegation.priority) }}>
                        {selectedDelegation.priority}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Agent Flow</h4>
                  <div className="flow-diagram">
                    <div className="flow-agent">
                      <i className="fas fa-user"></i>
                      <span>From Agent</span>
                      <strong>{selectedDelegation.fromAgent}</strong>
                    </div>
                    <div className="flow-arrow">
                      <i className="fas fa-arrow-right"></i>
                      <div className="flow-message">
                        <span>{selectedDelegation.reason}</span>
                      </div>
                    </div>
                    <div className="flow-agent">
                      <i className="fas fa-user-check"></i>
                      <span>To Agent</span>
                      <strong>{selectedDelegation.toAgent}</strong>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Performance Analysis</h4>
                  <div className="metrics-grid">
                    <div className="metric-item">
                      <span className="metric-label">Confidence:</span>
                      <span className="metric-value">{selectedDelegation.confidence}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Skill Match:</span>
                      <span className="metric-value">{selectedDelegation.skillMatch}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Workload Fit:</span>
                      <span className="metric-value">{selectedDelegation.workloadFit}%</span>
                    </div>
                    <div className="metric-item">
                      <span className="metric-label">Success Probability:</span>
                      <span className="metric-value">{selectedDelegation.successProbability}%</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h4>Technical Information</h4>
                  <div className="technical-info">
                    <div className="tech-item">
                      <span className="tech-label">Delegation Time:</span>
                      <span className="tech-value">{selectedDelegation.metrics?.delegationTime}</span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Expected Duration:</span>
                      <span className="tech-value">{selectedDelegation.expectedDuration}</span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Risk Assessment:</span>
                      <span className="tech-value" style={{ color: getRiskColor(selectedDelegation.riskAssessment) }}>
                        {selectedDelegation.riskAssessment}
                      </span>
                    </div>
                    <div className="tech-item">
                      <span className="tech-label">Monitoring Level:</span>
                      <span className="tech-value">{selectedDelegation.monitoringLevel}</span>
                    </div>
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

export default TaskDelegationTracking;
