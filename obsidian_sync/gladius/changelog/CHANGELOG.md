# Gladius Changelog

All notable changes to the Gladius Enterprise System are documented here.

## [Unreleased]

### In Progress
- GGUF model fine-tuning for complete Ollama replacement
- Social media API integrations (keys configured, awaiting activation)
- Discord consensus voting implementation

## [2026-01-14] - Enhanced Chart Annotations & Autonomous Mode

### Added
- **Enhanced Chart Annotations**: RSI, ADX, ATR indicators with subplots
- **Support/Resistance Levels**: Automatic detection and visualization
- **Trade Setup Visualization**: Entry/exit zones on charts
- **Chart Learning Tools**: `analyze_chart`, `draw_indicator`, `detect_pattern`, `annotate_chart`, `generate_report`
- **Autonomous Daemon Mode**: `--auto` flag for indefinite self-running operation
- **30-Day Continuous Operation**: System designed for month-long autonomous runs

### Changed
- Charts now include multi-panel layout (price, volume, RSI, ADX)
- All technical indicators integrated into visualization
- Main daemon loop fully wired with cognition engine

### Fixed
- Chart annotation positioning for better readability
- Indicator subplot scaling issues

## [2026-01-13] - Cognition Autonomy Complete

### Added
- **Full Autonomy Cycle**: End-to-end self-improvement with Obsidian sync
- **Consensus System**: Discord voting + email escalation for proposals
- **Context Manager**: Token-aware summarization for coherent narratives
- **Native Tool Router**: Pattern-based routing with <10ms latency
- **Training Generator**: Synthetic + historical data generation
- **Flight Checklist**: Comprehensive system status with mermaid diagram

### Changed
- Self-improvement now routes proposals by impact level
- Memory module integrates with Hektor VDB natively
- Tool calling uses native definitions with 16 tools

### Fixed
- Hektor VDB document persistence issue
- Memory module compatibility with vector store
- add_vector method signature mismatch

## [2026-01-12] - Cognition Engine Integration

### Added
- **Hektor VDB**: Native C++ vector database with SIMD optimization
- **Memory Module**: Multi-database access with unified interface
- **Learning Loop**: Continuous learning with prediction tracking
- **Self-Improvement Engine**: Proposal lifecycle with snapshots

### Changed
- Migrated from external vector stores to native Hektor
- Added ONNX Runtime support for embeddings

## [2026-01-11] - Syndicate Pipeline Enhancements

### Added
- Dashboard backend with Flask + JWT auth
- RANSAC trendline analysis for charts
- Annotated chart generation with matplotlib
- Grafana overview dashboard

### Changed
- LLM worker now uses provider hints for fallback
- Added PREFER_OLLAMA option for local inference

## [2026-01-09] - Discord & LinkedIn Automation

### Added
- **Arty Discord Bot**: 15 commands with context-aware responses
- **LinkedIn Automation Module**: Professional posting framework
- Comprehensive webhook tests
- Environment variable management improvements

### Fixed
- LinkedIn OAuth integration issues
- Discord bot modular restructuring

## [2026-01-08] - MQL5 Research Phase 3

### Added
- Phase 3 manifest with advanced trading strategies
- Candle Range Theory (CRT) implementation
- Opening Range Breakout (ORB) system
- Adaptive Linear Regression Channel strategy

## [2026-01-07] - System Diagrams & Metadata

### Added
- Comprehensive system diagrams in mermaid format
- Machine-readable metadata for all modules
- Research organization with navigation maps

### Changed
- Improved documentation structure with README files

## [2026-01-01] - Automata Framework

### Added
- **Automata**: Enterprise automation framework
- Social media platform adapters (Twitter, LinkedIn, Facebook, Instagram, YouTube)
- Smart scheduler with rate limiting
- Content pipeline with approval workflow

### Changed
- Imported syndicate-legacy into Artifact/syndicate
- Added publish error migrations

## [2025-12-XX] - Infrastructure Foundation

### Added
- **Infra API**: FastAPI server with markets/assets/portfolio services
- Docker containerization with docker-compose
- Prometheus + Grafana monitoring stack
- Health check and startup scripts

### Changed
- Enabled CORS for dashboard integration
- Added reflection JSON for action tracking

## [2025-12-XX] - Initial Repository

### Added
- Repository foundation with AI-only contribution policy
- Architectural mandate for resilient fintech AI systems
- Lead-dev working directory with guidelines
- Authorization templates and enforcement workflow

---

## Statistics

- **Total Commits**: 165
- **Active Development Days**: 35+
- **Core Modules**: 8 (Cognition, Syndicate, Automata, Arty, Hektor, Infra, Dashboard, Projects)
- **Tools Implemented**: 18 native tools + 5 charting tools
- **Proposals Created**: 15+ self-improvement proposals
- **Charts Generated**: 6 per cycle (GOLD, SILVER, DXY, VIX, SPX, YIELD)

## Version Naming

- **v0.x.x**: Alpha development (current)
- **v1.0.0**: First stable release (planned Q1 2026)

---

*Generated: 2026-01-14*
