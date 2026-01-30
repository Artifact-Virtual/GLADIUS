# GLADIUS Command Terminal — Implementation Guide

**Version**: 2.0
**Last Updated**: 2026-01-30
**Purpose**: Step-by-step guide to implement the Electron dashboard

---

## PREREQUISITES

- Node.js 18+
- Python 3.10+
- Electron experience
- React + TypeScript experience
- Familiarity with GLADIUS system

---

## PHASE 1: PROJECT INITIALIZATION

### 1. Create Electron Project

```bash
cd /home/runner/work/GLADIUS/GLADIUS/ui
npm init -y
npm install --save-dev electron electron-builder typescript @types/node
npm install --save-dev vite @vitejs/plugin-react
```

### 2. Install UI Dependencies

```bash
npm install react react-dom
npm install @types/react @types/react-dom --save-dev
npm install tailwindcss postcss autoprefixer
npm install chart.js react-chartjs-2
npm install zustand
npm install lucide-react
npm install date-fns
```

### 3. Project Structure

```
ui/
├── electron/
│   ├── main.ts
│   ├── preload.ts
│   └── ipc/
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── stores/
│   └── types/
├── package.json
├── tsconfig.json
└── vite.config.ts
```

---

## PHASE 2: ELECTRON SETUP

### Main Process (electron/main.ts)

```typescript
import { app, BrowserWindow } from 'electron';
import * as path from 'path';

function createWindow() {
  const win = new BrowserWindow({
    width: 1920,
    height: 1080,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      sandbox: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  win.loadFile('index.html');
}

app.whenReady().then(createWindow);
```

---

## PHASE 3: IPC CHANNELS

Create handlers for each backend system:

- `gladius:*` - GLADIUS operations
- `sentinel:*` - SENTINEL daemon
- `legion:*` - Agent orchestration
- `logs:*` - Log streaming
- `artifact:*` - Artifact operations

---

## PHASE 4: UI IMPLEMENTATION

### Component Order

1. Layout components (Grid, Split, Tabs)
2. Core components (StatusCard, MetricChart)
3. Page components (Mission Overview first)
4. Navigation and routing
5. Command palette
6. Polish and refinement

---

## PHASE 5: INTEGRATION

Connect to Python backend:
- Spawn Python processes
- Stream stdout/stderr
- Handle errors gracefully
- Implement reconnection logic

---

## PHASE 6: TESTING & DEPLOYMENT

1. Unit tests for components
2. Integration tests for IPC
3. E2E tests for workflows
4. Package with electron-builder
5. Create installers

---

## QUICK START COMMANDS

```bash
# Development
npm run dev

# Build
npm run build

# Package
npm run package

# Test
npm test
```

---

See page blueprints for detailed implementation specs.

