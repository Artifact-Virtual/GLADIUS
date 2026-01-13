# Gladius Operational Mandate

> Mission, responsibilities, and expectations for the Gladius autonomous enterprise system.

---

## Mission

Gladius is an autonomous enterprise operating system that:

1. **Manages context and vectorization** across all business artifacts
2. **Coordinates research** (Syndicate) and **trading** (Cthulu) operations
3. **Learns from outcomes** to improve prediction accuracy over time
4. **Scales horizontally** via independent artifact deployment
5. **Self-improves** through consensus-driven proposal system
6. **Maintains coherent context** across long-running sessions

---

## Key Responsibilities

### Availability
- Core services (Infra API, Dashboard, Syndicate) must be recoverable
- Health checks run automatically on startup
- Graceful shutdown with regression verification

### Data Integrity
- All reports ingested into cognition engine
- SQLite fallback ensures persistence
- Atomic writes with manifests
- Context versioning with rollback support

### Security
- No secrets committed to git
- Environment variables for API keys
- JWT authentication for Dashboard API
- Sandboxed workspace operations

### Observability
- Centralized logging
- Health check endpoints
- Prometheus metrics (planned)
- Context window usage tracking

### Governance
- Medium-impact changes require community consensus (Discord)
- High-impact changes escalate to dev team review (Email)
- Full audit trail for all proposals

---

## Artifacts Under Management

| Artifact | Codename | Mission | SLA Target |
|----------|----------|---------|------------|
| Alpha | Syndicate | Daily market research & signals | 99% (dev) |
| Beta | Cthulu | Trade execution & management | 99.9% (prod) |
| Theta | TBD | Social publishing & monetization | TBD |

---

## Cognition Engine Mandate

The cognition engine MUST:

1. **Ingest all generated reports** into vector memory
2. **Provide semantic context** to AI analysis
3. **Track prediction outcomes** for learning
4. **Maintain SQLite fallback** for robustness
5. **Route proposals** through consensus system
6. **Manage context** for narrative coherence

Current metrics:
- Documents indexed: 18+
- Win rate tracking: Active
- Vector dimension: 384
- Training examples: 155+
- Consensus sessions: Available
- Context management: Active

---

## Consensus System Mandate

Proposals are routed based on impact:

| Impact | Routing | Authority |
|--------|---------|-----------|
| Low | Auto-approve | System |
| Medium | Discord vote (60% threshold) | Community |
| High | Email escalation | Dev Team |
| Critical | Executive review | Leadership |

---

## Context Management Mandate

The system MUST:

1. **Maintain context window** under 8000 tokens
2. **Auto-summarize** when exceeding 6000 tokens
3. **Preserve high-importance** decisions and learnings
4. **Prune low-importance** observations
5. **Version context** for rollback capability
6. **Export context** for training data

---

## Operational Baseline

| Metric | Target | Current |
|--------|--------|---------|
| Service uptime | 99% | Active |
| Report generation | Daily | ✅ |
| Cognition ingestion | Per-cycle | ✅ |
| Context retrieval | < 1s | ✅ |
| Consensus routing | < 5s | ✅ |
| Context tokens | < 8000 | ✅ |

---

## Immediate Actions

1. ✅ Integrate cognition engine with Syndicate
2. ✅ Implement Consensus System
3. ✅ Implement Context Manager
4. 🚧 Configure Discord webhook for voting
5. 🚧 Configure SMTP for email escalation
6. 🚧 Run autonomous self-improvement cycle
7. 📋 Deploy Cthulu to production
8. 📋 Set up web presence (artifactvirtual.com)

---

## Ownership

- **Gladius Core**: Context, vectorization, memory, consensus
- **Syndicate (Alpha)**: Research, analysis, signals
- **Cthulu (Beta)**: Trading, execution, management
- **Infrastructure**: APIs, dashboards, deployment

---

*Last updated: 2026-01-13*