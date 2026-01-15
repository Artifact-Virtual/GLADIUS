import React, { useState, useEffect, useCallback } from 'react';

const WorkflowTemplateLibrary = () => {
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('gallery'); // gallery, list, categories
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [filters, setFilters] = useState({
    category: 'all',
    complexity: 'all',
    popularity: 'all'
  });
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('popularity');
  const [newTemplate, setNewTemplate] = useState({
    name: '',
    description: '',
    category: 'business',
    complexity: 'medium',
    steps: []
  });

  const generateTemplates = useCallback(() => {
    const categories = ['business', 'data', 'integration', 'automation', 'reporting', 'security'];
    const complexities = ['simple', 'medium', 'complex', 'advanced'];
    
    const templateData = [
      {
        name: 'Customer Onboarding Workflow',
        description: 'Complete customer registration and setup process with validation steps',
        category: 'business',
        tags: ['customer', 'onboarding', 'validation', 'setup']
      },
      {
        name: 'Data Processing Pipeline',
        description: 'ETL workflow for data extraction, transformation, and loading',
        category: 'data',
        tags: ['etl', 'processing', 'pipeline', 'transformation']
      },
      {
        name: 'API Integration Template',
        description: 'Standard template for integrating external APIs with error handling',
        category: 'integration',
        tags: ['api', 'integration', 'error-handling', 'external']
      },
      {
        name: 'Automated Reporting Workflow',
        description: 'Generate and distribute reports on scheduled basis',
        category: 'reporting',
        tags: ['reports', 'automation', 'scheduling', 'distribution']
      },
      {
        name: 'Security Compliance Check',
        description: 'Comprehensive security audit and compliance validation',
        category: 'security',
        tags: ['security', 'compliance', 'audit', 'validation']
      },
      {
        name: 'Employee Onboarding Process',
        description: 'HR workflow for new employee setup and orientation',
        category: 'business',
        tags: ['hr', 'employee', 'onboarding', 'orientation']
      },
      {
        name: 'Backup and Recovery Automation',
        description: 'Automated backup process with disaster recovery procedures',
        category: 'automation',
        tags: ['backup', 'recovery', 'disaster', 'automation']
      },
      {
        name: 'Quality Assurance Testing',
        description: 'Automated QA testing workflow with result reporting',
        category: 'automation',
        tags: ['qa', 'testing', 'automation', 'quality']
      },
      {
        name: 'Financial Reconciliation',
        description: 'Monthly financial reconciliation and reporting process',
        category: 'business',
        tags: ['finance', 'reconciliation', 'reporting', 'monthly']
      },
      {
        name: 'Data Migration Workflow',
        description: 'Safe data migration with validation and rollback capabilities',
        category: 'data',
        tags: ['migration', 'validation', 'rollback', 'data']
      },
      {
        name: 'Email Campaign Automation',
        description: 'Marketing email campaign with personalization and tracking',
        category: 'automation',
        tags: ['email', 'campaign', 'marketing', 'personalization']
      },
      {
        name: 'Incident Response Workflow',
        description: 'Security incident response and escalation procedures',
        category: 'security',
        tags: ['incident', 'response', 'escalation', 'security']
      },
      {
        name: 'Invoice Processing Automation',
        description: 'Automated invoice validation and approval workflow',
        category: 'business',
        tags: ['invoice', 'approval', 'validation', 'finance']
      },
      {
        name: 'System Health Monitoring',
        description: 'Continuous system monitoring with alerting',
        category: 'automation',
        tags: ['monitoring', 'health', 'alerting', 'system']
      },
      {
        name: 'Customer Support Ticket Routing',
        description: 'Smart ticket routing based on priority and expertise',
        category: 'business',
        tags: ['support', 'routing', 'priority', 'customer']
      },
      {
        name: 'Database Maintenance Workflow',
        description: 'Routine database maintenance and optimization tasks',
        category: 'data',
        tags: ['database', 'maintenance', 'optimization', 'routine']
      },
      {
        name: 'Social Media Publishing',
        description: 'Multi-platform social media content publishing workflow',
        category: 'automation',
        tags: ['social', 'publishing', 'content', 'multi-platform']
      },
      {
        name: 'Contract Approval Process',
        description: 'Legal contract review and approval workflow',
        category: 'business',
        tags: ['contract', 'legal', 'approval', 'review']
      }
    ];

    return templateData.map((template, index) => ({
      id: `template-${index + 1}`,
      ...template,
      complexity: complexities[Math.floor(Math.random() * complexities.length)],
      popularity: Math.floor(Math.random() * 1000) + 100,
      usageCount: Math.floor(Math.random() * 500) + 50,
      rating: (Math.random() * 2 + 3).toFixed(1), // 3.0 - 5.0
      estimatedTime: Math.floor(Math.random() * 180) + 30, // 30-210 minutes
      createdBy: ['System Admin', 'DevOps Team', 'Business Analyst', 'Workflow Designer'][Math.floor(Math.random() * 4)],
      createdAt: new Date(Date.now() - Math.random() * 365 * 86400000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 30 * 86400000).toISOString(),
      version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
      steps: Array.from({ length: Math.floor(Math.random() * 8) + 3 }, (_, stepIndex) => ({
        id: `step-${stepIndex + 1}`,
        name: [
          'Initialize Process',
          'Validate Input Data',
          'Process Information',
          'Generate Report',
          'Send Notification',
          'Update Database',
          'Perform Validation',
          'Execute Action',
          'Complete Process',
          'Archive Results'
        ][stepIndex % 10],
        description: `Step ${stepIndex + 1} description for workflow execution`,
        type: ['action', 'decision', 'approval', 'notification', 'validation'][Math.floor(Math.random() * 5)],
        estimatedTime: Math.floor(Math.random() * 30) + 5,
        required: Math.random() > 0.3,
        automation: Math.random() > 0.4
      })),
      requirements: [
        'System access permissions',
        'Valid input data format',
        'Network connectivity',
        'Database access',
        'Email configuration'
      ].slice(0, Math.floor(Math.random() * 3) + 2),
      outputs: [
        'Process completion report',
        'Updated records',
        'Notification emails',
        'Generated documents',
        'Audit logs'
      ].slice(0, Math.floor(Math.random() * 3) + 2),
      variables: Array.from({ length: Math.floor(Math.random() * 5) + 2 }, (_, varIndex) => ({
        name: ['customerEmail', 'processId', 'approvalLevel', 'dataSource', 'outputFormat'][varIndex % 5],
        type: ['string', 'number', 'boolean', 'array', 'object'][Math.floor(Math.random() * 5)],
        required: Math.random() > 0.4,
        defaultValue: 'default_value'
      })),
      permissions: {
        view: ['admin', 'user', 'guest'],
        use: ['admin', 'user'],
        edit: ['admin'],
        delete: ['admin']
      },
      deployments: Math.floor(Math.random() * 20) + 5,
      successRate: (Math.random() * 20 + 80).toFixed(1),
      avgExecutionTime: Math.floor(Math.random() * 120) + 30,
      lastUsed: new Date(Date.now() - Math.random() * 7 * 86400000).toISOString(),
      reviews: Array.from({ length: Math.floor(Math.random() * 5) + 1 }, (_, reviewIndex) => ({
        id: `review-${reviewIndex + 1}`,
        user: `user${reviewIndex + 1}`,
        rating: Math.floor(Math.random() * 2) + 4, // 4-5 stars
        comment: 'Great template, very useful for our automation needs',
        date: new Date(Date.now() - Math.random() * 90 * 86400000).toISOString()
      })),
      relatedTemplates: [],
      documentation: {
        setup: 'Setup instructions for the workflow template',
        usage: 'Usage guidelines and best practices',
        troubleshooting: 'Common issues and solutions'
      }
    }));
  }, []);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      try {
        await new Promise(resolve => setTimeout(resolve, 1000));
        setTemplates(generateTemplates());
        setLoading(false);
      } catch (error) {
        setLoading(false);
        console.error('Error loading templates:', error);
      }
    };

    loadData();
  }, [generateTemplates]);

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.tags.some(tag => tag.toLowerCase().includes(searchTerm.toLowerCase()));
    
    return matchesSearch &&
           (filters.category === 'all' || template.category === filters.category) &&
           (filters.complexity === 'all' || template.complexity === filters.complexity);
  });

  const sortedTemplates = [...filteredTemplates].sort((a, b) => {
    switch (sortBy) {
      case 'popularity':
        return b.popularity - a.popularity;
      case 'rating':
        return parseFloat(b.rating) - parseFloat(a.rating);
      case 'usage':
        return b.usageCount - a.usageCount;
      case 'name':
        return a.name.localeCompare(b.name);
      case 'recent':
        return new Date(b.updatedAt) - new Date(a.updatedAt);
      default:
        return 0;
    }
  });

  const getComplexityColor = (complexity) => {
    switch (complexity) {
      case 'simple': return '#28a745';
      case 'medium': return '#ffc107';
      case 'complex': return '#fd7e14';
      case 'advanced': return '#dc3545';
      default: return '#6c757d';
    }
  };

  const getCategoryColor = (category) => {
    switch (category) {
      case 'business': return '#667eea';
      case 'data': return '#764ba2';
      case 'integration': return '#f093fb';
      case 'automation': return '#4facfe';
      case 'reporting': return '#43e97b';
      case 'security': return '#fa709a';
      default: return '#666';
    }
  };

  const handleTemplateUse = (template) => {
    console.log('Using template:', template.name);
    // Here you would typically navigate to workflow creation with this template
  };

  const renderGalleryView = () => (
    <div className="templates-gallery">
      {sortedTemplates.map(template => (
        <div key={template.id} className="template-card">
          <div className="template-header">
            <div className="template-title">
              <h3>{template.name}</h3>
              <span className="template-version">{template.version}</span>
            </div>
            <div className="template-badges">
              <span className="category-badge" style={{backgroundColor: getCategoryColor(template.category)}}>
                {template.category}
              </span>
              <span className="complexity-badge" style={{backgroundColor: getComplexityColor(template.complexity)}}>
                {template.complexity}
              </span>
            </div>
          </div>

          <div className="template-description">
            <p>{template.description}</p>
          </div>

          <div className="template-stats">
            <div className="stat-item">
              <i className="fas fa-star"></i>
              <span>{template.rating}</span>
            </div>
            <div className="stat-item">
              <i className="fas fa-download"></i>
              <span>{template.usageCount}</span>
            </div>
            <div className="stat-item">
              <i className="fas fa-clock"></i>
              <span>{template.estimatedTime}min</span>
            </div>
            <div className="stat-item">
              <i className="fas fa-list"></i>
              <span>{template.steps.length} steps</span>
            </div>
          </div>

          <div className="template-tags">
            {template.tags.slice(0, 3).map(tag => (
              <span key={tag} className="template-tag">{tag}</span>
            ))}
            {template.tags.length > 3 && (
              <span className="more-tags">+{template.tags.length - 3}</span>
            )}
          </div>

          <div className="template-actions">
            <button 
              className="action-btn use"
              onClick={() => handleTemplateUse(template)}
            >
              <i className="fas fa-play"></i>
              Use Template
            </button>
            <button 
              className="action-btn preview"
              onClick={() => setSelectedTemplate(template)}
            >
              <i className="fas fa-eye"></i>
              Preview
            </button>
            <button className="action-btn favorite">
              <i className="fas fa-heart"></i>
            </button>
          </div>

          <div className="template-footer">
            <span className="created-by">by {template.createdBy}</span>
            <span className="last-used">Used {new Date(template.lastUsed).toLocaleDateString()}</span>
          </div>
        </div>
      ))}
    </div>
  );

  const renderListView = () => (
    <div className="templates-list">
      <div className="list-header">
        <div className="header-cell">Template</div>
        <div className="header-cell">Category</div>
        <div className="header-cell">Complexity</div>
        <div className="header-cell">Rating</div>
        <div className="header-cell">Usage</div>
        <div className="header-cell">Actions</div>
      </div>
      {sortedTemplates.map(template => (
        <div key={template.id} className="list-row">
          <div className="list-cell template-info">
            <div className="template-name">{template.name}</div>
            <div className="template-desc">{template.description.substring(0, 60)}...</div>
          </div>
          <div className="list-cell">
            <span className="category-tag" style={{backgroundColor: getCategoryColor(template.category)}}>
              {template.category}
            </span>
          </div>
          <div className="list-cell">
            <span className="complexity-tag" style={{backgroundColor: getComplexityColor(template.complexity)}}>
              {template.complexity}
            </span>
          </div>
          <div className="list-cell">
            <div className="rating-display">
              <i className="fas fa-star"></i>
              {template.rating}
            </div>
          </div>
          <div className="list-cell">
            <span className="usage-count">{template.usageCount}</span>
          </div>
          <div className="list-cell">
            <div className="list-actions">
              <button 
                className="action-btn-small use"
                onClick={() => handleTemplateUse(template)}
              >
                <i className="fas fa-play"></i>
              </button>
              <button 
                className="action-btn-small preview"
                onClick={() => setSelectedTemplate(template)}
              >
                <i className="fas fa-eye"></i>
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const renderCategoriesView = () => {
    const categorizedTemplates = templates.reduce((acc, template) => {
      if (!acc[template.category]) {
        acc[template.category] = [];
      }
      acc[template.category].push(template);
      return acc;
    }, {});

    return (
      <div className="categories-view">
        {Object.entries(categorizedTemplates).map(([category, categoryTemplates]) => (
          <div key={category} className="category-section">
            <div className="category-header">
              <h3 style={{color: getCategoryColor(category)}}>{category}</h3>
              <span className="category-count">{categoryTemplates.length} templates</span>
            </div>
            <div className="category-templates">
              {categoryTemplates.slice(0, 6).map(template => (
                <div key={template.id} className="category-template-card">
                  <div className="template-mini-header">
                    <h4>{template.name}</h4>
                    <span className="mini-rating">
                      <i className="fas fa-star"></i>
                      {template.rating}
                    </span>
                  </div>
                  <p>{template.description.substring(0, 80)}...</p>
                  <div className="mini-actions">
                    <button 
                      className="mini-btn use"
                      onClick={() => handleTemplateUse(template)}
                    >
                      Use
                    </button>
                    <button 
                      className="mini-btn preview"
                      onClick={() => setSelectedTemplate(template)}
                    >
                      Preview
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="workflow-template-library loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading workflow templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="workflow-template-library">
      <div className="library-header">
        <div className="header-left">
          <h2>Workflow Template Library</h2>
          <p>Discover and use pre-built workflow templates</p>
        </div>
        <div className="header-actions">
          <div className="view-toggle">
            <button 
              className={`view-btn ${viewMode === 'gallery' ? 'active' : ''}`}
              onClick={() => setViewMode('gallery')}
            >
              <i className="fas fa-th-large"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <i className="fas fa-list"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'categories' ? 'active' : ''}`}
              onClick={() => setViewMode('categories')}
            >
              <i className="fas fa-folder"></i>
            </button>
          </div>
          <button 
            className="create-template-btn"
            onClick={() => setShowCreateModal(true)}
          >
            <i className="fas fa-plus"></i>
            Create Template
          </button>
        </div>
      </div>

      <div className="library-controls">
        <div className="search-controls">
          <div className="search-box">
            <i className="fas fa-search"></i>
            <input
              type="text"
              placeholder="Search templates..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>

        <div className="filter-controls">
          <select value={filters.category} onChange={(e) => setFilters({...filters, category: e.target.value})}>
            <option value="all">All Categories</option>
            <option value="business">Business</option>
            <option value="data">Data</option>
            <option value="integration">Integration</option>
            <option value="automation">Automation</option>
            <option value="reporting">Reporting</option>
            <option value="security">Security</option>
          </select>

          <select value={filters.complexity} onChange={(e) => setFilters({...filters, complexity: e.target.value})}>
            <option value="all">All Complexity</option>
            <option value="simple">Simple</option>
            <option value="medium">Medium</option>
            <option value="complex">Complex</option>
            <option value="advanced">Advanced</option>
          </select>

          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="popularity">Most Popular</option>
            <option value="rating">Highest Rated</option>
            <option value="usage">Most Used</option>
            <option value="recent">Recently Updated</option>
            <option value="name">Name A-Z</option>
          </select>
        </div>

        <div className="results-info">
          <span>{sortedTemplates.length} templates found</span>
        </div>
      </div>

      <div className="library-content">
        {viewMode === 'gallery' && renderGalleryView()}
        {viewMode === 'list' && renderListView()}
        {viewMode === 'categories' && renderCategoriesView()}
      </div>

      {selectedTemplate && (
        <div className="modal-overlay" onClick={() => setSelectedTemplate(null)}>
          <div className="template-preview-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>{selectedTemplate.name}</h3>
              <button className="close-btn" onClick={() => setSelectedTemplate(null)}>
                <i className="fas fa-times"></i>
              </button>
            </div>
            <div className="modal-content">
              <div className="preview-section">
                <h4>Workflow Steps</h4>
                <div className="steps-list">
                  {selectedTemplate.steps.map((step, index) => (
                    <div key={step.id} className="step-item">
                      <div className="step-number">{index + 1}</div>
                      <div className="step-content">
                        <div className="step-name">{step.name}</div>
                        <div className="step-description">{step.description}</div>
                        <div className="step-meta">
                          <span className="step-type">{step.type}</span>
                          <span className="step-time">{step.estimatedTime}min</span>
                          {step.required && <span className="step-required">Required</span>}
                          {step.automation && <span className="step-automated">Automated</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="preview-section">
                <h4>Requirements</h4>
                <ul className="requirements-list">
                  {selectedTemplate.requirements.map((req, index) => (
                    <li key={index}>{req}</li>
                  ))}
                </ul>
              </div>

              <div className="preview-section">
                <h4>Expected Outputs</h4>
                <ul className="outputs-list">
                  {selectedTemplate.outputs.map((output, index) => (
                    <li key={index}>{output}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="action-btn use-template"
                onClick={() => handleTemplateUse(selectedTemplate)}
              >
                <i className="fas fa-play"></i>
                Use This Template
              </button>
              <button className="action-btn clone-template">
                <i className="fas fa-copy"></i>
                Clone & Customize
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowTemplateLibrary;
