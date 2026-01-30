# PAGE 01: MISSION OVERVIEW
## Enterprise Dashboard - Primary Command Interface

**Version:** 1.0.0  
**Status:** Production Blueprint  
**Purpose:** Central command interface for GLADIUS system monitoring and control

---

## ASCII BLUEPRINT LAYOUT

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  GLADIUS MISSION CONTROL                                    [?] [⚙] [🔔] [@user] [X] ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║  ┌─ SYSTEM STATUS GRID ─────────────────────────────────────────────────────────┐   ║
║  │                                                                               │   ║
║  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │   ║
║  │  │   🤖 GLADIUS     │  │   👁 SENTINEL    │  │   ⚔ LEGION       │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   STATUS: ●●●●●○ │  │   STATUS: ●●●●●● │  │   STATUS: ●●●●○○ │          │   ║
║  │  │   [TRAINING]     │  │   [ACTIVE]       │  │   [READY]        │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   Epoch: 47/100  │  │   Threats: 0     │  │   Agents: 26/26  │          │   ║
║  │  │   Loss: 0.0234   │  │   Uptime: 72h    │  │   Queue: 145     │          │   ║
║  │  │   ETA: 4.2h      │  │   CPU: 23%       │  │   Tasks/s: 47    │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   [MONITOR]      │  │   [GUARD]        │  │   [MANAGE]       │          │   ║
║  │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │   ║
║  │                                                                               │   ║
║  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐          │   ║
║  │  │  📊 SYNDICATE    │  │  🏭 AUTOMATA     │  │  💻 SYSTEM       │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   STATUS: ●●●●●● │  │   STATUS: ●●●●●● │  │   STATUS: ●●●●●● │          │   ║
║  │  │   [RESEARCHING]  │  │   [PUBLISHING]   │  │   [HEALTHY]      │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   Markets: 4     │  │   Packages: 12   │  │   CPU: 34%       │          │   ║
║  │  │   Data/hr: 2.4k  │  │   Downloads: 89k │  │   RAM: 8.2/32GB  │          │   ║
║  │  │   APIs: 8/8      │  │   Status: ✓✓✓   │  │   Disk: 45%      │          │   ║
║  │  │                  │  │                  │  │                  │          │   ║
║  │  │   [REPORTS]      │  │   [PUBLISH]      │  │   [DIAGNOSTICS]  │          │   ║
║  │  └──────────────────┘  └──────────────────┘  └──────────────────┘          │   ║
║  │                                                                               │   ║
║  └───────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
║  ┌─ REAL-TIME METRICS ───────────────────────────────────────────────────────────┐   ║
║  │                                                                                │   ║
║  │  CPU USAGE (34%)          MEMORY (8.2GB/32GB)        NETWORK (↓ 45MB/s)      │   ║
║  │  ████████░░░░░░░░░░░       ████████░░░░░░░░░░░        ████████████░░░░       │   ║
║  │                                                                                │   ║
║  │  GPU TEMP (67°C)          DISK I/O (234 MB/s)        ACTIVE THREADS (156)    │   ║
║  │  ██████████░░░░░░░░        ███████████████░░░         ████████████████       │   ║
║  │                                                                                │   ║
║  └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
║  ┌─ QUICK ACTIONS ──────────────┐  ┌─ ACTIVITY FEED ──────────────────────────┐    ║
║  │                               │  │                                          │    ║
║  │  [▶ START TRAINING]          │  │  ⏱ 14:32:18 - Training epoch 47 started  │    ║
║  │  [⏸ PAUSE OPERATIONS]        │  │  ✓ 14:30:05 - SENTINEL scan completed   │    ║
║  │  [🔄 SYNC ARTIFACTS]         │  │  ℹ 14:28:42 - LEGION agent A deployed    │    ║
║  │  [📊 GENERATE REPORT]        │  │  ⚠ 14:25:15 - High memory usage detected │    ║
║  │  [🚨 EMERGENCY STOP]         │  │  ✓ 14:20:33 - Artifact sync complete    │    ║
║  │  [⚙ SYSTEM SETTINGS]         │  │  ℹ 14:18:07 - SYNDICATE data refreshed   │    ║
║  │                               │  │  ✓ 14:15:44 - Backup completed          │    ║
║  │  [📁 OPEN LOGS]              │  │  ℹ 14:12:29 - New agent task queued      │    ║
║  │  [🔍 SEARCH ARTIFACTS]       │  │  ✓ 14:10:18 - Health check passed       │    ║
║  │  [📤 EXPORT DATA]            │  │  ℹ 14:08:55 - Config reloaded           │    ║
║  │                               │  │                                          │    ║
║  │                               │  │  [View All Activity →]                   │    ║
║  └───────────────────────────────┘  └──────────────────────────────────────────┘    ║
║                                                                                       ║
║  ┌─ SYSTEM HEALTH ────────────────────────────────────────────────────────────────┐  ║
║  │                                                                                 │  ║
║  │  Last Health Check: 2 minutes ago                                              │  ║
║  │  Next Scheduled Check: 8 minutes                                               │  ║
║  │                                                                                 │  ║
║  │  ✓ All subsystems operational      ✓ Network connectivity stable              │  ║
║  │  ✓ Database connections healthy    ✓ API endpoints responsive                 │  ║
║  │  ⚠ Memory usage above 75%          ✓ Disk space sufficient (55% free)        │  ║
║  │                                                                                 │  ║
║  └─────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝

STATUS BAR: GLADIUS v2.0.0 | Uptime: 72h 14m | Last Sync: 2m ago | [CTRL+K] Command
```

---

## COMPONENT SPECIFICATIONS

### 1. HEADER BAR
**Location:** Top fixed position  
**Height:** 48px  
**Components:**
- **Title:** "GLADIUS MISSION CONTROL" - Bold, 18pt
- **Help Icon [?]:** Opens contextual help overlay
- **Settings [⚙]:** Opens system configuration panel
- **Notifications [🔔]:** Badge count for unread alerts
- **User Menu [@user]:** Dropdown with profile/logout
- **Close [X]:** Minimize/close application

**Interactions:**
- All icons clickable with hover tooltips
- Notification badge pulses when new alerts arrive
- Double-click title bar to maximize/restore window

---

### 2. STATUS GRID (6 Cards)

#### Card Layout Specification
**Dimensions:** 250px x 200px per card  
**Spacing:** 20px gap between cards  
**Grid:** 3 columns x 2 rows  

#### Card A: GLADIUS
**Icon:** 🤖 Robot face  
**Primary Status:** Training progress bar (6-segment)  
**State Badge:** [TRAINING] | [IDLE] | [EVALUATING]  
**Metrics:**
- **Epoch:** Current/Total (e.g., 47/100)
- **Loss:** Current loss value (4 decimal places)
- **ETA:** Time remaining in hours/minutes
**Action Button:** [MONITOR] - Opens Training Console

**Status States:**
- ●●●●●● (6 filled) - Optimal
- ●●●●●○ (5 filled) - Good
- ●●●●○○ (4 filled) - Fair
- ●●●○○○ (3 filled) - Warning
- ●●○○○○ (2 filled) - Critical
- ●○○○○○ (1 filled) - Emergency

#### Card B: SENTINEL
**Icon:** 👁 Eye  
**Primary Status:** Guardian health indicator  
**State Badge:** [ACTIVE] | [SCANNING] | [ALERT] | [OFFLINE]  
**Metrics:**
- **Threats:** Active threat count
- **Uptime:** Hours of continuous operation
- **CPU:** CPU usage percentage
**Action Button:** [GUARD] - Opens Sentinel Guard page

#### Card C: LEGION
**Icon:** ⚔ Crossed swords  
**Primary Status:** Agent fleet readiness  
**State Badge:** [READY] | [BUSY] | [DEPLOYING] | [IDLE]  
**Metrics:**
- **Agents:** Active/Total agent count
- **Queue:** Pending task count
- **Tasks/s:** Task completion rate
**Action Button:** [MANAGE] - Opens LEGION Agents page

#### Card D: SYNDICATE
**Icon:** 📊 Chart with upward trend  
**Primary Status:** Market intelligence gathering  
**State Badge:** [RESEARCHING] | [ANALYZING] | [IDLE]  
**Metrics:**
- **Markets:** Active market connections
- **Data/hr:** Data points collected per hour
- **APIs:** Connected/Total API count
**Action Button:** [REPORTS] - Opens Artifact Ops page

#### Card E: AUTOMATA
**Icon:** 🏭 Factory  
**Primary Status:** Publishing automation status  
**State Badge:** [PUBLISHING] | [SYNCING] | [IDLE] | [ERROR]  
**Metrics:**
- **Packages:** Total published packages
- **Downloads:** Total download count
- **Status:** Health check icons (✓✓✓)
**Action Button:** [PUBLISH] - Opens Artifact Ops page

#### Card F: SYSTEM
**Icon:** 💻 Computer  
**Primary Status:** Overall system health  
**State Badge:** [HEALTHY] | [WARNING] | [CRITICAL]  
**Metrics:**
- **CPU:** System CPU usage percentage
- **RAM:** Used/Total memory in GB
- **Disk:** Disk usage percentage
**Action Button:** [DIAGNOSTICS] - Opens system diagnostics

---

### 3. REAL-TIME METRICS PANEL

**Height:** 120px  
**Update Frequency:** 1 second  
**Metrics (6 total):**

#### Metric Display Format
```
METRIC NAME (value)
████████░░░░░░░░░  [Visual bar]
```

**Metrics:**
1. **CPU USAGE** - 0-100% with 20-segment bar
2. **MEMORY** - Used/Total with 20-segment bar
3. **NETWORK** - Download speed with arrow icon
4. **GPU TEMP** - Temperature in Celsius
5. **DISK I/O** - Read/Write speed in MB/s
6. **ACTIVE THREADS** - Thread count

**Color Coding (when rendered):**
- Green (0-60%): Optimal
- Yellow (61-80%): Warning
- Red (81-100%): Critical

---

### 4. QUICK ACTIONS PANEL

**Dimensions:** 300px width x 400px height  
**Position:** Bottom-left quadrant  
**Button Count:** 10

**Button Specifications:**
- Height: 36px each
- Full-width with 10px padding
- Icon + Text label
- Hover state shows tooltip with shortcut key
- Disabled state when action unavailable

**Actions List:**
1. **[▶ START TRAINING]** - Initiates GLADIUS training - Ctrl+T
2. **[⏸ PAUSE OPERATIONS]** - Pauses all active operations - Ctrl+P
3. **[🔄 SYNC ARTIFACTS]** - Syncs artifact repositories - Ctrl+S
4. **[📊 GENERATE REPORT]** - Creates system report - Ctrl+R
5. **[🚨 EMERGENCY STOP]** - Kills all processes - Ctrl+Shift+X
6. **[⚙ SYSTEM SETTINGS]** - Opens settings - Ctrl+,
7. **[📁 OPEN LOGS]** - Opens Logs Explorer - Ctrl+L
8. **[🔍 SEARCH ARTIFACTS]** - Search interface - Ctrl+F
9. **[📤 EXPORT DATA]** - Export system data - Ctrl+E
10. **[🔄 REFRESH ALL]** - Refresh all data - F5

---

### 5. ACTIVITY FEED

**Dimensions:** Flexible width, 400px height  
**Position:** Bottom-right quadrant  
**Capacity:** Last 100 events, display 10 at a time  
**Auto-scroll:** Yes, when new events arrive

**Event Format:**
```
[ICON] HH:MM:SS - Event description text
```

**Event Types:**
- ⏱ **Timer** - Scheduled events
- ✓ **Success** - Completed operations
- ℹ **Info** - Informational messages
- ⚠ **Warning** - Warning conditions
- ❌ **Error** - Error conditions
- 🔔 **Alert** - Critical alerts

**Features:**
- Click event to view details
- Right-click for context menu (Copy, Clear)
- Search/filter events
- Export event log
- Auto-hide resolved warnings

**Footer Button:**
- [View All Activity →] - Opens full activity log viewer

---

### 6. SYSTEM HEALTH SUMMARY

**Height:** 100px  
**Position:** Bottom of page, above status bar  
**Update Frequency:** 5 minutes (health checks)

**Display Components:**
- **Last Check Time:** Relative time display
- **Next Check Time:** Countdown to next check
- **Health Indicators:** 6 key system checks with ✓/⚠/❌ icons

**Health Checks:**
1. All subsystems operational
2. Network connectivity stable
3. Database connections healthy
4. API endpoints responsive
5. Memory/CPU within limits
6. Disk space sufficient

**Auto-actions:**
- Health check runs every 10 minutes
- Failed checks trigger notifications
- Critical failures auto-escalate

---

### 7. STATUS BAR

**Height:** 24px  
**Position:** Fixed bottom  
**Background:** Dark theme accent

**Segments (Left to Right):**
1. **Version:** GLADIUS v2.0.0
2. **Uptime:** System uptime (72h 14m format)
3. **Last Sync:** Time since last data sync
4. **Command Hint:** [CTRL+K] Command palette shortcut

**Interactions:**
- Click version to show changelog
- Click uptime to show detailed system info
- Click last sync to force sync
- Status bar right-click for quick settings

---

## INTERACTION PATTERNS

### Mouse Interactions
- **Click Status Card:** Expand to full-screen details
- **Hover Card:** Show quick tooltip with extended metrics
- **Right-Click Card:** Context menu (Refresh, Pin, Export)
- **Drag Card:** Reorder cards (saved to user preferences)
- **Double-Click Metric:** Open detailed metric history graph

### Keyboard Navigation
- **Tab:** Cycle through interactive elements
- **Enter:** Activate focused button/card
- **Space:** Toggle selection on focused item
- **Escape:** Close any open modal/overlay
- **Arrow Keys:** Navigate grid (2D navigation)

### Real-time Updates
- **Status Badges:** Update every 2 seconds
- **Metrics:** Update every 1 second
- **Activity Feed:** Real-time push notifications
- **Health Checks:** Every 10 minutes + on-demand

### Responsive Behavior
- **Window Width < 1200px:** Grid changes to 2 columns
- **Window Width < 800px:** Grid changes to 1 column (mobile)
- **Activity Feed:** Auto-hide on small screens (accessible via button)

---

## KEYBOARD SHORTCUTS

### Global Shortcuts (Available on this page)
| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open Command Palette |
| `Ctrl+T` | Start Training (GLADIUS) |
| `Ctrl+P` | Pause All Operations |
| `Ctrl+S` | Sync Artifacts |
| `Ctrl+R` | Generate Report |
| `Ctrl+L` | Open Logs Explorer |
| `Ctrl+F` | Search Artifacts |
| `Ctrl+E` | Export System Data |
| `Ctrl+,` | Open Settings |
| `Ctrl+Shift+X` | Emergency Stop (with confirmation) |
| `F5` | Refresh All Data |
| `F11` | Toggle Fullscreen |
| `Ctrl+1-6` | Jump to Status Card (1=GLADIUS, 2=SENTINEL, etc.) |
| `Ctrl+Space` | Toggle Activity Feed |
| `Alt+Left/Right` | Navigate between pages |

### Navigation Shortcuts
| Shortcut | Action |
|----------|--------|
| `Tab` | Next interactive element |
| `Shift+Tab` | Previous interactive element |
| `Arrow Keys` | Navigate status grid |
| `Enter` | Activate focused element |
| `Escape` | Close modal/return to overview |

### Quick Action Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+Q` | Quick Health Check |
| `Ctrl+D` | System Diagnostics |
| `Ctrl+H` | Show/Hide Help Overlay |
| `Ctrl+N` | Open Notifications Panel |

---

## DATA REFRESH RATES

| Component | Refresh Rate | Method |
|-----------|--------------|--------|
| Status Cards | 2 seconds | WebSocket push |
| Real-time Metrics | 1 second | WebSocket push |
| Activity Feed | Real-time | WebSocket push |
| System Health | 10 minutes | Polling (+ on-demand) |
| Status Bar | 5 seconds | Polling |

---

## STATE MANAGEMENT

### Status Card States
```javascript
{
  id: "gladius" | "sentinel" | "legion" | "syndicate" | "automata" | "system",
  status: "active" | "idle" | "warning" | "error" | "offline",
  health: 0-6, // Number of filled status dots
  badge: "string", // Current state label
  metrics: {
    primary: { label: "string", value: "string" },
    secondary: { label: "string", value: "string" },
    tertiary: { label: "string", value: "string" }
  },
  action: {
    label: "string",
    route: "string",
    enabled: boolean
  }
}
```

### Metric State
```javascript
{
  name: "string",
  value: number,
  unit: "string",
  max: number,
  threshold: {
    warning: number,
    critical: number
  },
  format: "percentage" | "bytes" | "number" | "temperature"
}
```

### Activity Event State
```javascript
{
  id: "uuid",
  timestamp: "ISO-8601",
  type: "timer" | "success" | "info" | "warning" | "error" | "alert",
  message: "string",
  source: "string", // Component that generated event
  severity: 0-5,
  metadata: object // Additional context data
}
```

---

## RESPONSIVE BREAKPOINTS

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Desktop XL | ≥1920px | Full 3-column grid, expanded metrics |
| Desktop L | 1600-1919px | Standard layout as shown |
| Desktop M | 1200-1599px | Standard layout, condensed spacing |
| Tablet | 800-1199px | 2-column grid, stacked actions/feed |
| Mobile | <800px | 1-column grid, collapsible panels |

---

## ACCESSIBILITY FEATURES

- **Keyboard Navigation:** Full keyboard support for all interactions
- **Screen Reader:** ARIA labels on all interactive elements
- **High Contrast:** Respects system high-contrast mode
- **Focus Indicators:** Clear focus outlines on all focusable elements
- **Reduced Motion:** Respects prefers-reduced-motion
- **Font Scaling:** Supports browser zoom up to 200%

---

## ERROR STATES

### Connection Lost
```
╔══════════════════════════════════════╗
║  ⚠ CONNECTION LOST                  ║
║                                      ║
║  Unable to connect to GLADIUS server ║
║  Attempting to reconnect...          ║
║                                      ║
║  [Retry Now]  [Go Offline]          ║
╚══════════════════════════════════════╝
```

### Service Unavailable
- Individual status cards show "OFFLINE" badge
- Metrics display last known values with "(stale)" indicator
- Action buttons disabled with tooltip explaining why

### Critical System Failure
- Full-screen red overlay
- Emergency contact information
- Kill switch for immediate shutdown
- Diagnostic log dump option

---

## PERFORMANCE TARGETS

- **Initial Load:** < 1 second
- **Card Render:** < 100ms per card
- **Metric Update:** < 50ms latency
- **Activity Event:** < 20ms to UI
- **Memory Usage:** < 200MB for page
- **CPU Usage:** < 5% idle, < 15% active

---

## IMPLEMENTATION NOTES

### Technology Stack
- **Framework:** Electron + React
- **State Management:** Redux with WebSocket middleware
- **Charting:** Chart.js for metric bars
- **Styling:** CSS Modules with CSS Grid
- **WebSocket:** Socket.io for real-time updates

### Component Hierarchy
```
MissionOverview (Page)
├── HeaderBar
├── StatusGrid
│   ├── StatusCard (x6)
│   │   ├── StatusIcon
│   │   ├── StatusIndicator
│   │   ├── MetricDisplay (x3)
│   │   └── ActionButton
├── MetricsPanel
│   └── MetricBar (x6)
├── QuickActionsPanel
│   └── ActionButton (x10)
├── ActivityFeed
│   ├── ActivityEvent (x10)
│   └── ViewAllButton
├── SystemHealthPanel
│   └── HealthIndicator (x6)
└── StatusBar
```

### File Structure
```
src/pages/MissionOverview/
├── index.tsx              # Main page component
├── components/
│   ├── HeaderBar.tsx
│   ├── StatusCard.tsx
│   ├── MetricBar.tsx
│   ├── ActivityFeed.tsx
│   ├── QuickActions.tsx
│   └── SystemHealth.tsx
├── hooks/
│   ├── useSystemStatus.ts
│   ├── useMetrics.ts
│   └── useActivityFeed.ts
├── styles/
│   └── MissionOverview.module.css
└── types.ts
```

---

## TESTING REQUIREMENTS

### Unit Tests
- All components render without errors
- Status calculations are accurate
- Event formatting is correct
- Keyboard shortcuts trigger correct actions

### Integration Tests
- WebSocket connection handling
- Status updates propagate correctly
- Error states display appropriately
- Navigation between pages works

### E2E Tests
- Complete user workflows
- Performance under load
- Memory leak detection
- Accessibility compliance (WCAG 2.1 AA)

---

## FUTURE ENHANCEMENTS

1. **Customizable Grid:** Drag-and-drop card reordering with saved layouts
2. **Card Presets:** Predefined layouts for different roles (Admin, Developer, Analyst)
3. **Dark/Light Themes:** User-selectable theme with custom color schemes
4. **Export Dashboard:** Export current view as image or PDF
5. **Widget System:** Plugin architecture for custom status cards
6. **Multi-monitor:** Support for spanning dashboard across displays
7. **Mobile App:** Companion mobile app with push notifications
8. **Voice Commands:** Voice control for common actions
9. **AI Insights:** ML-powered anomaly detection and recommendations
10. **Historical Playback:** Time-travel debugging of system state

---

**Document Status:** ✓ Ready for Implementation  
**Last Updated:** 2024  
**Blueprint Version:** 1.0.0
