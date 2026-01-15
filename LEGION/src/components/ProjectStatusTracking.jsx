import React, { useState, useEffect } from 'react';

const ProjectStatusTracking = ({ projectData, onProjectUpdate, onMilestoneUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('overview'); // 'overview', 'timeline', 'gantt', 'milestones'
  const [selectedProject, setSelectedProject] = useState(null);
  const [timeFilter, setTimeFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [data, setData] = useState({
    projects: [],
    milestones: [],
    metrics: {},
    dependencies: [],
    resources: []
  });

  useEffect(() => {
    const loadProjectData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Use provided projectData or fetch from API
        if (projectData) {
          setData(projectData);
        } else {
          const response = await fetch(`/api/enterprise/project-tracking?filter=${statusFilter}&time=${timeFilter}`);
          if (!response.ok) throw new Error('Failed to load project data');
          
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (err) {
        console.error('Error loading project data:', err);
        setError(err.message);
        
        // Mock data for development
        const mockData = {
          projects: [
            {
              id: 'proj_001',
              name: 'AI Consulting Platform Development',
              description: 'Development of comprehensive AI consulting platform with autonomous agents',
              status: 'in_progress',
              priority: 'high',
              startDate: '2024-06-01',
              endDate: '2024-09-30',
              completionPercentage: 68,
              manager: 'Project Manager Alpha',
              team: ['Development Agent', 'QA Agent', 'Design Agent', 'DevOps Agent'],
              budget: {
                allocated: 250000,
                spent: 170000,
                remaining: 80000
              },
              health: 'good',
              riskLevel: 'medium',
              category: 'Product Development',
              tags: ['AI', 'Platform', 'Critical'],
              milestones: [
                {
                  id: 'ms_001',
                  name: 'Architecture Design Complete',
                  status: 'completed',
                  dueDate: '2024-06-30',
                  completedDate: '2024-06-28',
                  dependencies: []
                },
                {
                  id: 'ms_002',
                  name: 'Core Platform MVP',
                  status: 'completed',
                  dueDate: '2024-08-15',
                  completedDate: '2024-08-12',
                  dependencies: ['ms_001']
                },
                {
                  id: 'ms_003',
                  name: 'Agent Integration Phase 1',
                  status: 'in_progress',
                  dueDate: '2024-09-01',
                  completedDate: null,
                  dependencies: ['ms_002']
                },
                {
                  id: 'ms_004',
                  name: 'Beta Testing & Optimization',
                  status: 'pending',
                  dueDate: '2024-09-20',
                  completedDate: null,
                  dependencies: ['ms_003']
                }
              ],
              kpis: {
                codeQuality: 92,
                testCoverage: 87,
                performanceScore: 89,
                securityScore: 94
              },
              lastUpdate: '2024-07-22'
            },
            {
              id: 'proj_002',
              name: 'Enterprise Dashboard Enhancement',
              description: 'Complete redesign and enhancement of enterprise operations dashboard',
              status: 'in_progress',
              priority: 'high',
              startDate: '2024-07-01',
              endDate: '2024-08-31',
              completionPercentage: 75,
              manager: 'UI/UX Manager Beta',
              team: ['Frontend Agent', 'Backend Agent', 'Design Agent'],
              budget: {
                allocated: 150000,
                spent: 112500,
                remaining: 37500
              },
              health: 'excellent',
              riskLevel: 'low',
              category: 'UI/UX Enhancement',
              tags: ['Dashboard', 'Frontend', 'Operations'],
              milestones: [
                {
                  id: 'ms_005',
                  name: 'Requirements Analysis',
                  status: 'completed',
                  dueDate: '2024-07-10',
                  completedDate: '2024-07-08',
                  dependencies: []
                },
                {
                  id: 'ms_006',
                  name: 'Design System Creation',
                  status: 'completed',
                  dueDate: '2024-07-20',
                  completedDate: '2024-07-18',
                  dependencies: ['ms_005']
                },
                {
                  id: 'ms_007',
                  name: 'Component Development',
                  status: 'in_progress',
                  dueDate: '2024-08-10',
                  completedDate: null,
                  dependencies: ['ms_006']
                },
                {
                  id: 'ms_008',
                  name: 'Integration & Testing',
                  status: 'pending',
                  dueDate: '2024-08-25',
                  completedDate: null,
                  dependencies: ['ms_007']
                }
              ],
              kpis: {
                designConsistency: 96,
                userSatisfaction: 91,
                performanceScore: 94,
                accessibility: 98
              },
              lastUpdate: '2024-07-22'
            },
            {
              id: 'proj_003',
              name: 'Business Intelligence Pipeline',
              description: 'Implementation of comprehensive BI pipeline for automated analytics and reporting',
              status: 'planning',
              priority: 'medium',
              startDate: '2024-08-01',
              endDate: '2024-11-30',
              completionPercentage: 15,
              manager: 'Analytics Manager Gamma',
              team: ['Data Engineer Agent', 'BI Analyst Agent', 'Research Agent'],
              budget: {
                allocated: 180000,
                spent: 27000,
                remaining: 153000
              },
              health: 'good',
              riskLevel: 'medium',
              category: 'Data & Analytics',
              tags: ['BI', 'Analytics', 'Automation'],
              milestones: [
                {
                  id: 'ms_009',
                  name: 'Data Architecture Design',
                  status: 'in_progress',
                  dueDate: '2024-08-20',
                  completedDate: null,
                  dependencies: []
                },
                {
                  id: 'ms_010',
                  name: 'ETL Pipeline Development',
                  status: 'pending',
                  dueDate: '2024-09-15',
                  completedDate: null,
                  dependencies: ['ms_009']
                },
                {
                  id: 'ms_011',
                  name: 'Analytics Engine Implementation',
                  status: 'pending',
                  dueDate: '2024-10-15',
                  completedDate: null,
                  dependencies: ['ms_010']
                },
                {
                  id: 'ms_012',
                  name: 'Reporting Dashboard',
                  status: 'pending',
                  dueDate: '2024-11-15',
                  completedDate: null,
                  dependencies: ['ms_011']
                }
              ],
              kpis: {
                dataQuality: 0,
                pipelineReliability: 0,
                queryPerformance: 0,
                reportAccuracy: 0
              },
              lastUpdate: '2024-07-22'
            },
            {
              id: 'proj_004',
              name: 'Security & Compliance Upgrade',
              description: 'Enhanced security measures and compliance framework implementation',
              status: 'completed',
              priority: 'critical',
              startDate: '2024-04-01',
              endDate: '2024-06-30',
              completionPercentage: 100,
              manager: 'Security Manager Delta',
              team: ['Security Agent', 'Compliance Agent', 'DevSecOps Agent'],
              budget: {
                allocated: 120000,
                spent: 118500,
                remaining: 1500
              },
              health: 'excellent',
              riskLevel: 'low',
              category: 'Security & Compliance',
              tags: ['Security', 'Compliance', 'Critical'],
              milestones: [
                {
                  id: 'ms_013',
                  name: 'Security Audit & Assessment',
                  status: 'completed',
                  dueDate: '2024-04-20',
                  completedDate: '2024-04-18',
                  dependencies: []
                },
                {
                  id: 'ms_014',
                  name: 'Compliance Framework Design',
                  status: 'completed',
                  dueDate: '2024-05-10',
                  completedDate: '2024-05-08',
                  dependencies: ['ms_013']
                },
                {
                  id: 'ms_015',
                  name: 'Security Controls Implementation',
                  status: 'completed',
                  dueDate: '2024-06-15',
                  completedDate: '2024-06-12',
                  dependencies: ['ms_014']
                },
                {
                  id: 'ms_016',
                  name: 'Compliance Verification',
                  status: 'completed',
                  dueDate: '2024-06-28',
                  completedDate: '2024-06-25',
                  dependencies: ['ms_015']
                }
              ],
              kpis: {
                securityScore: 98,
                complianceScore: 97,
                vulnerabilityCount: 2,
                incidentResponse: 99
              },
              lastUpdate: '2024-06-30'
            }
          ],
          metrics: {
            totalProjects: 4,
            activeProjects: 3,
            completedProjects: 1,
            overallProgress: 64.5,
            totalBudget: 700000,
            spentBudget: 428000,
            onTimeDelivery: 87,
            qualityScore: 93,
            riskProjects: 1,
            criticalMilestones: 2
          },
          dependencies: [
            {
              from: 'proj_001',
              to: 'proj_002',
              type: 'finish_to_start',
              description: 'Dashboard enhancement depends on platform completion'
            },
            {
              from: 'proj_002',
              to: 'proj_003',
              type: 'start_to_start',
              description: 'BI pipeline can start after dashboard design completion'
            }
          ],
          resources: [
            {
              name: 'Development Team',
              utilization: 92,
              capacity: 100,
              skills: ['React', 'Node.js', 'Python', 'AI/ML']
            },
            {
              name: 'Design Team',
              utilization: 78,
              capacity: 100,
              skills: ['UI/UX', 'Design Systems', 'Prototyping']
            },
            {
              name: 'DevOps Team',
              utilization: 85,
              capacity: 100,
              skills: ['AWS', 'Docker', 'CI/CD', 'Monitoring']
            }
          ]
        };
        setData(mockData);
      } finally {
        setLoading(false);
      }
    };

    loadProjectData();
    const interval = setInterval(loadProjectData, 180000); // Refresh every 3 minutes
    return () => clearInterval(interval);
  }, [timeFilter, statusFilter, projectData]);

  const handleProjectUpdate = (projectId, updates) => {
    if (onProjectUpdate) {
      onProjectUpdate(projectId, updates);
    }
    // Update local data
    setData(prev => ({
      ...prev,
      projects: prev.projects.map(project => 
        project.id === projectId ? { ...project, ...updates } : project
      )
    }));
  };

  const handleMilestoneUpdate = (projectId, milestoneId, updates) => {
    if (onMilestoneUpdate) {
      onMilestoneUpdate(projectId, milestoneId, updates);
    }
    // Update local data
    setData(prev => ({
      ...prev,
      projects: prev.projects.map(project => 
        project.id === projectId ? {
          ...project,
          milestones: project.milestones.map(milestone =>
            milestone.id === milestoneId ? { ...milestone, ...updates } : milestone
          )
        } : project
      )
    }));
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0
    }).format(amount);
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    const colors = {
      planning: '#f59e0b',
      in_progress: '#3b82f6',
      completed: '#10b981',
      on_hold: '#ef4444',
      cancelled: '#6b7280'
    };
    return colors[status] || '#6b7280';
  };

  const getHealthColor = (health) => {
    const colors = {
      excellent: '#10b981',
      good: '#3b82f6',
      fair: '#f59e0b',
      poor: '#ef4444'
    };
    return colors[health] || '#6b7280';
  };

  const getRiskColor = (risk) => {
    const colors = {
      low: '#10b981',
      medium: '#f59e0b',
      high: '#ef4444',
      critical: '#dc2626'
    };
    return colors[risk] || '#6b7280';
  };

  const getFilteredProjects = () => {
    let filtered = data.projects;
    
    if (statusFilter !== 'all') {
      filtered = filtered.filter(project => project.status === statusFilter);
    }
    
    if (timeFilter !== 'all') {
      const now = new Date();
      filtered = filtered.filter(project => {
        const endDate = new Date(project.endDate);
        switch (timeFilter) {
          case 'current':
            return project.status === 'in_progress';
          case 'upcoming':
            return endDate > now && project.status !== 'completed';
          case 'overdue':
            return endDate < now && project.status !== 'completed';
          default:
            return true;
        }
      });
    }
    
    return filtered;
  };

  if (loading) {
    return (
      <div className="project-status-tracking loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading project data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="project-status-tracking error">
        <div className="error-message">
          <h3>Error Loading Project Data</h3>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const filteredProjects = getFilteredProjects();

  return (
    <div className="project-status-tracking">
      {/* Header */}
      <div className="panel-header">
        <div className="header-content">
          <h2>Project Status & Milestone Tracking</h2>
          <p>Monitor project progress, milestones, and resource allocation</p>
        </div>
        <div className="header-controls">
          <select 
            value={statusFilter} 
            onChange={(e) => setStatusFilter(e.target.value)}
            className="status-filter"
          >
            <option value="all">All Status</option>
            <option value="planning">Planning</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="on_hold">On Hold</option>
          </select>
          <select 
            value={timeFilter} 
            onChange={(e) => setTimeFilter(e.target.value)}
            className="time-filter"
          >
            <option value="all">All Projects</option>
            <option value="current">Current</option>
            <option value="upcoming">Upcoming</option>
            <option value="overdue">Overdue</option>
          </select>
          <select 
            value={viewMode} 
            onChange={(e) => setViewMode(e.target.value)}
            className="view-mode-selector"
          >
            <option value="overview">Overview</option>
            <option value="timeline">Timeline</option>
            <option value="milestones">Milestones</option>
            <option value="resources">Resources</option>
          </select>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="project-metrics">
        <div className="metric-card">
          <div className="metric-icon">📊</div>
          <div className="metric-content">
            <div className="metric-value">{data.metrics.totalProjects}</div>
            <div className="metric-label">Total Projects</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">🚀</div>
          <div className="metric-content">
            <div className="metric-value">{data.metrics.activeProjects}</div>
            <div className="metric-label">Active Projects</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">💰</div>
          <div className="metric-content">
            <div className="metric-value">{formatCurrency(data.metrics.totalBudget)}</div>
            <div className="metric-label">Total Budget</div>
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon">📈</div>
          <div className="metric-content">
            <div className="metric-value">{data.metrics.overallProgress}%</div>
            <div className="metric-label">Overall Progress</div>
          </div>
        </div>
      </div>

      {/* Overview View */}
      {viewMode === 'overview' && (
        <div className="projects-overview">
          <div className="projects-grid">
            {filteredProjects.map((project) => (
              <div 
                key={project.id} 
                className="project-card"
                onClick={() => setSelectedProject(project)}
              >
                <div className="project-header">
                  <div className="project-title">
                    <h3>{project.name}</h3>
                    <div className="project-meta">
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(project.status) }}
                      >
                        {project.status.replace('_', ' ').toUpperCase()}
                      </span>
                      <span className="priority-badge priority-{project.priority}">
                        {project.priority.toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="project-health">
                    <div 
                      className="health-indicator"
                      style={{ backgroundColor: getHealthColor(project.health) }}
                      title={`Health: ${project.health}`}
                    ></div>
                  </div>
                </div>

                <div className="project-description">
                  <p>{project.description}</p>
                </div>

                <div className="project-progress">
                  <div className="progress-header">
                    <span>Progress</span>
                    <span>{project.completionPercentage}%</span>
                  </div>
                  <div className="progress-bar">
                    <div 
                      className="progress-fill"
                      style={{ width: `${project.completionPercentage}%` }}
                    ></div>
                  </div>
                </div>

                <div className="project-timeline">
                  <div className="timeline-item">
                    <span className="timeline-label">Start:</span>
                    <span className="timeline-date">{formatDate(project.startDate)}</span>
                  </div>
                  <div className="timeline-item">
                    <span className="timeline-label">End:</span>
                    <span className="timeline-date">{formatDate(project.endDate)}</span>
                  </div>
                </div>

                <div className="project-budget">
                  <div className="budget-header">
                    <span>Budget</span>
                    <span>{formatCurrency(project.budget.spent)} / {formatCurrency(project.budget.allocated)}</span>
                  </div>
                  <div className="budget-bar">
                    <div 
                      className="budget-fill"
                      style={{ width: `${(project.budget.spent / project.budget.allocated) * 100}%` }}
                    ></div>
                  </div>
                </div>

                <div className="project-team">
                  <div className="team-header">
                    <span>Team ({project.team.length})</span>
                    <span 
                      className="risk-indicator"
                      style={{ color: getRiskColor(project.riskLevel) }}
                    >
                      Risk: {project.riskLevel}
                    </span>
                  </div>
                  <div className="team-members">
                    {project.team.slice(0, 3).map((member, index) => (
                      <span key={index} className="team-member">{member}</span>
                    ))}
                    {project.team.length > 3 && (
                      <span className="team-more">+{project.team.length - 3} more</span>
                    )}
                  </div>
                </div>

                <div className="project-milestones-summary">
                  <div className="milestones-stats">
                    <span className="completed-milestones">
                      {project.milestones.filter(m => m.status === 'completed').length} completed
                    </span>
                    <span className="total-milestones">
                      / {project.milestones.length} total
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Timeline View */}
      {viewMode === 'timeline' && (
        <div className="timeline-view">
          <div className="timeline-container">
            <div className="timeline-header">
              <h3>Project Timeline</h3>
            </div>
            <div className="timeline-projects">
              {filteredProjects.map((project) => {
                const startDate = new Date(project.startDate);
                const endDate = new Date(project.endDate);
                const duration = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));
                
                return (
                  <div key={project.id} className="timeline-project">
                    <div className="timeline-project-info">
                      <h4>{project.name}</h4>
                      <span className="timeline-duration">{duration} days</span>
                    </div>
                    <div className="timeline-bar-container">
                      <div 
                        className="timeline-bar"
                        style={{ backgroundColor: getStatusColor(project.status) }}
                      >
                        <div 
                          className="timeline-progress"
                          style={{ width: `${project.completionPercentage}%` }}
                        ></div>
                      </div>
                      <div className="timeline-dates">
                        <span className="start-date">{formatDate(project.startDate)}</span>
                        <span className="end-date">{formatDate(project.endDate)}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {/* Milestones View */}
      {viewMode === 'milestones' && (
        <div className="milestones-view">
          <div className="milestones-grid">
            {filteredProjects.map((project) => (
              <div key={project.id} className="project-milestones">
                <div className="milestones-header">
                  <h3>{project.name}</h3>
                  <span className="milestone-count">
                    {project.milestones.length} milestones
                  </span>
                </div>
                <div className="milestones-list">
                  {project.milestones.map((milestone) => (
                    <div 
                      key={milestone.id} 
                      className={`milestone-item ${milestone.status}`}
                    >
                      <div className="milestone-status">
                        <div className={`status-icon ${milestone.status}`}>
                          {milestone.status === 'completed' && '✓'}
                          {milestone.status === 'in_progress' && '⏳'}
                          {milestone.status === 'pending' && '○'}
                        </div>
                      </div>
                      <div className="milestone-content">
                        <div className="milestone-name">{milestone.name}</div>
                        <div className="milestone-date">
                          Due: {formatDate(milestone.dueDate)}
                          {milestone.completedDate && (
                            <span className="completed-date">
                              (Completed: {formatDate(milestone.completedDate)})
                            </span>
                          )}
                        </div>
                        {milestone.dependencies.length > 0 && (
                          <div className="milestone-dependencies">
                            Dependencies: {milestone.dependencies.length}
                          </div>
                        )}
                      </div>
                      <div className="milestone-actions">
                        <select 
                          value={milestone.status}
                          onChange={(e) => handleMilestoneUpdate(project.id, milestone.id, { status: e.target.value })}
                          className="milestone-status-selector"
                        >
                          <option value="pending">Pending</option>
                          <option value="in_progress">In Progress</option>
                          <option value="completed">Completed</option>
                        </select>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resources View */}
      {viewMode === 'resources' && (
        <div className="resources-view">
          <div className="resources-grid">
            <div className="resource-utilization">
              <h3>Resource Utilization</h3>
              <div className="resources-list">
                {data.resources.map((resource, index) => (
                  <div key={index} className="resource-item">
                    <div className="resource-header">
                      <span className="resource-name">{resource.name}</span>
                      <span className="resource-utilization-percent">
                        {resource.utilization}% utilized
                      </span>
                    </div>
                    <div className="resource-bar">
                      <div 
                        className="resource-fill"
                        style={{ 
                          width: `${resource.utilization}%`,
                          backgroundColor: resource.utilization > 90 ? '#ef4444' : 
                                         resource.utilization > 75 ? '#f59e0b' : '#10b981'
                        }}
                      ></div>
                    </div>
                    <div className="resource-skills">
                      {resource.skills.map((skill, skillIndex) => (
                        <span key={skillIndex} className="skill-tag">{skill}</span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="project-allocation">
              <h3>Project Allocation</h3>
              <div className="allocation-chart">
                {filteredProjects.map((project) => (
                  <div key={project.id} className="allocation-item">
                    <div className="allocation-project">
                      <span className="project-name">{project.name}</span>
                      <span className="team-size">{project.team.length} members</span>
                    </div>
                    <div className="allocation-percentage">
                      {Math.round((project.team.length / filteredProjects.reduce((acc, p) => acc + p.team.length, 0)) * 100)}%
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Project Details Modal */}
      {selectedProject && (
        <div className="project-details-modal">
          <div className="modal-overlay" onClick={() => setSelectedProject(null)}></div>
          <div className="modal-content">
            <div className="modal-header">
              <h2>{selectedProject.name}</h2>
              <button 
                className="close-button"
                onClick={() => setSelectedProject(null)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="project-details-grid">
                <div className="detail-section">
                  <h3>Project Information</h3>
                  <div className="detail-items">
                    <div className="detail-item">
                      <label>Status:</label>
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(selectedProject.status) }}
                      >
                        {selectedProject.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <label>Priority:</label>
                      <span className={`priority-badge priority-${selectedProject.priority}`}>
                        {selectedProject.priority.toUpperCase()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <label>Health:</label>
                      <span style={{ color: getHealthColor(selectedProject.health) }}>
                        {selectedProject.health.toUpperCase()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <label>Risk Level:</label>
                      <span style={{ color: getRiskColor(selectedProject.riskLevel) }}>
                        {selectedProject.riskLevel.toUpperCase()}
                      </span>
                    </div>
                    <div className="detail-item">
                      <label>Manager:</label>
                      <span>{selectedProject.manager}</span>
                    </div>
                    <div className="detail-item">
                      <label>Category:</label>
                      <span>{selectedProject.category}</span>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Timeline & Progress</h3>
                  <div className="detail-items">
                    <div className="detail-item">
                      <label>Start Date:</label>
                      <span>{formatDate(selectedProject.startDate)}</span>
                    </div>
                    <div className="detail-item">
                      <label>End Date:</label>
                      <span>{formatDate(selectedProject.endDate)}</span>
                    </div>
                    <div className="detail-item">
                      <label>Progress:</label>
                      <span>{selectedProject.completionPercentage}%</span>
                    </div>
                    <div className="detail-item">
                      <label>Last Update:</label>
                      <span>{formatDate(selectedProject.lastUpdate)}</span>
                    </div>
                  </div>
                  <div className="progress-visualization">
                    <div className="progress-bar large">
                      <div 
                        className="progress-fill"
                        style={{ width: `${selectedProject.completionPercentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Budget Information</h3>
                  <div className="budget-details">
                    <div className="budget-item">
                      <label>Allocated:</label>
                      <span>{formatCurrency(selectedProject.budget.allocated)}</span>
                    </div>
                    <div className="budget-item">
                      <label>Spent:</label>
                      <span>{formatCurrency(selectedProject.budget.spent)}</span>
                    </div>
                    <div className="budget-item">
                      <label>Remaining:</label>
                      <span>{formatCurrency(selectedProject.budget.remaining)}</span>
                    </div>
                  </div>
                  <div className="budget-visualization">
                    <div className="budget-bar large">
                      <div 
                        className="budget-fill"
                        style={{ width: `${(selectedProject.budget.spent / selectedProject.budget.allocated) * 100}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="detail-section full-width">
                  <h3>Key Performance Indicators</h3>
                  <div className="kpi-grid">
                    {Object.entries(selectedProject.kpis).map(([key, value]) => (
                      <div key={key} className="kpi-item">
                        <div className="kpi-label">
                          {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                        </div>
                        <div className="kpi-value">{value}{typeof value === 'number' && value <= 100 ? '%' : ''}</div>
                        <div className="kpi-bar">
                          <div 
                            className="kpi-fill"
                            style={{ width: `${Math.min(value, 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="detail-section full-width">
                  <h3>Team Members</h3>
                  <div className="team-list">
                    {selectedProject.team.map((member, index) => (
                      <span key={index} className="team-member-badge">{member}</span>
                    ))}
                  </div>
                </div>

                <div className="detail-section full-width">
                  <h3>Project Tags</h3>
                  <div className="tags-list">
                    {selectedProject.tags.map((tag, index) => (
                      <span key={index} className="project-tag">{tag}</span>
                    ))}
                  </div>
                </div>

                <div className="detail-section full-width">
                  <h3>Milestones Timeline</h3>
                  <div className="milestones-timeline">
                    {selectedProject.milestones.map((milestone) => (
                      <div key={milestone.id} className={`timeline-milestone ${milestone.status}`}>
                        <div className="milestone-marker">
                          <div className={`marker-icon ${milestone.status}`}>
                            {milestone.status === 'completed' && '✓'}
                            {milestone.status === 'in_progress' && '⏳'}
                            {milestone.status === 'pending' && '○'}
                          </div>
                        </div>
                        <div className="milestone-info">
                          <div className="milestone-title">{milestone.name}</div>
                          <div className="milestone-dates">
                            Due: {formatDate(milestone.dueDate)}
                            {milestone.completedDate && (
                              <span> | Completed: {formatDate(milestone.completedDate)}</span>
                            )}
                          </div>
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
    </div>
  );
};

export default ProjectStatusTracking;
