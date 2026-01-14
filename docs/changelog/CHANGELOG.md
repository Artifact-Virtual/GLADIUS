# CHANGELOG

All notable changes to the Gladius Enterprise System are documented here.

## [Unreleased]

### In Progress
- GGUF model fine-tuning for complete Ollama replacement
- Grafana dashboard integration
- React frontend completion

## [2026-01-14] - Consensus & ERP Integration Complete

### Added
- **SMTP Email Escalation**: Fully operational via smtp.hostinger.com:465 (SSL)
  - Account: ali.shakil@artifactvirtual.com
  - Aliases: admin@, adam@, gladius@, support@ all route to same inbox
  - Test emails confirmed working
- **Discord Consensus System**: Fully operational
  - Webhook configured and tested
  - Voting sessions ready for proposals
  - Impact-based routing (low→auto, medium→Discord, high→email, critical→executive)
- **ERP Integration Tools**: 8 new tools added to registry
  - `erp_sync_customers`, `erp_sync_products`, `erp_sync_orders`, `erp_sync_inventory`
  - `erp_get_status`, `erp_create_customer`, `erp_create_order`, `erp_update_inventory`
- **Governance Tools**: 4 new tools added
  - `create_proposal`, `route_proposal`, `get_voting_status`, `send_escalation_email`
- **System Mapping Files**: Documentation for each module
  - `src/cognition/SYSTEM_MAPPING.md` - Cognition engine commands
  - `automata/social_media/SYSTEM_MAPPING.md` - Social media commands
  - `automata/erp_integrations/SYSTEM_MAPPING.md` - ERP integration commands
  - `src/publishing/SYSTEM_MAPPING.md` - Publishing pipeline commands
- **SMTP Test Script**: `scripts/test_smtp_consensus.py` for verification
- **Enhanced Chart Annotations**: RSI, ADX, ATR indicators with subplots
- **Support/Resistance Levels**: Automatic detection and visualization
- **Trade Setup Visualization**: Entry/exit zones on charts
- **Autonomous Daemon Mode**: `--auto` flag for indefinite self-running operation

### Changed
- Tool registry expanded from 22 to 37+ tools
- Consensus system now uses `DISCORD_WEBHOOK_URL` with fallback
- Email config uses `ali.shakil@artifactvirtual.com` with SSL on port 465
- Flight checklist updated to 75% completion (was 65%)
- Charts now include multi-panel layout (price, volume, RSI, ADX)

### Fixed
- SMTP connection using SSL instead of STARTTLS for Hostinger
- Discord webhook fallback chain for consensus
- Email recipient parsing for dev team and executives
- Chart annotation positioning for better readability

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
