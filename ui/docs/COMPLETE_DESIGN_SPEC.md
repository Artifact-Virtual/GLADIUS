# GLADIUS COMMAND TERMINAL — Complete Design Specification

**Version**: 2.0  
**Last Updated**: 2026-01-30  
**Status**: Enterprise Internal Application - Full Design

---

## EXECUTIVE SUMMARY

The GLADIUS Command Terminal is an **enterprise-grade Electron desktop application** for internal operations.

### Design Goals

✅ **Enterprise-First**: Professional, functional, WCAG 2.1 AA compliant  
✅ **Keyboard-Driven**: Complete keyboard navigation  
✅ **Real-Time**: Live data streaming  
✅ **Secure**: Air-gapped capable  
✅ **Accessible**: Full accessibility support

---

## DESIGN PRINCIPLES

1. **Clarity Over Aesthetics** - Information hierarchy paramount
2. **Keyboard-First** - All features keyboard-accessible
3. **Real-Time Awareness** - Live status indicators
4. **Progressive Disclosure** - Summary → Details
5. **Consistent Patterns** - Unified UI elements
6. **Accessibility** - WCAG 2.1 AA compliance

---

## SYSTEM ARCHITECTURE

```
┌──────────────────────────────────────────────────────────────┐
│                    ELECTRON MAIN PROCESS                      │
│  • Window Management                                         │
│  • Security Policy                                           │
│  • IPC Validation                                            │
└────────────────────┬─────────────────────────────────────────┘
                     │
     ┌───────────────┼──────────────┐
     │               │              │
┌────▼────┐    ┌────▼────┐   ┌────▼────┐
│PRELOAD  │    │RENDERER │   │BACKEND  │
│         │    │React UI │   │Python   │
│IPC APIs │    │Charts   │   │Scripts  │
└─────────┘    └─────────┘   └─────────┘
```

---

## TECHNOLOGY STACK

| Layer | Technology |
|-------|-----------|
| Shell | Electron 28+ |
| UI | React 18.2 + TypeScript 5 |
| Styling | Tailwind CSS 3 |
| State | Zustand |
| Charts | Chart.js 4 |
| Icons | Lucide React |
| Backend | Python 3.10+ |

---

## COLOR SCHEME

### Dark Theme (Default)

```
Background:    #0A0E27 (Deep Navy)
Secondary:     #151B3B (Dark Slate)
Accent:        #1E2749 (Midnight Blue)

Text Primary:  #E4E7EB (Light Gray)
Text Secondary:#9CA3AF (Medium Gray)

Primary:       #3B82F6 (Blue)
Success:       #10B981 (Green)
Warning:       #F59E0B (Amber)
Error:         #EF4444 (Red)
Info:          #8B5CF6 (Purple)
```

---

## KEYBOARD SHORTCUTS

| Shortcut | Action |
|----------|--------|
| `Cmd/Ctrl + K` | Command palette |
| `Cmd/Ctrl + 1-6` | Switch tabs |
| `Cmd/Ctrl + L` | Focus logs |
| `Cmd/Ctrl + R` | Refresh |
| `Tab` | Next element |
| `Esc` | Close modal |

