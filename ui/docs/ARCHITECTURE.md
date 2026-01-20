# GLADIUS Command Terminal — Architecture

## Goals

* Provide a local-first, air-gapped friendly control plane for the entire GLADIUS enterprise stack.
* Eliminate browser attack surface (no exposed HTTP dashboards).
* Offer mission-critical workflows (SENTINEL guard, GLADIUS training, LEGION orchestration, Artifact automation) through a single secure desktop.

## High-Level Stack

| Layer | Tech | Notes |
| --- | --- | --- |
| Shell | Electron main process | Creates windows, enforces security policy, manages IPC |
| Bridge | Preload scripts (`contextBridge`) | Expose whitelisted APIs for renderer (e.g., `ipc.invoke('gladius:startCycle')`) |
| Renderer | React + TypeScript + Tailwind (or plain) | Provides modular panes, theming, keyboard-first UX |
| Backends | Existing scripts (`gladius.sh`, `sentinel/start_sentinel.sh`, `LEGION/cli.py`, etc.) | Spawned as child processes; stdout/stderr multiplexed into UI |

## Module Breakdown

```
ui/
├── electron/
│   ├── main.ts              # window creation, menu, auto-updates
│   ├── preload.ts           # contextBridge exports (logs, commands)
│   ├── security.ts          # CSP, permission policies, sandbox rules
│   └── ipc/
│       ├── gladius.ts       # wraps gladius.sh commands
│       ├── sentinel.ts      # status/start/stop/targets
│       ├── legion.ts        # agent orchestration
│       └── artifact.ts      # syndicate, qwen operations
├── renderer/
│   ├── components/
│   │   ├── MissionOverview.tsx
│   │   ├── CommandPalette.tsx
│   │   ├── TrainingConsole.tsx
│   │   ├── SentinelGuard.tsx
│   │   └── LogExplorer.tsx
│   ├── hooks/useIpcStream.ts
│   ├── state (Zustand/Redux) for telemetry caching
│   └── styles (Tailwind, tokens)
└── docs/
    ├── ARCHITECTURE.md (this file)
    └── UX_FLOW.md
```

## IPC Channels (Initial)

| Channel | Arguments | Result | Notes |
| --- | --- | --- | --- |
| `gladius:status` | – | Parsed output of `./gladius.sh status` | JSON normalized |
| `gladius:cycle` | options? | stream id | Runs `./gladius.sh cycle` |
| `sentinel:status` | – | {watchdogPid, learningRunning, heartbeat} | Pulls from `start_sentinel.sh status` |
| `sentinel:command` | `{action:'start'|'stop'|'scan', payload}` | success/error | Stop requires secure password prompt |
| `training:start` | `{resume:boolean,maxHours:number}` | stream id | Runs trainer in PTY, also updates monitor |
| `training:state` | – | JSON from `moe_training_state.json` | Reused by renderer for graphs |
| `logs:tail` | `{path:string}` | stream id | Streams log files (read-only) |

## Security Considerations

1. **Renderer isolation** — `nodeIntegration=false`, `contextIsolation=true`, `enableRemoteModule=false`.
2. **IPC validation** — Every request validated server-side; reject arbitrary commands.
3. **Secrets** — Sensitive env (kill passwords, tokens) never exposed to renderer; prompts handled via native dialogs and stored only in main memory.
4. **Auto-updates** — Optional; default offline packaging.
5. **Auditability** — All operations logged to `ui/logs/operator_<date>.log`.

## Next Steps

1. Finalize UX flows (see `UX_FLOW.md`) and confirm component layout.
2. Initialize Electron project structure with TypeScript, ESLint, Tailwind.
3. Implement IPC scaffolding with placeholder data.
4. Build renderer shells (panels without live data).
5. Integrate real process execution and log streaming.
