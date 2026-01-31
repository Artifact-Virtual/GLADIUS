# GLADIUS Command Terminal — Technical Specifications

**Version**: 2.0
**Last Updated**: 2026-01-30

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────┐
│            ELECTRON SHELL (Chromium)            │
├─────────────────────────────────────────────────┤
│  Main Process  │  Preload  │  Renderer Process  │
│  Node.js       │  Bridge   │  React + TS        │
├─────────────────────────────────────────────────┤
│         IPC Communication Layer                 │
├─────────────────────────────────────────────────┤
│  Python Backend (gladius.sh, SENTINEL, LEGION)  │
└─────────────────────────────────────────────────┘
```

---

## TECHNOLOGY STACK

### Frontend
- **Electron 28+**: Desktop framework
- **React 18.2**: UI library
- **TypeScript 5**: Type safety
- **Tailwind CSS 3**: Styling
- **Chart.js 4**: Data visualization
- **Zustand**: State management

### Backend Integration
- **Python 3.10+**: Existing services
- **Child Process**: Spawn Python scripts
- **WebSocket**: Real-time streaming
- **IPC**: Electron inter-process communication

---

## SECURITY MODEL

### Renderer Isolation
- `nodeIntegration: false`
- `contextIsolation: true`
- `sandbox: true`
- CSP headers enforced

### IPC Validation
- All commands validated in main process
- No arbitrary code execution
- Password-protected sensitive operations
- Audit logging

---

## PERFORMANCE TARGETS

| Metric | Target |
|--------|--------|
| First Paint | < 500ms |
| Time to Interactive | < 1.5s |
| Memory (idle) | < 500 MB |
| Memory (active) | < 1 GB |
| CPU (idle) | < 5% |

---

## ACCESSIBILITY

- WCAG 2.1 AA compliant
- Full keyboard navigation
- Screen reader support
- High contrast mode

---

## DEPLOYMENT

Package for:
- macOS (DMG, signed)
- Linux (AppImage, DEB)
- Windows (NSIS installer)

