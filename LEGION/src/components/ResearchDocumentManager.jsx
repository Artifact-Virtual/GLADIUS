import React, { useState, useEffect, useCallback } from 'react';

const ResearchDocumentManager = () => {
  const [activeView, setActiveView] = useState('documents');
  const [documents, setDocuments] = useState([]);
  const [folders, setFolders] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [collaborations, setCollaborations] = useState([]);
  const [archives, setArchives] = useState([]);
  const [analytics, setAnalytics] = useState([]);
  const [workflows, setWorkflows] = useState([]);
  const [selectedDocument, setSelectedDocument] = useState(null);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [currentPath, setCurrentPath] = useState(['Root']);
  const [documentFilters, setDocumentFilters] = useState({
    type: 'all',
    status: 'all',
    category: 'all',
    author: 'all',
    dateRange: 'all',
    size: 'all',
    tags: []
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('modified');
  const [sortOrder, setSortOrder] = useState('desc');
  const [viewMode, setViewMode] = useState('grid');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);
  const [uploadModal, setUploadModal] = useState(false);
  const [newFolderModal, setNewFolderModal] = useState(false);
  const [documentModal, setDocumentModal] = useState(false);
  const [shareModal, setShareModal] = useState(false);
  const [versionModal, setVersionModal] = useState(false);
  const [previewModal, setPreviewModal] = useState(false);
  const [selectedItems, setSelectedItems] = useState([]);
  const [bulkAction, setBulkAction] = useState('');

  // Mock data generators
  const generateDocuments = useCallback(() => {
    const documentTypes = ['research-report', 'analysis', 'proposal', 'presentation', 'whitepaper', 'case-study', 'manual', 'specification'];
    const statuses = ['draft', 'review', 'approved', 'published', 'archived'];
    const categories = ['market-research', 'competitive-analysis', 'financial', 'technical', 'strategic', 'operational', 'compliance', 'hr'];
    const authors = ['Dr. Sarah Chen', 'Michael Rodriguez', 'Emma Thompson', 'David Kim', 'Lisa Zhang', 'Robert Johnson', 'Maria Garcia', 'James Wilson'];
    const extensions = ['.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md'];
    
    const documentTitles = [
      'Q4 2024 Market Analysis Report', 'Competitive Intelligence Summary', 'Financial Performance Review',
      'Strategic Planning Framework', 'Operational Efficiency Study', 'Customer Satisfaction Analysis',
      'Technology Innovation Roadmap', 'Risk Assessment Documentation', 'Compliance Audit Report',
      'Product Development Proposal', 'Market Expansion Strategy', 'Digital Transformation Plan',
      'Supply Chain Optimization', 'Brand Positioning Research', 'Customer Journey Mapping',
      'Performance Metrics Dashboard', 'Investment Analysis Report', 'Partnership Evaluation',
      'Process Improvement Guide', 'Quality Assurance Manual', 'Training Documentation',
      'Policy Framework Document', 'Implementation Checklist', 'Best Practices Guide'
    ];

    return Array.from({ length: 20 }, (_, index) => ({
      id: `doc-${index + 1}`,
      title: documentTitles[index] || `Research Document ${index + 1}`,
      type: documentTypes[Math.floor(Math.random() * documentTypes.length)],
      status: statuses[Math.floor(Math.random() * statuses.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      author: authors[Math.floor(Math.random() * authors.length)],
      size: (Math.random() * 10 + 0.5).toFixed(2) + ' MB',
      extension: extensions[Math.floor(Math.random() * extensions.length)],
      createdAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      modifiedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      accessedAt: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      version: `v${Math.floor(Math.random() * 5) + 1}.${Math.floor(Math.random() * 10)}`,
      versions: Math.floor(Math.random() * 8) + 1,
      downloads: Math.floor(Math.random() * 500) + 50,
      views: Math.floor(Math.random() * 1000) + 100,
      shares: Math.floor(Math.random() * 25) + 5,
      comments: Math.floor(Math.random() * 15) + 2,
      tags: ['research', 'analysis', 'strategic', 'important', 'confidential', 'draft', 'published'].slice(0, Math.floor(Math.random() * 4) + 2),
      description: `Comprehensive research document containing detailed analysis and insights for business decision-making and strategic planning purposes.`,
      folder: currentPath[currentPath.length - 1],
      isStarred: Math.random() > 0.7,
      isShared: Math.random() > 0.5,
      hasComments: Math.random() > 0.6,
      isLocked: Math.random() > 0.8,
      permissions: {
        read: true,
        write: Math.random() > 0.3,
        share: Math.random() > 0.4,
        delete: Math.random() > 0.6
      },
      collaborators: Math.floor(Math.random() * 5) + 1,
      lastEditor: authors[Math.floor(Math.random() * authors.length)],
      checksum: Math.random().toString(36).substring(2, 15),
      language: ['en', 'es', 'fr', 'de', 'zh'][Math.floor(Math.random() * 5)],
      readingTime: Math.floor(Math.random() * 45) + 5,
      wordCount: Math.floor(Math.random() * 5000) + 1000
    }));
  }, [currentPath]);

  const generateFolders = useCallback(() => {
    const folderNames = [
      'Market Research', 'Competitive Analysis', 'Financial Reports', 'Strategic Planning',
      'Operational Documents', 'Technical Specifications', 'Compliance Records', 'HR Policies',
      'Product Development', 'Customer Research', 'Partnership Agreements', 'Legal Documents',
      'Training Materials', 'Process Documentation', 'Quality Assurance', 'Risk Management'
    ];

    return Array.from({ length: 12 }, (_, index) => ({
      id: `folder-${index + 1}`,
      name: folderNames[index] || `Folder ${index + 1}`,
      path: [...currentPath, folderNames[index] || `Folder ${index + 1}`],
      documentCount: Math.floor(Math.random() * 25) + 5,
      subfolderCount: Math.floor(Math.random() * 8) + 2,
      size: (Math.random() * 500 + 50).toFixed(1) + ' MB',
      createdAt: new Date(Date.now() - Math.random() * 180 * 24 * 60 * 60 * 1000).toISOString(),
      modifiedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      owner: ['Research Team', 'Analytics Team', 'Strategy Team', 'Operations Team'][Math.floor(Math.random() * 4)],
      permissions: {
        read: true,
        write: Math.random() > 0.2,
        share: Math.random() > 0.3,
        delete: Math.random() > 0.7
      },
      isShared: Math.random() > 0.4,
      collaborators: Math.floor(Math.random() * 8) + 2,
      tags: ['important', 'archived', 'active', 'shared', 'restricted'].slice(0, Math.floor(Math.random() * 3) + 1),
      description: `Organized collection of documents related to ${folderNames[index] || 'business operations'} and strategic initiatives.`
    }));
  }, [currentPath]);

  const generateTemplates = useCallback(() => {
    const templateTypes = ['report', 'proposal', 'analysis', 'presentation', 'manual', 'policy'];
    const templateNames = [
      'Market Research Report Template', 'Business Proposal Template', 'Financial Analysis Template',
      'Strategic Plan Template', 'Project Charter Template', 'Risk Assessment Template',
      'Competitive Analysis Template', 'Customer Survey Template', 'Process Documentation Template',
      'Training Manual Template', 'Policy Document Template', 'Case Study Template'
    ];

    return Array.from({ length: 10 }, (_, index) => ({
      id: `template-${index + 1}`,
      name: templateNames[index] || `Template ${index + 1}`,
      type: templateTypes[Math.floor(Math.random() * templateTypes.length)],
      category: ['business', 'technical', 'legal', 'hr', 'finance'][Math.floor(Math.random() * 5)],
      usage: Math.floor(Math.random() * 100) + 10,
      rating: (Math.random() * 2 + 3).toFixed(1),
      createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000).toISOString(),
      updatedAt: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
      author: 'Template Team',
      version: `v${Math.floor(Math.random() * 3) + 1}.${Math.floor(Math.random() * 5)}`,
      description: `Professional template for creating standardized ${templateTypes[Math.floor(Math.random() * templateTypes.length)]} documents with consistent formatting and structure.`,
      tags: ['template', 'standard', 'professional', 'business'].slice(0, Math.floor(Math.random() * 3) + 2),
      preview: `/templates/preview-${index + 1}.png`,
      downloadUrl: `/templates/download-${index + 1}`,
      size: (Math.random() * 2 + 0.1).toFixed(2) + ' MB'
    }));
  }, []);

  const generateCollaborations = useCallback(() => {
    const projectNames = [
      'Market Expansion Study', 'Digital Transformation Initiative', 'Competitive Analysis Project',
      'Customer Experience Research', 'Product Development Plan', 'Risk Assessment Review',
      'Strategic Planning Session', 'Operational Efficiency Study', 'Brand Positioning Analysis',
      'Technology Innovation Research'
    ];

    return Array.from({ length: 8 }, (_, index) => ({
      id: `collab-${index + 1}`,
      projectName: projectNames[index] || `Collaboration Project ${index + 1}`,
      documents: Math.floor(Math.random() * 15) + 5,
      collaborators: Math.floor(Math.random() * 8) + 3,
      activeUsers: Math.floor(Math.random() * 5) + 1,
      lastActivity: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
      status: ['active', 'paused', 'completed', 'planning'][Math.floor(Math.random() * 4)],
      deadline: new Date(Date.now() + Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString(),
      progress: Math.floor(Math.random() * 100),
      owner: ['Research Team', 'Strategy Team', 'Analytics Team'][Math.floor(Math.random() * 3)],
      priority: ['high', 'medium', 'low'][Math.floor(Math.random() * 3)],
      budget: (Math.random() * 100 + 20).toFixed(0) + 'K',
      description: `Collaborative research project focused on ${projectNames[index] || 'business development'} with multiple team members contributing to document creation and analysis.`
    }));
  }, []);

  const generateArchives = useCallback(() => {
    const archiveTypes = ['yearly', 'quarterly', 'monthly', 'project-based'];
    
    return Array.from({ length: 6 }, (_, index) => ({
      id: `archive-${index + 1}`,
      name: `Archive ${2024 - index}`,
      type: archiveTypes[Math.floor(Math.random() * archiveTypes.length)],
      documentCount: Math.floor(Math.random() * 500) + 100,
      size: (Math.random() * 5000 + 1000).toFixed(0) + ' MB',
      createdAt: new Date(2024 - index, 0, 1).toISOString(),
      lastAccessed: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
      status: ['active', 'sealed', 'compressed'][Math.floor(Math.random() * 3)],
      retentionPolicy: `${Math.floor(Math.random() * 5) + 5} years`,
      accessLevel: ['public', 'restricted', 'confidential'][Math.floor(Math.random() * 3)],
      backupStatus: ['completed', 'in-progress', 'pending'][Math.floor(Math.random() * 3)],
      description: `Archive containing historical documents and records from ${2024 - index} with proper retention and compliance management.`
    }));
  }, []);

  const generateAnalytics = useCallback(() => {
    return [
      {
        metric: 'Total Documents',
        value: Math.floor(Math.random() * 5000) + 2500,
        change: (Math.random() * 20 - 10).toFixed(1),
        trend: Math.random() > 0.5 ? 'up' : 'down'
      },
      {
        metric: 'Storage Used',
        value: (Math.random() * 500 + 250).toFixed(1) + ' GB',
        change: (Math.random() * 15 - 5).toFixed(1),
        trend: 'up'
      },
      {
        metric: 'Active Collaborations',
        value: Math.floor(Math.random() * 50) + 25,
        change: (Math.random() * 30 - 15).toFixed(1),
        trend: Math.random() > 0.5 ? 'up' : 'down'
      },
      {
        metric: 'Daily Downloads',
        value: Math.floor(Math.random() * 200) + 100,
        change: (Math.random() * 25 - 10).toFixed(1),
        trend: Math.random() > 0.5 ? 'up' : 'down'
      }
    ];
  }, []);

  const generateWorkflows = useCallback(() => {
    const workflowTypes = ['approval', 'review', 'publishing', 'archival', 'collaboration'];
    const workflowNames = [
      'Document Approval Workflow', 'Peer Review Process', 'Publication Pipeline',
      'Archive Management Flow', 'Collaboration Workflow', 'Quality Assurance Process',
      'Version Control Flow', 'Compliance Review Workflow'
    ];

    return Array.from({ length: 6 }, (_, index) => ({
      id: `workflow-${index + 1}`,
      name: workflowNames[index] || `Workflow ${index + 1}`,
      type: workflowTypes[Math.floor(Math.random() * workflowTypes.length)],
      status: ['active', 'paused', 'disabled'][Math.floor(Math.random() * 3)],
      documentsInFlow: Math.floor(Math.random() * 50) + 10,
      averageTime: `${Math.floor(Math.random() * 5) + 1} days`,
      completionRate: Math.floor(Math.random() * 30) + 70,
      steps: Math.floor(Math.random() * 6) + 3,
      automationLevel: Math.floor(Math.random() * 60) + 40,
      lastUsed: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
      createdBy: 'Workflow Admin',
      description: `Automated workflow for managing ${workflowTypes[Math.floor(Math.random() * workflowTypes.length)]} processes with built-in quality controls and notifications.`
    }));
  }, []);

  // Data loading
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Simulate API calls with realistic delays
        await new Promise(resolve => setTimeout(resolve, 900));
        
        setDocuments(generateDocuments());
        setFolders(generateFolders());
        setTemplates(generateTemplates());
        setCollaborations(generateCollaborations());
        setArchives(generateArchives());
        setAnalytics(generateAnalytics());
        setWorkflows(generateWorkflows());
        
      } catch (error) {
        console.error('Error loading research document data:', error);
        setError('Failed to load research document data. Please try again.');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [generateDocuments, generateFolders, generateTemplates, generateCollaborations, generateArchives, generateAnalytics, generateWorkflows]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    setDocuments(generateDocuments());
    setFolders(generateFolders());
    setTemplates(generateTemplates());
    setCollaborations(generateCollaborations());
    setArchives(generateArchives());
    setAnalytics(generateAnalytics());
    setWorkflows(generateWorkflows());
    
    setRefreshing(false);
  };

  // Filter and search logic
  const filteredDocuments = documents.filter(doc => {
    const matchesFilters = 
      (documentFilters.type === 'all' || doc.type === documentFilters.type) &&
      (documentFilters.status === 'all' || doc.status === documentFilters.status) &&
      (documentFilters.category === 'all' || doc.category === documentFilters.category) &&
      (documentFilters.author === 'all' || doc.author === documentFilters.author);
    
    const matchesSearch = !searchQuery || 
      doc.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      doc.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    
    return matchesFilters && matchesSearch;
  });

  const sortData = (data) => {
    return data.sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'modified':
          aValue = new Date(a.modifiedAt);
          bValue = new Date(b.modifiedAt);
          break;
        case 'created':
          aValue = new Date(a.createdAt);
          bValue = new Date(b.createdAt);
          break;
        case 'name':
          aValue = a.title || a.name;
          bValue = b.title || b.name;
          break;
        case 'size':
          aValue = parseFloat(a.size);
          bValue = parseFloat(b.size);
          break;
        case 'type':
          aValue = a.type;
          bValue = b.type;
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

  const sortedDocuments = sortData([...filteredDocuments]);
  const sortedFolders = sortData([...folders]);

  const getStatusColor = (status) => {
    const colors = {
      draft: '#6c757d',
      review: '#ffc107',
      approved: '#28a745',
      published: '#007bff',
      archived: '#6f42c1',
      active: '#28a745',
      paused: '#ffc107',
      completed: '#17a2b8',
      planning: '#fd7e14',
      disabled: '#dc3545'
    };
    return colors[status] || '#666';
  };

  const getTypeIcon = (type) => {
    const icons = {
      'research-report': 'fas fa-file-alt',
      'analysis': 'fas fa-chart-bar',
      'proposal': 'fas fa-file-contract',
      'presentation': 'fas fa-file-powerpoint',
      'whitepaper': 'fas fa-file-pdf',
      'case-study': 'fas fa-file-medical',
      'manual': 'fas fa-book',
      'specification': 'fas fa-file-code'
    };
    return icons[type] || 'fas fa-file';
  };

  const formatFileSize = (size) => {
    if (typeof size === 'string') return size;
    if (size < 1024) return size + ' B';
    if (size < 1024 * 1024) return (size / 1024).toFixed(1) + ' KB';
    if (size < 1024 * 1024 * 1024) return (size / (1024 * 1024)).toFixed(1) + ' MB';
    return (size / (1024 * 1024 * 1024)).toFixed(1) + ' GB';
  };

  const handleFolderClick = (folder) => {
    setCurrentPath(folder.path);
    setSelectedFolder(folder);
  };

  const handleDocumentClick = (document) => {
    setSelectedDocument(document);
    setDocumentModal(true);
  };

  const handleBreadcrumbClick = (index) => {
    setCurrentPath(currentPath.slice(0, index + 1));
  };

  const handleBulkAction = () => {
    if (selectedItems.length === 0) return;
    
    switch (bulkAction) {
      case 'download':
        console.log('Downloading selected items:', selectedItems);
        break;
      case 'delete':
        console.log('Deleting selected items:', selectedItems);
        break;
      case 'move':
        console.log('Moving selected items:', selectedItems);
        break;
      case 'archive':
        console.log('Archiving selected items:', selectedItems);
        break;
      default:
        break;
    }
    
    setSelectedItems([]);
    setBulkAction('');
  };

  const renderDocumentsView = () => (
    <div className="documents-content">
      <div className="documents-controls">
        <div className="controls-header">
          <div className="breadcrumb">
            {currentPath.map((path, index) => (
              <span key={index} className="breadcrumb-item">
                <button onClick={() => handleBreadcrumbClick(index)}>
                  {path}
                </button>
                {index < currentPath.length - 1 && <i className="fas fa-chevron-right"></i>}
              </span>
            ))}
          </div>
          <div className="view-controls">
            <button 
              className={`view-btn ${viewMode === 'grid' ? 'active' : ''}`}
              onClick={() => setViewMode('grid')}
            >
              <i className="fas fa-th"></i>
            </button>
            <button 
              className={`view-btn ${viewMode === 'list' ? 'active' : ''}`}
              onClick={() => setViewMode('list')}
            >
              <i className="fas fa-list"></i>
            </button>
          </div>
        </div>

        <div className="search-and-actions">
          <div className="search-section">
            <div className="search-input">
              <i className="fas fa-search"></i>
              <input
                type="text"
                placeholder="Search documents and folders..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
          </div>
          <div className="action-buttons">
            <button className="action-btn upload" onClick={() => setUploadModal(true)}>
              <i className="fas fa-upload"></i>
              Upload
            </button>
            <button className="action-btn new-folder" onClick={() => setNewFolderModal(true)}>
              <i className="fas fa-folder-plus"></i>
              New Folder
            </button>
          </div>
        </div>

        <div className="filter-and-sort">
          <div className="filter-section">
            <select value={documentFilters.type} onChange={(e) => setDocumentFilters({...documentFilters, type: e.target.value})}>
              <option value="all">All Types</option>
              <option value="research-report">Research Reports</option>
              <option value="analysis">Analysis</option>
              <option value="proposal">Proposals</option>
              <option value="presentation">Presentations</option>
              <option value="whitepaper">Whitepapers</option>
            </select>
            <select value={documentFilters.status} onChange={(e) => setDocumentFilters({...documentFilters, status: e.target.value})}>
              <option value="all">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="review">Under Review</option>
              <option value="approved">Approved</option>
              <option value="published">Published</option>
              <option value="archived">Archived</option>
            </select>
            <select value={documentFilters.category} onChange={(e) => setDocumentFilters({...documentFilters, category: e.target.value})}>
              <option value="all">All Categories</option>
              <option value="market-research">Market Research</option>
              <option value="competitive-analysis">Competitive Analysis</option>
              <option value="financial">Financial</option>
              <option value="technical">Technical</option>
              <option value="strategic">Strategic</option>
            </select>
          </div>
          <div className="sort-section">
            <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
              <option value="modified">Sort by Modified</option>
              <option value="created">Sort by Created</option>
              <option value="name">Sort by Name</option>
              <option value="size">Sort by Size</option>
              <option value="type">Sort by Type</option>
            </select>
            <button 
              className="sort-order"
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            >
              <i className={`fas fa-sort-${sortOrder === 'asc' ? 'up' : 'down'}`}></i>
            </button>
          </div>
        </div>

        {selectedItems.length > 0 && (
          <div className="bulk-actions">
            <span className="selection-count">{selectedItems.length} items selected</span>
            <select value={bulkAction} onChange={(e) => setBulkAction(e.target.value)}>
              <option value="">Select Action</option>
              <option value="download">Download</option>
              <option value="move">Move</option>
              <option value="archive">Archive</option>
              <option value="delete">Delete</option>
            </select>
            <button className="apply-action" onClick={handleBulkAction} disabled={!bulkAction}>
              Apply
            </button>
            <button className="clear-selection" onClick={() => setSelectedItems([])}>
              Clear
            </button>
          </div>
        )}
      </div>

      <div className={`documents-grid ${viewMode}`}>
        {/* Folders */}
        {sortedFolders.map(folder => (
          <div key={folder.id} className="folder-item" onClick={() => handleFolderClick(folder)}>
            <div className="folder-icon">
              <i className="fas fa-folder"></i>
            </div>
            <div className="folder-info">
              <h4>{folder.name}</h4>
              <div className="folder-meta">
                <span>{folder.documentCount} documents</span>
                <span>{folder.subfolderCount} folders</span>
                <span>{folder.size}</span>
              </div>
              <div className="folder-details">
                <span className="owner">{folder.owner}</span>
                <span className="modified">{new Date(folder.modifiedAt).toLocaleDateString()}</span>
              </div>
            </div>
            <div className="folder-actions">
              <button className="action-btn"><i className="fas fa-ellipsis-v"></i></button>
            </div>
          </div>
        ))}

        {/* Documents */}
        {sortedDocuments.map(document => (
          <div key={document.id} className="document-item" onClick={() => handleDocumentClick(document)}>
            <div className="document-selection">
              <input 
                type="checkbox" 
                checked={selectedItems.includes(document.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedItems([...selectedItems, document.id]);
                  } else {
                    setSelectedItems(selectedItems.filter(id => id !== document.id));
                  }
                }}
                onClick={(e) => e.stopPropagation()}
              />
            </div>
            <div className="document-icon">
              <i className={getTypeIcon(document.type)}></i>
            </div>
            <div className="document-info">
              <h4>{document.title}</h4>
              <div className="document-meta">
                <span className="status-badge" style={{ backgroundColor: getStatusColor(document.status) }}>
                  {document.status}
                </span>
                <span className="type">{document.type}</span>
                <span className="size">{document.size}</span>
              </div>
              <div className="document-details">
                <span className="author">{document.author}</span>
                <span className="modified">{new Date(document.modifiedAt).toLocaleDateString()}</span>
                <span className="version">{document.version}</span>
              </div>
              <div className="document-stats">
                <span className="views"><i className="fas fa-eye"></i> {document.views}</span>
                <span className="downloads"><i className="fas fa-download"></i> {document.downloads}</span>
                {document.isShared && <span className="shared"><i className="fas fa-share-alt"></i></span>}
                {document.isStarred && <span className="starred"><i className="fas fa-star"></i></span>}
                {document.hasComments && <span className="comments"><i className="fas fa-comment"></i> {document.comments}</span>}
              </div>
            </div>
            <div className="document-actions">
              <button className="action-btn download" onClick={(e) => {e.stopPropagation(); console.log('Download:', document.id);}}>
                <i className="fas fa-download"></i>
              </button>
              <button className="action-btn share" onClick={(e) => {e.stopPropagation(); setShareModal(true);}}>
                <i className="fas fa-share-alt"></i>
              </button>
              <button className="action-btn more" onClick={(e) => {e.stopPropagation();}}>
                <i className="fas fa-ellipsis-v"></i>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderTemplatesView = () => (
    <div className="templates-content">
      <div className="templates-header">
        <h3>Document Templates</h3>
        <button className="new-template-btn">
          <i className="fas fa-plus"></i>
          Create Template
        </button>
      </div>
      <div className="templates-grid">
        {templates.map(template => (
          <div key={template.id} className="template-card">
            <div className="template-preview">
              <div className="preview-placeholder">
                <i className="fas fa-file-alt"></i>
              </div>
            </div>
            <div className="template-info">
              <h4>{template.name}</h4>
              <div className="template-meta">
                <span className="type">{template.type}</span>
                <span className="category">{template.category}</span>
              </div>
              <div className="template-stats">
                <div className="stat">
                  <span className="stat-value">{template.usage}</span>
                  <span className="stat-label">Uses</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{template.rating}</span>
                  <span className="stat-label">Rating</span>
                </div>
                <div className="stat">
                  <span className="stat-value">{template.size}</span>
                  <span className="stat-label">Size</span>
                </div>
              </div>
              <p className="template-description">{template.description}</p>
              <div className="template-actions">
                <button className="use-template">Use Template</button>
                <button className="preview-template">Preview</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderCollaborationsView = () => (
    <div className="collaborations-content">
      <div className="collaborations-header">
        <h3>Active Collaborations</h3>
        <button className="new-collaboration-btn">
          <i className="fas fa-plus"></i>
          Start Collaboration
        </button>
      </div>
      <div className="collaborations-grid">
        {collaborations.map(collab => (
          <div key={collab.id} className="collaboration-card">
            <div className="collaboration-header">
              <h4>{collab.projectName}</h4>
              <span className="status-badge" style={{ backgroundColor: getStatusColor(collab.status) }}>
                {collab.status}
              </span>
            </div>
            <div className="collaboration-stats">
              <div className="stat">
                <span className="stat-value">{collab.documents}</span>
                <span className="stat-label">Documents</span>
              </div>
              <div className="stat">
                <span className="stat-value">{collab.collaborators}</span>
                <span className="stat-label">Members</span>
              </div>
              <div className="stat">
                <span className="stat-value">{collab.activeUsers}</span>
                <span className="stat-label">Active</span>
              </div>
            </div>
            <div className="collaboration-progress">
              <div className="progress-header">
                <span>Progress</span>
                <span>{collab.progress}%</span>
              </div>
              <div className="progress-bar">
                <div className="progress-fill" style={{ width: `${collab.progress}%` }}></div>
              </div>
            </div>
            <div className="collaboration-details">
              <div className="detail">
                <span className="label">Owner:</span>
                <span className="value">{collab.owner}</span>
              </div>
              <div className="detail">
                <span className="label">Deadline:</span>
                <span className="value">{new Date(collab.deadline).toLocaleDateString()}</span>
              </div>
              <div className="detail">
                <span className="label">Priority:</span>
                <span className="value">{collab.priority}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderArchivesView = () => (
    <div className="archives-content">
      <div className="archives-header">
        <h3>Document Archives</h3>
        <div className="archive-controls">
          <button className="create-archive-btn">
            <i className="fas fa-archive"></i>
            Create Archive
          </button>
          <button className="restore-btn">
            <i className="fas fa-undo"></i>
            Restore
          </button>
        </div>
      </div>
      <div className="archives-grid">
        {archives.map(archive => (
          <div key={archive.id} className="archive-card">
            <div className="archive-header">
              <h4>{archive.name}</h4>
              <span className="archive-type">{archive.type}</span>
            </div>
            <div className="archive-stats">
              <div className="stat">
                <span className="stat-value">{archive.documentCount}</span>
                <span className="stat-label">Documents</span>
              </div>
              <div className="stat">
                <span className="stat-value">{archive.size}</span>
                <span className="stat-label">Size</span>
              </div>
            </div>
            <div className="archive-details">
              <div className="detail">
                <span className="label">Created:</span>
                <span className="value">{new Date(archive.createdAt).toLocaleDateString()}</span>
              </div>
              <div className="detail">
                <span className="label">Retention:</span>
                <span className="value">{archive.retentionPolicy}</span>
              </div>
              <div className="detail">
                <span className="label">Access:</span>
                <span className="value">{archive.accessLevel}</span>
              </div>
            </div>
            <div className="archive-status">
              <span className="status-badge" style={{ backgroundColor: getStatusColor(archive.status) }}>
                {archive.status}
              </span>
              <span className="backup-status">{archive.backupStatus}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderAnalyticsView = () => (
    <div className="analytics-content">
      <div className="analytics-header">
        <h3>Document Analytics</h3>
        <div className="analytics-controls">
          <select className="time-range">
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
            <option value="12m">Last 12 Months</option>
          </select>
        </div>
      </div>
      <div className="analytics-metrics">
        {analytics.map((metric, index) => (
          <div key={index} className="metric-card">
            <div className="metric-header">
              <h4>{metric.metric}</h4>
              <div className={`trend-indicator ${metric.trend}`}>
                <i className={`fas fa-arrow-${metric.trend === 'up' ? 'up' : 'down'}`}></i>
                <span>{metric.change}%</span>
              </div>
            </div>
            <div className="metric-value">
              <span className="value">{metric.value}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="analytics-charts">
        <div className="chart-placeholder">
          <h4>Document Usage Trends</h4>
          <div className="chart-content">
            <i className="fas fa-chart-line"></i>
            <p>Chart visualization would be displayed here</p>
          </div>
        </div>
        <div className="chart-placeholder">
          <h4>Storage Growth</h4>
          <div className="chart-content">
            <i className="fas fa-chart-area"></i>
            <p>Chart visualization would be displayed here</p>
          </div>
        </div>
      </div>
    </div>
  );

  const renderWorkflowsView = () => (
    <div className="workflows-content">
      <div className="workflows-header">
        <h3>Document Workflows</h3>
        <button className="new-workflow-btn">
          <i className="fas fa-plus"></i>
          Create Workflow
        </button>
      </div>
      <div className="workflows-grid">
        {workflows.map(workflow => (
          <div key={workflow.id} className="workflow-card">
            <div className="workflow-header">
              <h4>{workflow.name}</h4>
              <span className="status-badge" style={{ backgroundColor: getStatusColor(workflow.status) }}>
                {workflow.status}
              </span>
            </div>
            <div className="workflow-stats">
              <div className="stat">
                <span className="stat-value">{workflow.documentsInFlow}</span>
                <span className="stat-label">In Process</span>
              </div>
              <div className="stat">
                <span className="stat-value">{workflow.averageTime}</span>
                <span className="stat-label">Avg Time</span>
              </div>
              <div className="stat">
                <span className="stat-value">{workflow.completionRate}%</span>
                <span className="stat-label">Success Rate</span>
              </div>
            </div>
            <div className="workflow-details">
              <div className="detail">
                <span className="label">Type:</span>
                <span className="value">{workflow.type}</span>
              </div>
              <div className="detail">
                <span className="label">Steps:</span>
                <span className="value">{workflow.steps}</span>
              </div>
              <div className="detail">
                <span className="label">Automation:</span>
                <span className="value">{workflow.automationLevel}%</span>
              </div>
            </div>
            <div className="workflow-actions">
              <button className="edit-workflow">Edit</button>
              <button className="view-workflow">View Details</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeView) {
      case 'documents':
        return renderDocumentsView();
      case 'templates':
        return renderTemplatesView();
      case 'collaborations':
        return renderCollaborationsView();
      case 'archives':
        return renderArchivesView();
      case 'analytics':
        return renderAnalyticsView();
      case 'workflows':
        return renderWorkflowsView();
      default:
        return renderDocumentsView();
    }
  };

  if (loading) {
    return (
      <div className="research-document-manager loading">
        <div className="loading-spinner">
          <i className="fas fa-spinner fa-spin"></i>
          <p>Loading research documents...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="research-document-manager error">
        <div className="error-message">
          <i className="fas fa-exclamation-triangle"></i>
          <p>{error}</p>
          <button onClick={() => window.location.reload()}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="research-document-manager">
      <div className="manager-header">
        <div className="header-left">
          <h1>Research Document Manager</h1>
          <p>Comprehensive document management and collaboration platform</p>
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
          <button className="settings-btn">
            <i className="fas fa-cog"></i>
            Settings
          </button>
        </div>
      </div>

      <div className="manager-navigation">
        <div className="nav-tabs">
          <button 
            className={`nav-tab ${activeView === 'documents' ? 'active' : ''}`}
            onClick={() => setActiveView('documents')}
          >
            <i className="fas fa-folder-open"></i>
            Documents
            <span className="count">{documents.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'templates' ? 'active' : ''}`}
            onClick={() => setActiveView('templates')}
          >
            <i className="fas fa-file-alt"></i>
            Templates
            <span className="count">{templates.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'collaborations' ? 'active' : ''}`}
            onClick={() => setActiveView('collaborations')}
          >
            <i className="fas fa-users"></i>
            Collaborations
            <span className="count">{collaborations.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'archives' ? 'active' : ''}`}
            onClick={() => setActiveView('archives')}
          >
            <i className="fas fa-archive"></i>
            Archives
            <span className="count">{archives.length}</span>
          </button>
          <button 
            className={`nav-tab ${activeView === 'analytics' ? 'active' : ''}`}
            onClick={() => setActiveView('analytics')}
          >
            <i className="fas fa-chart-bar"></i>
            Analytics
          </button>
          <button 
            className={`nav-tab ${activeView === 'workflows' ? 'active' : ''}`}
            onClick={() => setActiveView('workflows')}
          >
            <i className="fas fa-project-diagram"></i>
            Workflows
            <span className="count">{workflows.length}</span>
          </button>
        </div>
      </div>

      <div className="manager-main">
        {renderContent()}
      </div>

      {/* Modals would be rendered here */}
      {documentModal && selectedDocument && (
        <div className="modal-overlay" onClick={() => setDocumentModal(false)}>
          <div className="document-modal" onClick={(e) => e.stopPropagation()}>
            {/* Detailed document modal content */}
          </div>
        </div>
      )}
    </div>
  );
};

export default ResearchDocumentManager;
