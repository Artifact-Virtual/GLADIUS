# Introduction to Arty

## What is Arty?

**Arty (Autonomous Research Team)** is a self-guided learning system that operates without human intervention. It conducts autonomous research, extracts knowledge, and engages across multiple platforms.

## Core Philosophy

Social media integrations (Discord, LinkedIn) are **drivers and adapters**, not the core purpose. The true essence is creating a system that learns autonomously through:

- Iterative web research
- Keyword extraction and refinement
- Content analysis without LLMs
- Intelligent knowledge organization
- Automated content generation and scheduling

## Key Capabilities

### Autonomous Research
- Configuration-driven research fields (broad + targeted)
- Self-guided keyword extraction and refinement
- Multi-iteration research cycles
- No LLM required - uses statistical analysis (TF-IDF, entity recognition)
- Cost-optimized batch processing

### Central Storage
- **SQLite3**: Structured data (12 tables for research, content, scheduling)
- **pgvector**: Vector embeddings (neural network ready)
- **File System**: Organized storage (articles, notes, papers, drafts, blueprints)

### Platform Automation
- **Discord**: Research-driven engagement with context-aware responses
- **LinkedIn**: Automated posting with research-based content

## Architecture Overview

```
arty/
├── store/              # Central storage (SQLite3 + pgvector + file system)
├── research/           # Autonomous research engine
├── discord/            # Discord bot with research integration
├── linkedin/           # LinkedIn automation with research content
└── docs/               # This documentation
```

## How It Works

**Research Loop (No Human Intervention):**
1. Configure research fields in `config.json`
2. Initial web search with broad keywords
3. Extract keywords from results (statistical analysis)
4. Refine searches with extracted keywords
5. Multi-iteration deep research
6. Clean, format, organize content
7. Generate posts for all platforms
8. Schedule and auto-publish

**Cost Optimization:**
- Single run every 2-3 days
- Generates all content in one batch
- Schedules posts for entire period
- Minimizes API calls

## Use Cases

- **Research Teams**: Automated literature review and knowledge gathering
- **Content Creators**: Research-driven content generation at scale
- **Community Managers**: Intelligent Discord engagement with context awareness
- **Professional Networking**: Automated LinkedIn presence with quality content
- **Knowledge Management**: Centralized research storage with semantic search

## Next Steps

Ready to get started? Proceed to [Quick Start](QUICKSTART.md).

Want to understand the architecture deeper? See [Storage Layer](STORAGE.md) and [Research Engine](RESEARCH.md).
