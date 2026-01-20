# UX Flow — GLADIUS Command Terminal

## Navigation Map

```
┌──────────────────────────────┐
│ Global Top Bar               │
│  • System clock              │
│  • Environment (prod/dev)    │
│  • Quick actions             │
└──────────────────────────────┘
│ Mission Overview │ Command Palette │
│ (default view)   │ (Cmd/Ctrl + K)  │
│                  │                 │
├────────────────────────────────────┤
│ Tabs:                              │
│ 1. Mission                         │
│ 2. Training                        │
│ 3. Sentinel Guard                  │
│ 4. Logs                            │
│ 5. Agents (LEGION)                 │
│ 6. Artifact                        │
└────────────────────────────────────┘
```

### 1. Mission Overview
* Tiles for SENTINEL, GLADIUS, LEGION, Artifact, Observability.
* Click tile → drill-down tab.
* Live health feed from `gladius.sh status` (auto-refresh every 5s).

### 2. Command Palette
* Summoned via shortcut.
* Fuzzy search common tasks (`start sentinel`, `training resume`, `legion agent list`).
* Each action opens a new terminal pane with live output and log bookmarking.

### 3. Training Console
* Split view: Rich terminal stream + metric panels (loss, throughput, expert coverage).
* Buttons: Start fresh, Resume, Dry run, Open monitor (invokes `live_monitor.py` UI).
* Allows exporting checkpoints/GGUF (future).

### 4. Sentinel Guard
* Shows guardian targets, restart counters, watchdog log tail.
* “Kill switch” button opens secure modal requiring password (handled main-process only).
* Buttons: Scan now, Target list, Threat report.

### 5. LEGION Agents
* Grid of departments with status, queue depth.
* Buttons call `LEGION/legion/cli.py` commands; output piped into console panel.
* Context menu to open agent config (read-only) or restart a subsystem via `gladius.sh`.

### 6. Logs Explorer
* Tree of log files (GLADIUS/logs, SENTINEL/logs, Artifact/logs, etc).
* Search and filter.
* “Bookmark” feature to capture a snippet into case notes.

### 7. Artifact Panel
* Display Syndicate cycle status, Qwen operational trainer info, Arty automations.
* Buttons for `qwen_operational.py --status`, `npm run research:cycle`, etc.

## Interaction Principles

1. **Keyboard-first** — global shortcuts, tab navigation, command palette.
2. **Non-blocking** — long-running commands execute in background tabs; user can detach.
3. **Immutable history** — command outputs retained per session for audit.
4. **Context aware** — warnings if dependent service is down before running a command.
5. **Minimal color palette** — align with GLADIUS terminal branding.

## Future Enhancements

* Multi-window layout (e.g., dedicated Training window).
* Notification center for Sentinel alerts.
* Embedded markdown notebook for operator annotations.
