# Gladius Operational Mandate

> Mission, responsibilities, and expectations for the Gladius autonomous enterprise system.

---

## Mission

Gladius is an autonomous enterprise operating system that:

1. **Manages context and vectorization** across all business artifacts
2. **Coordinates research** (Syndicate) and **trading** (Cthulu) operations
3. **Learns from outcomes** to improve prediction accuracy over time
4. **Scales horizontally** via independent artifact deployment

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

### Security
- No secrets committed to git
- Environment variables for API keys
- JWT authentication for Dashboard API

### Observability
- Centralized logging
- Health check endpoints
- Prometheus metrics (planned)

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

Current metrics:
- Documents indexed: 12+
- Win rate tracking: Active
- Vector dimension: 384

---

## Operational Baseline

| Metric | Target | Current |
|--------|--------|---------|
| Service uptime | 99% | Active |
| Report generation | Daily | ✅ |
| Cognition ingestion | Per-cycle | ✅ |
| Context retrieval | < 1s | ✅ |

---

## Immediate Actions

1. ✅ Integrate cognition engine with Syndicate
2. 🚧 Fix Hektor VDB for native performance
3. 🚧 Deploy Cthulu to production
4. 📋 Set up web presence (artifactvirtual.com)
5. 📋 Implement blockchain/token architecture

---

## Ownership

- **Gladius Core**: Context, vectorization, memory
- **Syndicate (Alpha)**: Research, analysis, signals
- **Cthulu (Beta)**: Trading, execution, management
- **Infrastructure**: APIs, dashboards, deployment

---

*Last updated: 2026-01-13*