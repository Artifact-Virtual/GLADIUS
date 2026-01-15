import React, { useState, useEffect, useCallback } from 'react';

const ManualWorkflowControls = () => {
  const [workflows, setWorkflows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState('control'); // control, builder, history
  const [selectedWorkflow, setSelectedWorkflow] = useState(null);
  const [executionParams, setExecutionParams] = useState({});
  const [showExecutionModal, setShowExecutionModal] = useState(false);
  const [showBuilderModal, setShowBuilderModal] = useState(false);
  const [executionHistory, setExecutionHistory] = useState([]);
  const [filters, setFilters] = useState({
    status: 'all',
    category: 'all',
    priority: 'all'
  });
  const [newWorkflow, setNewWorkflow] = useState({
    name: '',
    description: '',
    category: 'business',
    priority: 'medium',
    steps: []
  });

  const generateWorkflowData = useCallback(() => {
    const categories = ['business', 'technical', 'marketing', 'finance', 'operations', 'security'];
    const priorities = ['low', 'medium', 'high', 'critical'];
    const statuses = ['ready', 'running', 'completed', 'failed', 'paused'];

    const workflowTemplates = [
      {
        name: 'Customer Data Validation',
        description: 'Validate customer information and update records',
        category: 'business',
        estimatedDuration: 15
      },
      {
        name: 'System Health Check',
        description: 'Comprehensive system health and performance check',
        category: 'technical',
        estimatedDuration: 30
      },
      {
        name: 'Marketing Campaign Launch',
        description: 'Launch and monitor marketing campaign across channels',
        category: 'marketing',
        estimatedDuration: 45
      },
      {
        name: 'Financial Report Generation',
        description: 'Generate detailed financial reports and analysis',
        category: 'finance',
        estimatedDuration: 60
      },
      {
        name: 'Inventory Reconciliation',
        description: 'Reconcile inventory counts and update system',
        category: 'operations',
        estimatedDuration: 25
      },
      {
        name: 'Security Audit Scan',
        description: 'Perform comprehensive security vulnerability scan',
        category: 'security',
        estimatedDuration: 90
      },
      {
        name: 'Employee Onboarding Process',
        description: 'Complete new employee setup and orientation',
        category: 'business',
        estimatedDuration: 120
      },
      {
        name: 'Database Backup Verification',
        description: 'Verify database backup integrity and accessibility',
        category: 'technical',
        estimatedDuration: 35
      },
      {
        name: 'Email Campaign Analytics',
        description: 'Analyze email campaign performance and generate insights',
        category: 'marketing',
        estimatedDuration: 20
      },
      {
        name: 'Invoice Processing Workflow',
        description: 'Process and approve pending invoices',
        category: 'finance',
        estimatedDuration: 40
      },
      {
        name: 'Quality Control Check',
        description: 'Perform quality control checks on production items',
        category: 'operations',
        estimatedDuration: 55
      },
      {
        name: 'Compliance Documentation',
        description: 'Update compliance documentation and certifications',
        category: 'security',
        estimatedDuration: 75
      },
      {
        name: 'Customer Feedback Analysis',
        description: 'Analyze customer feedback and generate action items',
        category: 'business',
        estimatedDuration: 30
      },
      {
        name: 'API Integration Test',
        description: 'Test API integrations and validate responses',
        category: 'technical',
        estimatedDuration: 45
      },
      {
        name: 'Social Media Content Review',
        description: 'Review and approve social media content pipeline',
        category: 'marketing',
        estimatedDuration: 25
      }
    ];

    return workflowTemplates.map((template, index) => ({
      id: `workflow-${index + 1}`,
      ...template,
      priority: priorities[Math.floor(Math.random() * priorities.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      lastRun: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
      runCount: Math.floor(Math.random() * 50) + 1,
      successRate: (Math.random() * 30 + 70).toFixed(1),
      avgDuration: template.estimatedDuration + Math.floor(Math.random() * 20) - 10,
      createdBy: ['Admin', 'System', 'Manager', 'Supervisor'][Math.floor(Math.random() * 4)],
      createdAt: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
      parameters: Array.from({ length: Math.floor(Math.random() * 5) + 2 }, (_, paramIndex) => ({
        id: `param-${paramIndex + 1}`,
        name: ['email', 'dateRange', 'department', 'threshold', 'category', 'priority'][paramIndex % 6],
        type: ['string', 'date', 'number', 'boolean', 'select'][Math.floor(Math.random() * 5)],
        required: Math.random() > 0.3,
        defaultValue: 'default',
        description: `Parameter ${paramIndex + 1} for workflow execution`
      })),
      steps: Array.from({ length: Math.floor(Math.random() * 8) + 3 }, (_, stepIndex) => ({
        id: `step-${stepIndex + 1}`,
        name: [
          'Initialize Process',
          'Validate Input',
          'Process Data',
          'Generate Output',
          'Send Notification',
          'Update Records',
          'Cleanup Resources',
          'Archive Results'
        ][stepIndex % 8],
        description: `Step ${stepIndex + 1} execution details`,
        estimatedDuration: Math.floor(Math.random() * 15) + 5,
        canSkip: Math.random() > 0.7,
        requiresApproval: Math.random() > 0.8,
        automated: Math.random() > 0.4
      })),
      dependencies: [],
      tags: categories.slice(0, Math.floor(Math.random() * 3) + 1),
      permissions: {
        execute: ['admin', 'manager', 'user'],
        view: ['admin', 'manager', 'user', 'guest'],
        modify: ['admin', 'manager']
      }
    }));
  }, []);

  const generateExecutionHistory = useCallback(() => {
    const statuses = ['completed', 'failed', 'cancelled', 'timeout'];
    const history = [];

    for (let i = 0; i < 50; i++) {
      const workflow = workflows[Math.floor(Math.random() * workflows.length)];
      if (workflow) {
        history.push({
          id: `execution-${i + 1}`,
          workflowId: workflow.id,
          workflowName: workflow.name,
          status: statuses[Math.floor(Math.random() * statuses.length)],
          startTime: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
          endTime: new Date(Date.now() - Math.random() * 29 * 86400000).toISOString(),
          duration: Math.floor(Math.random() * 180) + 30,
          triggeredBy: 'manual',
          executedBy: ['Admin', 'Manager', 'User'][Math.floor(Math.random() * 3)],
          parameters: workflow.parameters.reduce((acc, param) => {
            acc[param.name] = param.defaultValue;
            return acc;
          }, {}),
          stepResults: workflow.steps.map(step => ({
            stepId: step.id,
            status: Math.random() > 0.1 ? 'completed' : 'failed',
            duration: Math.floor(Math.random() * step.estimatedDuration * 2)
          })),
          logs: [
            'Workflow execution started',
            'Parameters validated successfully',
            'Processing data...',
            'Generating output...',
            'Workflow execution completed'
          ],
          errorMessage: workflow.error_message || null
        });
      }
    }

    return history.sort((a, b) => new Date(b.startTime) - new Date(a.startTime));
  }, [workflows]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        const workflowData = generateWorkflowData();
        setWorkflows(workflowData);
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading workflows:', error);
      }
    };

    loadData();
  }, [generateWorkflowData]);

  useEffect(() => {
    if (workflows.length > 0) {
      const history = generateExecutionHistory();
      setExecutionHistory(history);
    }
  }, [workflows, generateExecutionHistory]);

  const handleExecuteWorkflow = (workflow) => {
    setSelectedWorkflow(workflow);
    setExecutionParams(workflow.parameters.reduce((acc, param) => {
      acc[param.name] = param.defaultValue || '';
      return acc;
    }, {}));
    setShowExecutionModal(true);
  };

  const handleParameterChange = (paramName, value) => {
    setExecutionParams(prev => ({
      ...prev,
      [paramName]: value
    }));
  };

  const confirmExecution = () => {
    console.log('Executing workflow:', selectedWorkflow.name, 'with params:', executionParams);
    // Here you would typically make an API call to execute the workflow
    setShowExecutionModal(false);
    setSelectedWorkflow(null);
    setExecutionParams({});
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'ready': return '#28a745';
      case 'running': return '#4facfe';
      case 'completed': return '#28a745';
      case 'failed': return '#dc3545';
      case 'paused': return '#ffc107';
      case 'cancelled': return '#fd7e14';
      case 'timeout': return '#6c757d';
      default: return '#6c757d';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'critical': return '#dc3545';
      case 'high': return '#fd7e14';
      case 'medium': return '#ffc107';
      case 'low': return '#28a745';
      default: return '#6c757d';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'business': return '#667eea';
      case 'technical': return '#764ba2';
      case 'marketing': return '#f093fb';
      case 'finance': return '#4facfe';
      case 'operations': return '#43e97b';
      case 'security': return '#fa709a';
      default: return '#666';
    }
  };

  const filteredWorkflows = workflows.filter(workflow => {
    const matchesStatus = filters.status === 'all' || workflow.status === filters.status;
    const matchesCategory = filters.category === 'all' || workflow.category === filters.category;
    const matchesPriority = filters.priority === 'all' || workflow.priority === filters.priority;
    
    return matchesStatus && matchesCategory && matchesPriority;
  });

  const renderControlView = () => (
    <div className="control-view">
      <div className="control-filters">
        <select 
          value={filters.status} 
          onChange={(e) => setFilters({...filters, status: e.target.value})}
        >
          <option value="all">All Status</option>
          <option value="ready">Ready</option>
          <option value="running">Running</option>
          <option value="completed">Completed</option>
          <option value="failed">Failed</option>
          <option value="paused">Paused</option>
        </select>

        <select 
          value={filters.category} 
          onChange={(e) => setFilters({...filters, category: e.target.value})}
        >
          <option value="all">All Categories</option>
          <option value="business">Business</option>
          <option value="technical">Technical</option>
          <option value="marketing">Marketing</option>
          <option value="finance">Finance</option>
          <option value="operations">Operations</option>
          <option value="security">Security</option>
        </select>

        <select 
          value={filters.priority} 
          onChange={(e) => setFilters({...filters, priority: e.target.value})}
        >
          <option value="all">All Priorities</option>
          <option value="critical">Critical</option>
          <option value="high">High</option>
          <option value="medium">Medium</option>
          <option value="low">Low</option>
        </select>
      </div>

      <div className="workflows-grid">
        {filteredWorkflows.map(workflow => (
          <div key={workflow.id} className="workflow-control-card">
            <div className="workflow-header">
              <div className="workflow-title">
                <h3>{workflow.name}</h3>
                <div className="workflow-badges">
                  <span 
                    className="status-badge" 
                    style={{backgroundColor: getStatusColor(workflow.status)}}
                  >
                    {workflow.status}
                  </span>
                  <span 
                    className="priority-badge" 
                    style={{backgroundColor: getPriorityColor(workflow.priority)}}
                  >
                    {workflow.priority}
                  </span>
                  <span 
                    className="category-badge" 
                    style={{backgroundColor: getCategoryColor(workflow.category)}}
                  >
                    {workflow.category}
                  </span>
                </div>
              </div>
            </div>

            <div className="workflow-description">
              <p>{workflow.description}</p>
            </div>

            <div className="workflow-stats">
              <div className="stat-item">
                <i className="fas fa-clock"></i>
                <span>{workflow.avgDuration}min avg</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-play"></i>
                <span>{workflow.runCount} runs</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-check-circle"></i>
                <span>{workflow.successRate}% success</span>
              </div>
              <div className="stat-item">
                <i className="fas fa-list"></i>
                <span>{workflow.steps.length} steps</span>
              </div>
            </div>

            <div className="workflow-parameters">
              <div className="parameters-label">Parameters:</div>
              <div className="parameters-list">
                {workflow.parameters.slice(0, 3).map(param => (
                  <span key={param.id} className="parameter-tag">
                    {param.name}
                    {param.required && <span className="required">*</span>}
                  </span>
                ))}
                {workflow.parameters.length > 3 && (
                  <span className="more-params">+{workflow.parameters.length - 3}</span>
                )}
              </div>
            </div>

            <div className="workflow-actions">
              <button 
                className="action-btn execute"
                onClick={() => handleExecuteWorkflow(workflow)}
                disabled={workflow.status === 'running'}
              >
                <i className="fas fa-play"></i>
                Execute
              </button>
              <button className="action-btn pause" disabled={workflow.status !== 'running'}>
                <i className="fas fa-pause"></i>
                Pause
              </button>
              <button className="action-btn stop" disabled={workflow.status !== 'running'}>
                <i className="fas fa-stop"></i>
                Stop
              </button>
              <button className="action-btn details">
                <i className="fas fa-info-circle"></i>
                Details
              </button>
            </div>

            <div className="workflow-footer">
              <span className="last-run">Last run: {new Date(workflow.lastRun).toLocaleDateString()}</span>
              <span className="created-by">by {workflow.createdBy}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderBuilderView = () => (
    <div className="builder-view">
      <div className="builder-header">
        <h3>Workflow Builder</h3>
        <button 
          className="create-workflow-btn"
          onClick={() => setShowBuilderModal(true)}
        >
          <i className="fas fa-plus"></i>
          Create New Workflow
        </button>
      </div>

      <div className="workflow-templates">
        <h4>Quick Start Templates</h4>
        <div className="templates-grid">
          {[
            { name: 'Basic Approval', icon: 'fa-check', description: 'Simple approval workflow' },
            { name: 'Data Processing', icon: 'fa-database', description: 'ETL data processing pipeline' },
            { name: 'Notification Chain', icon: 'fa-bell', description: 'Multi-step notification workflow' },
            { name: 'Report Generation', icon: 'fa-chart-bar', description: 'Automated report generation' }
          ].map((template, index) => (
            <div key={index} className="template-card">
              <div className="template-icon">
                <i className={`fas ${template.icon}`}></i>
              </div>
              <div className="template-info">
                <h5>{template.name}</h5>
                <p>{template.description}</p>
              </div>
              <button className="use-template-btn">
                <i className="fas fa-plus"></i>
                Use Template
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="recent-workflows">
        <h4>Recent Workflows</h4>
        <div className="recent-list">
          {workflows.slice(0, 5).map(workflow => (
            <div key={workflow.id} className="recent-workflow-item">
              <div className="workflow-info">
                <div className="workflow-name">{workflow.name}</div>
                <div className="workflow-meta">
                  {workflow.category} • {workflow.steps.length} steps • {workflow.runCount} runs
                </div>
              </div>
              <div className="workflow-actions">
                <button className="action-btn-small edit">
                  <i className="fas fa-edit"></i>
                  Edit
                </button>
                <button className="action-btn-small clone">
                  <i className="fas fa-copy"></i>
                  Clone
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  const renderHistoryView = () => (
    <div className="history-view">
      <div className="history-header">
        <h3>Execution History</h3>
        <div className="history-filters">
          <select defaultValue="all">
            <option value="all">All Workflows</option>
            {workflows.map(workflow => (
              <option key={workflow.id} value={workflow.id}>{workflow.name}</option>
            ))}
          </select>
          <select defaultValue="all">
            <option value="all">All Status</option>
            <option value="completed">Completed</option>
            <option value="failed">Failed</option>
            <option value="cancelled">Cancelled</option>
          </select>
        </div>
      </div>

      <div className="history-list">
        {executionHistory.slice(0, 20).map(execution => (
          <div key={execution.id} className="history-item">
            <div className="execution-status-indicator">
              <div 
                className="status-dot" 
                style={{backgroundColor: getStatusColor(execution.status)}}
              ></div>
            </div>
            
            <div className="execution-info">
              <div className="execution-header">
                <div className="workflow-name">{execution.workflowName}</div>
                <div className="execution-time">
                  {new Date(execution.startTime).toLocaleString()}
                </div>
              </div>
              
              <div className="execution-details">
                <span className="duration">{Math.round(execution.duration / 60)}min</span>
                <span className="executed-by">by {execution.executedBy}</span>
                <span className="step-count">{execution.stepResults.length} steps</span>
              </div>

              {execution.errorMessage && (
                <div className="error-message">
                  <i className="fas fa-exclamation-triangle"></i>
                  {execution.errorMessage}
                </div>
              )}
            </div>

            <div className="execution-actions">
              <button className="action-btn-small view-logs">
                <i className="fas fa-file-alt"></i>
                Logs
              </button>
              <button className="action-btn-small rerun">
                <i className="fas fa-redo"></i>
                Rerun
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="manual-workflow-controls loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading workflow controls...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="manual-workflow-controls">
      <div className="controls-header">
        <div className="header-left">
          <h2>Manual Workflow Controls</h2>
          <p>Execute, monitor, and manage workflows manually</p>
        </div>
        <div className="header-stats">
          <div className="stat-card">
            <div className="stat-value">{workflows.filter(w => w.status === 'ready').length}</div>
            <div className="stat-label">Ready</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{workflows.filter(w => w.status === 'running').length}</div>
            <div className="stat-label">Running</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{executionHistory.filter(e => e.status === 'completed').length}</div>
            <div className="stat-label">Completed Today</div>
          </div>
        </div>
      </div>

      <div className="controls-nav">
        <button 
          className={`nav-btn ${activeView === 'control' ? 'active' : ''}`}
          onClick={() => setActiveView('control')}
        >
          <i className="fas fa-play-circle"></i>
          Workflow Control
        </button>
        <button 
          className={`nav-btn ${activeView === 'builder' ? 'active' : ''}`}
          onClick={() => setActiveView('builder')}
        >
          <i className="fas fa-tools"></i>
          Workflow Builder
        </button>
        <button 
          className={`nav-btn ${activeView === 'history' ? 'active' : ''}`}
          onClick={() => setActiveView('history')}
        >
          <i className="fas fa-history"></i>
          Execution History
        </button>
      </div>

      <div className="controls-content">
        {activeView === 'control' && renderControlView()}
        {activeView === 'builder' && renderBuilderView()}
        {activeView === 'history' && renderHistoryView()}
      </div>

      {showExecutionModal && selectedWorkflow && (
        <div className="modal-overlay" onClick={() => setShowExecutionModal(false)}>
          <div className="execution-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Execute Workflow: {selectedWorkflow.name}</h3>
              <button className="close-btn" onClick={() => setShowExecutionModal(false)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            
            <div className="modal-content">
              <div className="workflow-summary">
                <div className="summary-item">
                  <strong>Estimated Duration:</strong> {selectedWorkflow.avgDuration} minutes
                </div>
                <div className="summary-item">
                  <strong>Steps:</strong> {selectedWorkflow.steps.length}
                </div>
                <div className="summary-item">
                  <strong>Success Rate:</strong> {selectedWorkflow.successRate}%
                </div>
              </div>

              <div className="parameters-section">
                <h4>Parameters</h4>
                {selectedWorkflow.parameters.map(param => (
                  <div key={param.id} className="parameter-input">
                    <label>
                      {param.name}
                      {param.required && <span className="required">*</span>}
                    </label>
                    <input
                      type={param.type === 'number' ? 'number' : 
                           param.type === 'date' ? 'date' : 'text'}
                      value={executionParams[param.name] || ''}
                      onChange={(e) => handleParameterChange(param.name, e.target.value)}
                      placeholder={param.description}
                      required={param.required}
                    />
                  </div>
                ))}
              </div>

              <div className="steps-preview">
                <h4>Execution Steps</h4>
                <div className="steps-list">
                  {selectedWorkflow.steps.map((step, index) => (
                    <div key={step.id} className="step-preview">
                      <div className="step-number">{index + 1}</div>
                      <div className="step-content">
                        <div className="step-name">{step.name}</div>
                        <div className="step-meta">
                          {step.estimatedDuration}min
                          {step.requiresApproval && <span className="approval-required">Approval Required</span>}
                          {step.canSkip && <span className="can-skip">Skippable</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
            
            <div className="modal-actions">
              <button className="action-btn cancel" onClick={() => setShowExecutionModal(false)}>
                Cancel
              </button>
              <button className="action-btn execute" onClick={confirmExecution}>
                <i className="fas fa-play"></i>
                Execute Workflow
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ManualWorkflowControls;
