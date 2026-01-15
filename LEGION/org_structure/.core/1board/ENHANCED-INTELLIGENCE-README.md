# Enhanced Board Intelligence System

## Overview

The Enhanced Board Intelligence System provides a meticulously designed integration between workspace data (`W:\artifactvirtual\data`) and LLM-powered insights through Ollama. This system converts raw workspace data into structured, LLM-readable JSON context and generates actionable insights in a templated, updatable, and abstracted manner.

## Architecture

### Core Components

1. **Advanced Context Manager** (`advanced-context-manager.ts`)
   - Converts workspace data into structured LLM context
   - Provides comprehensive error handling and validation
   - Implements caching and backup strategies
   - Supports versioned context schemas for backwards compatibility

2. **LLM Context Converter** (`llm-context-converter.ts`)
   - Extracts and transforms data from multiple sources:
     - Research papers from `real_research/` JSON files
     - Enterprise data from `enterprise/` folder
     - DAO governance data from `dao/` folder
     - SQLite databases (*.db files)
   - Provides structured, type-safe context objects

3. **Ollama Integration** (`ollama-service.ts` + `ollama-startup.ts`)
   - Robust Ollama service startup and health monitoring
   - Templated insight generation with multiple analysis types
   - Automatic model downloading and validation
   - Graceful error handling and recovery

4. **Data Integration Service** (`data-integration.ts`)
   - Real-time monitoring of workspace data changes
   - Reactive data streams for live updates
   - Database and file system integration

## Data Flow

```
W:\artifactvirtual\data
├── real_research/*.json     → Research Papers Context
├── enterprise/              → Enterprise Context  
├── dao/                     → DAO Governance Context
├── *.db files              → Database Context
└── backups/                → Backup Data

         ↓ (Advanced Context Manager)

LLM-Readable JSON Context
├── metadata (timestamps, versions, confidence)
├── workspace (structure, metrics, activity)
├── research (papers, models, analyses)
├── enterprise (org structure, KPIs, operations)
├── dao (governance, proposals, voting)
├── databases (schemas, records, insights)
├── insights (categorized, prioritized)
└── actionableItems (tasks, priorities, deadlines)

         ↓ (Ollama Service)

Templated Actionable Insights
├── Executive Summary
├── Technical Analysis  
├── Action Plans
├── Risk Assessments
└── Strategic Recommendations
```

## Getting Started

### Prerequisites

1. **Ollama Installation**
   ```bash
   # Install Ollama (if not already installed)
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or on Windows, download from https://ollama.ai/download
   ```

2. **Dependencies Installation**
   ```bash
   cd w:\artifactvirtual\enterprise\org_structure\.core\1board
   npm install
   ```

### Quick Start

1. **Start the Enhanced Intelligence System**
   ```bash
   npm run intelligence:enhanced
   ```

2. **Access the Dashboard**
   - Navigate to `http://localhost:3001`
   - API Health: `http://localhost:3001/api/health`

### Manual Configuration

You can customize the system by modifying the startup configuration:

```typescript
const startup = new EnhancedBoardSystemStartup({
    enableDashboard: true,
    dashboardPort: 3001,
    enableOllama: true,
    ollamaModel: 'llama3.2', // or 'llama3.1', 'mistral', etc.
    contextRefreshInterval: 15, // minutes
    enableAdvancedLogging: true,
    workspaceDataPath: 'W:/artifactvirtual/data'
});
```

## API Endpoints

### Intelligence Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/intelligence/status` | GET | Get system and Ollama health status |
| `/api/intelligence/analyze` | POST | Generate insights for specific focus area |
| `/api/intelligence/recommendations` | POST | Get LLM recommendations for area |
| `/api/intelligence/context-summary` | GET | Get workspace context summary |
| `/api/intelligence/refresh` | POST | Force refresh of LLM context |
| `/api/intelligence/insights` | GET | Get current insights |
| `/api/intelligence/templates` | GET | Get available analysis templates |
| `/api/intelligence/focus-areas` | GET | Get available focus areas |

### Workspace Data Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/workspace/data-status` | GET | Get workspace data integration status |
| `/api/workspace/research-context` | GET | Get research data context |
| `/api/workspace/performance-history` | GET | Get board performance history |
| `/api/workspace/save-decision` | POST | Save board decision to workspace |

### Example API Usage

#### Generate Strategic Analysis
```bash
curl -X POST http://localhost:3001/api/intelligence/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "focusArea": "strategic",
    "priority": "high",
    "templateType": "executive-summary",
    "forceRefresh": false
  }'
```

#### Get Context Summary
```bash
curl http://localhost:3001/api/intelligence/context-summary
```

#### Get System Health
```bash
curl http://localhost:3001/api/intelligence/status
```

## Context Structure

The LLM context follows a structured format designed for maximum abstraction and maintainability:

```typescript
interface LLMContext {
    metadata: {
        generatedAt: Date;
        version: string;
        dataSource: string;
        totalDataPoints: number;
        confidenceScore: number;
    };
    workspace: {
        structure: DirectoryStructure;
        fileTypes: FileTypeAnalysis;
        keyMetrics: WorkspaceMetrics;
    };
    research: {
        papers: ResearchPaper[];
        models: CognitiveModel[];
        analyses: AnalysisResult[];
    };
    enterprise: {
        organizationalStructure: OrgStructure;
        strategies: StrategyDocument[];
        kpis: KPIMetrics[];
    };
    dao: {
        governance: DAOGovernance;
        proposals: ProposalData[];
        voting: VotingData;
    };
    databases: DatabaseContext[];
    insights: InsightContext[];
    actionableItems: ActionableItem[];
}
```

## Template Types

The system supports multiple analysis templates:

1. **Executive Summary** - High-level strategic overview
2. **Technical Analysis** - Detailed technical assessment
3. **Action Plan** - Concrete action items with timelines
4. **Risk Assessment** - Risk analysis and mitigation strategies

## Configuration Options

### Advanced Context Manager Configuration

```typescript
interface ContextManagementConfig {
    workspaceRoot: string;           // Path to workspace data
    cacheEnabled: boolean;           // Enable context caching
    cacheDirectory: string;          // Cache storage location
    maxCacheAge: number;            // Cache validity period (ms)
    autoRefreshInterval: number;     // Auto-refresh interval (minutes)
    compressionEnabled: boolean;     // Enable context compression
    validationEnabled: boolean;      // Enable context validation
    backupEnabled: boolean;         // Enable context backups
}
```

### Ollama Startup Configuration

```typescript
interface OllamaStartupConfig {
    baseUrl: string;                // Ollama server URL
    port: number;                   // Ollama port
    model: string;                  // LLM model to use
    autoStart: boolean;             // Auto-start Ollama service
    healthCheckInterval: number;    // Health check frequency (ms)
    maxRetries: number;             // Max retry attempts
    timeout: number;                // Request timeout (ms)
    logLevel: 'debug' | 'info' | 'warn' | 'error';
}
```

## Monitoring and Health Checks

The system provides comprehensive monitoring:

1. **System Health Monitoring**
   - Ollama service status and response times
   - Context manager health and metrics
   - Data source availability and quality
   - Error rates and recovery status

2. **Performance Metrics**
   - Context generation time
   - Data processing speed
   - Cache hit rates
   - Insight generation performance

3. **Data Quality Metrics**
   - Context validation scores
   - Data completeness indicators
   - Source reliability metrics
   - Confidence scores for insights

## Troubleshooting

### Common Issues

1. **Ollama Service Not Starting**
   ```bash
   # Check if Ollama is installed
   ollama --version
   
   # Start Ollama manually
   ollama serve
   
   # Check if port 11434 is available
   netstat -an | findstr 11434
   ```

2. **Context Generation Errors**
   - Verify workspace data path exists: `W:\artifactvirtual\data`
   - Check read permissions on data files
   - Review logs for validation errors

3. **Dashboard Not Accessible**
   - Verify port 3001 is not in use
   - Check firewall settings
   - Review dashboard startup logs

### Debug Logging

Enable advanced logging for troubleshooting:

```typescript
const startup = new EnhancedBoardSystemStartup({
    enableAdvancedLogging: true
});
```

## Development

### Building the System

```bash
# Development mode
npm run intelligence:enhanced

# Production build
npm run build
npm run intelligence:enhanced:prod
```

### Testing

```bash
# Run tests
npm test

# Watch mode
npm run test:watch
```

### Code Quality

```bash
# Linting
npm run lint

# Formatting
npm run format
```

## Security Considerations

1. **Data Privacy**
   - Workspace data is processed locally
   - No external API calls for sensitive data
   - LLM processing happens on local Ollama instance

2. **Access Control**
   - API endpoints can be secured with authentication
   - File system permissions control data access
   - Backup encryption available

3. **Data Validation**
   - Input validation for all data sources
   - Context schema validation
   - Error handling for malformed data

## Performance Optimization

1. **Caching Strategy**
   - Context caching reduces regeneration overhead
   - Configurable cache expiration
   - Intelligent cache invalidation

2. **Data Processing**
   - Incremental data processing
   - Parallel database queries
   - Optimized JSON parsing

3. **Resource Management**
   - Memory-efficient context generation
   - Automatic cleanup of temporary files
   - Configurable processing limits

## Contributing

1. Follow TypeScript best practices
2. Add comprehensive error handling
3. Include unit tests for new features
4. Update documentation for API changes
5. Maintain backwards compatibility for context schema

## License

This system is part of the Artifact Virtual Board Governance framework and follows the project's licensing terms.
