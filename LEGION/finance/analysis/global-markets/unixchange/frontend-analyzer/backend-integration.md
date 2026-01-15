// backend-integration.md
# Artifact Virtual Backend Integration (Analyzer)

## Artifact Standards
- Modular, API-driven, and agent-oriented
- Use WebSocket for real-time, REST for config/commands
- All data flows are auditable and append-only (see Artifact docs)
- Agent graph and chain pipeline must be pluggable and observable

## Integration Plan
1. **WebSocket API Contract**
   - Endpoint: `/ws/analyzer` (backend)
   - Message types: `market_data`, `ai_result`, `agent_command`, `agent_status`
   - All messages JSON, with `type` and `payload`
2. **REST API Contract**
   - `/api/analyzer/config` (GET/POST)
   - `/api/analyzer/command` (POST)
3. **Agent Graph/Chain Pipeline**
   - Each agent is a microservice (see ADAM Protocol)
   - Pipeline: Data → Perception → Memory → Action → Vault
   - Use event-driven, append-only logs for all agent actions
4. **Angular Backend Workspace**
   - Receives analyzer output via WebSocket
   - Sends commands/config via REST
   - Visualizes agent graph and pipeline status

## Example Message
```json
{
  "type": "ai_result",
  "payload": {
    "timestamp": "2025-06-09T12:00:00Z",
    "result": { "anomalies": 3, "mean": 42.1 }
  }
}
```

---

**Follow this plan to ensure Artifact-compliant, modular, and auditable backend integration.**
