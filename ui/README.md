# GLADIUS Electron Dashboard

Enterprise-grade Electron desktop application for managing and monitoring GLADIUS AI systems, SENTINEL security operations, LEGION agent orchestration, and Artifact management.

## 🚀 Features

### Implemented ✅
- **IPC Communication Layer** - Complete bidirectional communication between Electron and Python subsystems
- **System Status Monitoring** - Real-time status tracking for all modules
- **Dark Theme UI** - Professional dark theme with cyan/purple accents
- **Responsive Layout** - Sidebar navigation, header, and content areas
- **Type-Safe Architecture** - Full TypeScript support with strict typing
- **State Management** - Zustand-based global state management
- **Security Hardened** - Input validation, sanitization, and command injection protection
- **Cross-Platform** - Automatic Python executable detection (Windows/Unix)

### In Progress 🚧
- Module-specific interfaces (GLADIUS, SENTINEL, LEGION, Artifact)
- Real-time log streaming and monitoring
- Command palette
- Charts and visualizations

## 📦 Installation

```bash
cd ui
npm install
```

## 🔧 Development

### Start Development Server
```bash
npm run dev
```
This runs both Vite (React) and Electron in development mode.

### Build for Production
```bash
# Build React app
npm run build

# Build Electron app
npm run build:electron

# Package for distribution
npm run package
```

## 🏗️ Architecture

### Directory Structure
```
ui/
├── electron/               # Electron main process
│   ├── ipc/               # IPC handlers
│   │   ├── gladius.ts     # GLADIUS operations
│   │   ├── sentinel.ts    # SENTINEL operations
│   │   ├── legion.ts      # LEGION operations
│   │   ├── logs.ts        # Log streaming
│   │   ├── artifact.ts    # Artifact management
│   │   └── utils.ts       # Security utilities
│   ├── main.ts            # Main process entry
│   └── preload.ts         # Preload script (contextBridge)
├── src/                   # React renderer process
│   ├── components/        # Reusable components
│   ├── pages/             # Page components
│   ├── stores/            # Zustand stores
│   ├── styles/            # Tailwind CSS
│   ├── types/             # TypeScript definitions
│   ├── App.tsx            # Main app component
│   └── main.tsx           # React entry point
└── index.html             # HTML entry point
```

### IPC Communication Flow
```
React Component
  ↓ window.electron.gladius.status()
Preload Script (contextBridge)
  ↓ ipcRenderer.invoke('gladius:status')
Main Process (IPC Handler)
  ↓ spawn('python3', ['gladius_cli.py', 'status'])
Python CLI Script
  ↓ executes command
GLADIUS/SENTINEL/LEGION/Artifact Systems
```

## 🎨 Design System

### Colors
- **Primary Background:** `#0A0E27`
- **Secondary Background:** `#1A1F3A`
- **Accent Cyan:** `#00D9FF`
- **Accent Purple:** `#9D4EDD`
- **Success Green:** `#00FF87`
- **Warning Yellow:** `#FFB800`
- **Error Red:** `#FF3366`

### Component Classes
- `.btn-primary` - Primary action button
- `.btn-secondary` - Secondary action button
- `.btn-ghost` - Ghost button
- `.card` - Standard card
- `.card-glass` - Glass-morphism card
- `.badge-*` - Status badges (success, warning, error, info)
- `.sidebar-link` - Navigation link
- `.gradient-text` - Gradient text effect

## 🔐 Security

### Input Validation
All user inputs are validated and sanitized:
- **String sanitization** - Removes dangerous shell characters
- **Path validation** - Prevents path traversal attacks
- **Numeric validation** - Enforces min/max bounds
- **Filename validation** - Restricts to safe patterns
- **Array sanitization** - Sanitizes each element

### Process Security
- No shell execution (`spawn` without shell option)
- Arguments passed as arrays, not concatenated strings
- Proper process lifecycle management
- Graceful shutdown with cleanup handlers

### Electron Security
- ✅ Context Isolation enabled
- ✅ Node Integration disabled in renderer
- ✅ Sandbox mode enabled
- ✅ Content Security Policy enforced
- ✅ contextBridge for safe IPC

See [SECURITY_SUMMARY.md](./SECURITY_SUMMARY.md) for detailed security analysis.

## 📚 API Reference

### GLADIUS Operations
```typescript
window.electron.gladius.status()
window.electron.gladius.benchmark({ dataset, metric })
window.electron.gladius.train({ dataset, epochs, batchSize })
window.electron.gladius.interact(message)
```

### SENTINEL Operations
```typescript
window.electron.sentinel.status()
window.electron.sentinel.start({ port, logLevel })
window.electron.sentinel.stop()
window.electron.sentinel.scan(target, { depth, profile })
```

### LEGION Operations
```typescript
window.electron.legion.status()
window.electron.legion.listAgents()
window.electron.legion.createAgent({ name, type, role })
window.electron.legion.deployAgent(agentId, { target, mode })
window.electron.legion.stopAgent(processId)
```

### Log Operations
```typescript
window.electron.logs.list()
window.electron.logs.read(logName, lines)
window.electron.logs.streamStart(logName)
window.electron.logs.streamStop(logName)
window.electron.logs.clear(logName)
window.electron.logs.onStreamData(callback)
```

### Artifact Operations
```typescript
window.electron.artifact.status()
window.electron.artifact.list({ type, tag })
window.electron.artifact.get(artifactId)
window.electron.artifact.create({ name, type, path, description, tags })
window.electron.artifact.delete(artifactId)
window.electron.artifact.export(artifactId, destination)
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run linter
npm run lint
```

## 📊 Build Status

- ✅ TypeScript compilation: **PASSING**
- ✅ Vite production build: **PASSING**
- ✅ CodeQL security scan: **PASSING** (0 alerts)
- ✅ Code review: **ADDRESSED** (all critical issues fixed)

## 🛠️ Technologies

- **Electron** - Desktop application framework
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Zustand** - State management
- **React Router** - Client-side routing
- **Lucide React** - Icon library
- **Tail** - Log file monitoring

## 📝 License

PROPRIETARY - Artifact Virtual

## 👥 Authors

Artifact Virtual Development Team

## 🔗 Related Documentation

- [Architecture](./docs/ARCHITECTURE.md)
- [Component Library](./docs/COMPONENT_LIBRARY.md)
- [Implementation Guide](./docs/IMPLEMENTATION_GUIDE.md)
- [Implementation Status](./IMPLEMENTATION_STATUS.md)
- [Security Summary](./SECURITY_SUMMARY.md)

## 🚦 Next Steps

1. Implement full page interfaces for each module
2. Add real-time WebSocket/IPC event streaming
3. Create command palette component
4. Add charts and data visualizations
5. Implement settings persistence
6. Add comprehensive test coverage
7. Create error boundary components
8. Implement notification system
9. Add keyboard shortcuts
10. Production deployment configuration
