# GLADIUS Command Terminal (Electron)

This workspace will host the hardened Electron-based operator console for the GLADIUS stack.

## Status

- [x] Architecture and UX requirements captured (see `docs/ARCHITECTURE.md` and `docs/UX_FLOW.md`)
- [ ] Electron scaffolding (main/preload/renderer)
- [ ] IPC bridges for SENTINEL, GLADIUS, LEGION, Artifact
- [ ] Training monitor integration
- [ ] Packaging scripts

## Development Plan

1. Finalize threat model and data-flow diagrams.
2. Scaffold Electron project (`npm create @electron/app` + Vite/React renderer).
3. Implement secure preload bridges with strict TypeScript contracts.
4. Port existing CLI workflows into IPC actions.
5. Build renderer dashboards (Mission overview, Command palette, Training console, Sentinel guard).
6. Package via `electron-builder` and document installation.

> **Note:** No Electron dependencies are installed yet; this repo stage only captures design intent. The next step is initializing the actual project structure once the design is approved.
