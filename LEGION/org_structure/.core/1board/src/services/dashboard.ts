/**
 * Board System Dashboard
 * Web-based visualization of the autonomous board governance system
 */

import cors from 'cors';
import express, { Request, Response } from 'express';
import fs from 'fs';
import http from 'http';
import path from 'path';
import WebSocket from 'ws';

import { boardSystem } from './board-orchestrator';

// Define types for error handling
interface ErrorWithMessage {
  message: string;
}

function isErrorWithMessage(error: unknown): error is ErrorWithMessage {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    typeof (error as Record<string, unknown>).message === 'string'
  );
}

function getErrorMessage(error: unknown): string {
  if (isErrorWithMessage(error)) {
    return error.message;
  }
  return String(error);
}

// Dashboard events for WebSocket
interface DashboardEvent {
  type: string;
  data: any;
  timestamp: Date;
}

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Keep track of connected clients
const clients = new Set<WebSocket>();

// Enable CORS for all routes
app.use(cors());

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));
app.use(express.json());

/**
 * REST API endpoints
 */

// Get system status
app.get('/api/status', (_req: Request, res: Response) => {
    try {
        // Use intervene to get system status
        boardSystem.intervene('get_system_status', {})
            .then(status => {
                res.json({
                    ...status,
                    uptime: process.uptime(),
                    timestamp: new Date()
                });
            })
            .catch(error => {
                res.status(500).json({ 
                    error: getErrorMessage(error),
                    status: 'ERROR'
                });
            });
    } catch (error) {
        res.status(500).json({ 
            error: getErrorMessage(error),
            status: 'ERROR'
        });
    }
});

// Get current metrics
app.get('/api/metrics', async (req, res) => {
    try {
        const metrics = await boardSystem.intervene('get_metrics', {});
        res.json(metrics);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get current system state
app.get('/api/state', async (req, res) => {
    try {
        const state = await boardSystem.intervene('get_state', {});
        res.json(state);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get director status
app.get('/api/directors/:role', async (req, res) => {
    try {
        const { role } = req.params;
        const status = await boardSystem.intervene('director_status', { role });
        res.json(status);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Inject an event
app.post('/api/events', async (req, res) => {
    try {
        const { event } = req.body;
        if (!event) {
            return res.status(400).json({ error: 'No event provided' });
        }
        
        const result = await boardSystem.intervene('inject_event', { event });
        res.json(result);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Start the system
app.post('/api/start', async (req, res) => {
    try {
        await boardSystem.start();
        res.json({ success: true, message: 'Board system started' });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Stop the system
app.post('/api/stop', async (req, res) => {
    try {
        await boardSystem.stop();
        res.json({ success: true, message: 'Board system stopped' });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get workspace data status
app.get('/api/workspace/data-status', async (req, res) => {
    try {
        const status = await boardSystem.intervene('workspace_data_status', {});
        res.json(status);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get research context from workspace data
app.get('/api/workspace/research-context', async (req, res) => {
    try {
        const context = await boardSystem.intervene('get_research_context', {});
        res.json(context);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get board performance history from workspace data
app.get('/api/workspace/performance-history', async (req, res) => {
    try {
        const history = await boardSystem.getPerformanceHistory();
        res.json({ success: true, history });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Save board decision to workspace data
app.post('/api/workspace/save-decision', async (req, res) => {
    try {
        const { decision } = req.body;
        if (!decision) {
            return res.status(400).json({ error: 'No decision provided' });
        }
        
        await boardSystem.saveDecision(decision);
        res.json({ success: true, message: 'Decision saved to workspace data' });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Board Intelligence endpoints

// Get Board Intelligence status
app.get('/api/intelligence/status', async (req, res) => {
    try {
        const status = boardSystem.getBoardIntelligenceStatus();
        res.json(status);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Generate Board Analysis with LLM
app.post('/api/intelligence/analyze', async (req, res) => {
    try {
        const { focusArea, priority, templateType, forceRefresh } = req.body;
        const insights = await boardSystem.generateBoardAnalysis({
            focusArea,
            priority,
            templateType,
            forceRefresh
        });
        res.json({ insights, count: insights.length });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get LLM recommendations for specific area
app.post('/api/intelligence/recommendations', async (req, res) => {
    try {
        const { area, templateType = 'executive-summary' } = req.body;
        if (!area) {
            return res.status(400).json({ error: 'Area parameter required' });
        }
        
        const recommendations = await boardSystem.getLLMRecommendations(area, templateType);
        res.json({ recommendations, count: recommendations.length });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get workspace context summary with LLM analysis
app.get('/api/intelligence/context-summary', async (req, res) => {
    try {
        const summary = await boardSystem.getWorkspaceContextSummary();
        res.json(summary);
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Refresh Board Intelligence
app.post('/api/intelligence/refresh', async (req, res) => {
    try {
        await boardSystem.refreshBoardIntelligence();
        res.json({ success: true, message: 'Board Intelligence refreshed' });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Get current Board Intelligence insights
app.get('/api/intelligence/insights', async (req, res) => {
    try {
        const insights = boardSystem.getCurrentBoardInsights();
        res.json({ insights, count: insights.length });
    } catch (error) {
        res.status(500).json({ error: getErrorMessage(error) });
    }
});

// Template management endpoints

// Get available analysis templates
app.get('/api/intelligence/templates', (req, res) => {
    const templates = [
        {
            id: 'executive-summary',
            name: 'Executive Summary',
            description: 'High-level strategic overview for board members',
            focusAreas: ['strategic', 'operational', 'financial']
        },
        {
            id: 'technical-analysis',
            name: 'Technical Analysis',
            description: 'Detailed technical assessment and recommendations',
            focusAreas: ['operational', 'research']
        },
        {
            id: 'action-plan',
            name: 'Action Plan',
            description: 'Concrete action items with timelines and priorities',
            focusAreas: ['strategic', 'operational', 'research', 'financial', 'governance']
        },
        {
            id: 'risk-assessment',
            name: 'Risk Assessment',
            description: 'Comprehensive risk analysis and mitigation strategies',
            focusAreas: ['governance', 'financial', 'operational']
        },
        {
            id: 'strategic-planning',
            name: 'Strategic Planning',
            description: 'Long-term strategic insights and planning recommendations',
            focusAreas: ['strategic', 'research', 'financial']
        }
    ];
    
    res.json({ templates });
});

// Get available focus areas
app.get('/api/intelligence/focus-areas', (req, res) => {
    const focusAreas = [
        { id: 'strategic', name: 'Strategic', description: 'Strategic planning and positioning' },
        { id: 'operational', name: 'Operational', description: 'Day-to-day operations and efficiency' },
        { id: 'research', name: 'Research', description: 'Research and development activities' },
        { id: 'financial', name: 'Financial', description: 'Financial health and resource management' },
        { id: 'governance', name: 'Governance', description: 'Governance and compliance matters' }
    ];
    
    res.json({ focusAreas });
});

/**
 * WebSocket for real-time updates
 */
wss.on('connection', (ws) => {
    console.log('Client connected to dashboard');
    clients.add(ws);
    
    ws.on('close', () => {
        console.log('Client disconnected from dashboard');
        clients.delete(ws);
    });
    
    // Send initial data
    const initialData = {
        type: 'initial',
        status: {
            running: boardSystem.isRunning,
            uptime: process.uptime(),
            timestamp: new Date()
        }
    };
    ws.send(JSON.stringify(initialData));
});

/**
 * Broadcast metrics to all connected clients
 */
const broadcastMetrics = async () => {
    if (clients.size === 0) return;
    
    try {
        const metrics = await boardSystem.intervene('get_metrics', {});
        const message = JSON.stringify({
            type: 'metrics',
            data: metrics,
            timestamp: new Date()
        });
        
        for (const client of clients) {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        }
    } catch (error) {
        console.error('Error broadcasting metrics:', error);
    }
};

/**
 * Start the dashboard
 */
export const startDashboard = (port = 3000) => {
    server.listen(port, () => {
        console.log(`Board System Dashboard running at http://localhost:${port}`);
        
        // Start metrics broadcasting
        setInterval(broadcastMetrics, 5000);
        
        // Create dashboard HTML file if it doesn't exist
        createDashboardHTML();
    });
    
    return server;
};

/**
 * Create dashboard HTML file
 */
const createDashboardHTML = () => {
    const publicDir = path.join(__dirname, 'public');
    if (!fs.existsSync(publicDir)) {
        fs.mkdirSync(publicDir, { recursive: true });
    }
    
    const htmlPath = path.join(publicDir, 'index.html');
    if (!fs.existsSync(htmlPath)) {
        const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Artifact Virtual - Board Governance System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { padding: 20px; background-color: #f8f9fa; }
        .card { margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .metrics-panel { height: 300px; overflow-y: auto; }
        .system-status { font-size: 1.2em; }
        .card-header { background-color: #343a40; color: white; }
        .director-card { height: 250px; }
        .ws-status { position: absolute; top: 10px; right: 10px; }
        .ws-connected { color: green; }
        .ws-disconnected { color: red; }
        #eventLog { height: 200px; overflow-y: auto; font-family: monospace; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row mb-4">
            <div class="col">
                <h1>Artifact Virtual - Autonomous Board Governance System</h1>
                <p class="lead">Real-time monitoring and visualization dashboard</p>
                <div class="ws-status">
                    <span id="wsStatus" class="ws-disconnected">●</span>
                    <span id="wsStatusText">Disconnected</span>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">System Status</div>
                    <div class="card-body">
                        <div class="system-status">
                            Status: <span id="systemStatus">Unknown</span>
                        </div>
                        <div>Uptime: <span id="uptime">0s</span></div>
                        <div>Last Update: <span id="lastUpdate">Never</span></div>
                        <div class="mt-3">
                            <button id="startBtn" class="btn btn-success">Start System</button>
                            <button id="stopBtn" class="btn btn-danger">Stop System</button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">Event Queue</div>
                    <div class="card-body">
                        <div>Queued Events: <span id="queuedEvents">0</span></div>
                        <div>Processed Events: <span id="processedEvents">0</span></div>
                        <div class="mt-3">
                            <button id="injectEventBtn" class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#eventModal">
                                Inject Event
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">System Health</div>
                    <div class="card-body">
                        <canvas id="healthChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row mb-4">
            <div class="col-12">
                <div class="card">
                    <div class="card-header">Director Activity</div>
                    <div class="card-body">
                        <div class="row" id="directorsPanel">
                            <!-- Director cards will be dynamically added here -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="row">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-header">System Metrics</div>
                    <div class="card-body metrics-panel">
                        <pre id="metricsJson">No metrics available</pre>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-header">Event Log</div>
                    <div class="card-body">
                        <div id="eventLog"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Event Injection Modal -->
    <div class="modal fade" id="eventModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Inject Event</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                    <div class="mb-3">
                        <label for="eventType" class="form-label">Event Type</label>
                        <select class="form-select" id="eventType">
                            <option value="MARKET_SHIFT">Market Shift</option>
                            <option value="REGULATORY_CHANGE">Regulatory Change</option>
                            <option value="SECURITY_INCIDENT">Security Incident</option>
                            <option value="TECHNICAL_FAILURE">Technical Failure</option>
                            <option value="RESEARCH_BREAKTHROUGH">Research Breakthrough</option>
                            <option value="STRATEGIC_OPPORTUNITY">Strategic Opportunity</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="eventDescription" class="form-label">Description</label>
                        <input type="text" class="form-control" id="eventDescription">
                    </div>
                    <div class="mb-3">
                        <label for="eventSeverity" class="form-label">Severity</label>
                        <select class="form-select" id="eventSeverity">
                            <option value="INFORMATIONAL">Informational</option>
                            <option value="LOW">Low</option>
                            <option value="MEDIUM">Medium</option>
                            <option value="HIGH">High</option>
                            <option value="CRITICAL">Critical</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="eventData" class="form-label">Additional Data (JSON)</label>
                        <textarea class="form-control" id="eventData" rows="5"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="submitEventBtn">Inject Event</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // WebSocket connection
        let socket;
        let healthChart;
        let reconnectTimeout;

        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            socket = new WebSocket(\`\${protocol}//\${window.location.host}\`);
            
            socket.onopen = () => {
                document.getElementById('wsStatus').className = 'ws-connected';
                document.getElementById('wsStatusText').textContent = 'Connected';
                console.log('WebSocket connected');
                clearTimeout(reconnectTimeout);
            };
            
            socket.onclose = () => {
                document.getElementById('wsStatus').className = 'ws-disconnected';
                document.getElementById('wsStatusText').textContent = 'Disconnected';
                console.log('WebSocket disconnected, reconnecting...');
                reconnectTimeout = setTimeout(connectWebSocket, 3000);
            };
            
            socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };
            
            socket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        }
        
        // Handle WebSocket messages
        function handleWebSocketMessage(message) {
            if (message.type === 'initial') {
                updateSystemStatus(message.status);
            } else if (message.type === 'metrics') {
                updateMetrics(message.data);
                addEventLog(\`Received metrics update (\${new Date().toLocaleTimeString()})\`);
            }
        }
        
        // Update system status display
        function updateSystemStatus(status) {
            document.getElementById('systemStatus').textContent = status.running ? 'RUNNING' : 'STOPPED';
            document.getElementById('systemStatus').className = status.running ? 'text-success' : 'text-danger';
            document.getElementById('uptime').textContent = \`\${Math.floor(status.uptime)}s\`;
            document.getElementById('lastUpdate').textContent = new Date(status.timestamp).toLocaleString();
            
            document.getElementById('startBtn').disabled = status.running;
            document.getElementById('stopBtn').disabled = !status.running;
        }
        
        // Update metrics display
        function updateMetrics(metrics) {
            if (!metrics) return;
            
            // Update JSON display
            document.getElementById('metricsJson').textContent = JSON.stringify(metrics, null, 2);
            
            // Update event queue
            if (metrics.events) {
                document.getElementById('queuedEvents').textContent = metrics.events.queued;
                document.getElementById('processedEvents').textContent = metrics.events.processed;
            }
            
            // Update directors panel
            updateDirectors(metrics.directors);
            
            // Update health chart
            updateHealthChart(metrics);
        }
        
        // Update directors panel
        function updateDirectors(directors) {
            if (!directors) return;
            
            const directorsPanel = document.getElementById('directorsPanel');
            directorsPanel.innerHTML = '';
            
            for (const [role, metrics] of Object.entries(directors)) {
                const directorCard = document.createElement('div');
                directorCard.className = 'col-md-4 mb-3';
                directorCard.innerHTML = \`
                    <div class="card director-card">
                        <div class="card-header">\${formatRoleName(role)}</div>
                        <div class="card-body">
                            <div>Performance: \${getPerformanceText(metrics)}</div>
                            <div>Status: \${getStatusBadge(metrics)}</div>
                            <div class="mt-2">
                                <button class="btn btn-sm btn-info view-director-btn" data-role="\${role}">View Details</button>
                            </div>
                        </div>
                    </div>
                \`;
                directorsPanel.appendChild(directorCard);
            }
            
            // Add click handlers for view buttons
            document.querySelectorAll('.view-director-btn').forEach(btn => {
                btn.addEventListener('click', () => {
                    viewDirectorDetails(btn.dataset.role);
                });
            });
        }
        
        // Format role name for display
        function formatRoleName(role) {
            return role.replace(/_/g, ' ').split(' ').map(
                word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()
            ).join(' ');
        }
        
        // Get performance text
        function getPerformanceText(metrics) {
            if (!metrics || !metrics.performance) return 'N/A';
            return \`\${(metrics.performance.reduce((a, b) => a + b, 0) / metrics.performance.length * 100).toFixed(1)}%\`;
        }
        
        // Get status badge
        function getStatusBadge(metrics) {
            if (!metrics) return '<span class="badge bg-secondary">Unknown</span>';
            
            if (metrics.reliability > 0.95) {
                return '<span class="badge bg-success">Excellent</span>';
            } else if (metrics.reliability > 0.8) {
                return '<span class="badge bg-primary">Good</span>';
            } else if (metrics.reliability > 0.6) {
                return '<span class="badge bg-warning text-dark">Fair</span>';
            } else {
                return '<span class="badge bg-danger">Poor</span>';
            }
        }
        
        // View director details
        function viewDirectorDetails(role) {
            fetch(\`/api/directors/\${role}\`)
                .then(response => response.json())
                .then(data => {
                    console.log('Director details:', data);
                    // In a real app, would show a modal with details
                    alert(\`Director \${formatRoleName(role)} details loaded to console\`);
                })
                .catch(error => console.error('Error fetching director details:', error));
        }
        
        // Initialize health chart
        function initHealthChart() {
            const ctx = document.getElementById('healthChart').getContext('2d');
            healthChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: ['Operational', 'Strategic', 'Financial', 'Security'],
                    datasets: [{
                        data: [85, 78, 92, 88],
                        backgroundColor: ['#2ecc71', '#3498db', '#f1c40f', '#e74c3c']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }
        
        // Update health chart
        function updateHealthChart(metrics) {
            if (!healthChart || !metrics) return;
            
            // In a real app, would extract actual metrics
            // This is a simplified example
            healthChart.data.datasets[0].data = [
                Math.random() * 30 + 70,
                Math.random() * 30 + 65,
                Math.random() * 20 + 75,
                Math.random() * 25 + 70
            ];
            healthChart.update();
        }
        
        // Add event to log
        function addEventLog(message) {
            const log = document.getElementById('eventLog');
            const entry = document.createElement('div');
            entry.textContent = \`[\${new Date().toLocaleTimeString()}] \${message}\`;
            log.appendChild(entry);
            
            // Auto-scroll to bottom
            log.scrollTop = log.scrollHeight;
            
            // Limit entries
            while (log.children.length > 50) {
                log.removeChild(log.firstChild);
            }
        }
        
        // Start the system
        document.getElementById('startBtn').addEventListener('click', () => {
            fetch('/api/start', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addEventLog('System started');
                    document.getElementById('systemStatus').textContent = 'RUNNING';
                    document.getElementById('systemStatus').className = 'text-success';
                    document.getElementById('startBtn').disabled = true;
                    document.getElementById('stopBtn').disabled = false;
                } else {
                    addEventLog(\`Failed to start system: \${data.error || 'Unknown error'}\`);
                }
            })
            .catch(error => {
                console.error('Error starting system:', error);
                addEventLog(\`Error starting system: \${error.message}\`);
            });
        });
        
        // Stop the system
        document.getElementById('stopBtn').addEventListener('click', () => {
            fetch('/api/stop', { 
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addEventLog('System stopped');
                    document.getElementById('systemStatus').textContent = 'STOPPED';
                    document.getElementById('systemStatus').className = 'text-danger';
                    document.getElementById('startBtn').disabled = false;
                    document.getElementById('stopBtn').disabled = true;
                } else {
                    addEventLog(\`Failed to stop system: \${data.error || 'Unknown error'}\`);
                }
            })
            .catch(error => {
                console.error('Error stopping system:', error);
                addEventLog(\`Error stopping system: \${error.message}\`);
            });
        });
        
        // Inject event
        document.getElementById('submitEventBtn').addEventListener('click', () => {
            const eventType = document.getElementById('eventType').value;
            const description = document.getElementById('eventDescription').value;
            const severity = document.getElementById('eventSeverity').value;
            let eventData = {};
            
            try {
                const jsonInput = document.getElementById('eventData').value.trim();
                if (jsonInput) {
                    eventData = JSON.parse(jsonInput);
                }
            } catch (error) {
                alert('Invalid JSON in event data field');
                return;
            }
            
            const event = {
                eventId: \`manual-\${Date.now()}\`,
                type: eventType,
                severity,
                source: 'MANUAL',
                description: description || \`Manual \${eventType} event\`,
                impact: {
                    strategic: Math.random() * 0.5 + 0.3,
                    operational: Math.random() * 0.5 + 0.3,
                    financial: Math.random() * 0.5 + 0.3,
                    reputational: Math.random() * 0.5 + 0.3
                },
                timestamp: new Date(),
                metadata: eventData
            };
            
            fetch('/api/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ event })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    addEventLog(\`Injected \${eventType} event\`);
                    document.getElementById('queuedEvents').textContent = data.queueLength;
                    
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('eventModal'));
                    modal.hide();
                } else {
                    addEventLog(\`Failed to inject event: \${data.message || 'Unknown error'}\`);
                }
            })
            .catch(error => {
                console.error('Error injecting event:', error);
                addEventLog(\`Error injecting event: \${error.message}\`);
            });
        });
        
        // Initialization
        document.addEventListener('DOMContentLoaded', () => {
            // Connect WebSocket
            connectWebSocket();
            
            // Initialize health chart
            initHealthChart();
            
            // Get initial system status
            fetch('/api/status')
                .then(response => response.json())
                .then(status => {
                    updateSystemStatus(status);
                    addEventLog('Dashboard initialized');
                })
                .catch(error => {
                    console.error('Error fetching system status:', error);
                    addEventLog(\`Error fetching system status: \${error.message}\`);
                });
            
            // Get initial metrics
            fetch('/api/metrics')
                .then(response => response.json())
                .then(metrics => {
                    updateMetrics(metrics);
                })
                .catch(error => {
                    console.error('Error fetching metrics:', error);
                });
        });
    </script>
</body>
</html>
        `;
        
        fs.writeFileSync(htmlPath, html);
        console.log(`Dashboard HTML created at ${htmlPath}`);
    }
};
