# PAGE 07: COMMAND PALETTE
## Global Quick Action & Navigation Overlay

**Version:** 1.0.0  
**Status:** Production Blueprint  
**Purpose:** Universal command interface for rapid navigation and action execution across the entire GLADIUS dashboard

---

## ASCII BLUEPRINT LAYOUT

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║                                                                                       ║
║                            [BACKGROUND PAGE DIMMED 80%]                               ║
║                                                                                       ║
║                                                                                       ║
║           ┌───────────────────────────────────────────────────────────┐              ║
║           │  ⌘ COMMAND PALETTE                               [ESC]    │              ║
║           ├───────────────────────────────────────────────────────────┤              ║
║           │                                                            │              ║
║           │  > train status_                                           │              ║
║           │  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │              ║
║           │                                                            │              ║
║           │  ┌────────────────────────────────────────────────────┐  │              ║
║           │  │  🎯 ACTIONS (8)                                    │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │  ▶ 🤖 View Training Status                Ctrl+T  │  │              ║
║           │  │    Open Training Console to view current status    │  │              ║
║           │  │                                                    │  │              ║
║           │  │    ⏸ Pause Training                       Ctrl+P  │  │              ║
║           │  │    Pause all training operations                   │  │              ║
║           │  │                                                    │  │              ║
║           │  │    ▶ Start Training                       Ctrl+T  │  │              ║
║           │  │    Begin model training process                    │  │              ║
║           │  │                                                    │  │              ║
║           │  │    📊 Training Report                     Ctrl+R  │  │              ║
║           │  │    Generate comprehensive training report          │  │              ║
║           │  │                                                    │  │              ║
║           │  │    💾 Save Training Checkpoint                     │  │              ║
║           │  │    Save current training state to checkpoint       │  │              ║
║           │  │                                                    │  │              ║
║           │  │    📈 View Training Metrics                        │  │              ║
║           │  │    Open detailed metrics dashboard                 │  │              ║
║           │  │                                                    │  │              ║
║           │  │    🔄 Restart Training Service                     │  │              ║
║           │  │    Restart the training service daemon             │  │              ║
║           │  │                                                    │  │              ║
║           │  │    ⚙ Configure Training Settings                  │  │              ║
║           │  │    Open training configuration panel               │  │              ║
║           │  │                                                    │  │              ║
║           │  ├────────────────────────────────────────────────────┤  │              ║
║           │  │  📍 NAVIGATION (12)                                │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │    🏠 Mission Overview                    Ctrl+1  │  │              ║
║           │  │    Go to main dashboard                            │  │              ║
║           │  │                                                    │  │              ║
║           │  │    🤖 Training Console                    Ctrl+2  │  │              ║
║           │  │    View live training status and controls          │  │              ║
║           │  │                                                    │  │              ║
║           │  │    👁 Sentinel Guard                     Ctrl+3  │  │              ║
║           │  │    Security monitoring and threat detection        │  │              ║
║           │  │                                                    │  │              ║
║           │  │    ⚔ LEGION Agents                       Ctrl+4  │  │              ║
║           │  │    Agent fleet management and coordination         │  │              ║
║           │  │                                                    │  │              ║
║           │  └────────────────────────────────────────────────────┘  │              ║
║           │                                                            │              ║
║           │  💡 TIP: Use arrow keys to navigate, Enter to select     │              ║
║           │  Type "?" for help with search syntax                     │              ║
║           │                                                            │              ║
║           └────────────────────────────────────────────────────────────┘              ║
║                                                                                       ║
║                                                                                       ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝


╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  ALTERNATE VIEW: HELP MODE (when user types "?")                                     ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║           ┌───────────────────────────────────────────────────────────┐              ║
║           │  ⌘ COMMAND PALETTE - HELP                        [ESC]    │              ║
║           ├───────────────────────────────────────────────────────────┤              ║
║           │                                                            │              ║
║           │  > ?_                                                      │              ║
║           │  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │              ║
║           │                                                            │              ║
║           │  ┌────────────────────────────────────────────────────┐  │              ║
║           │  │  📚 SEARCH SYNTAX                                  │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │                                                    │  │              ║
║           │  │  > command         Search all commands             │  │              ║
║           │  │  @ navigate        Navigate to pages               │  │              ║
║           │  │  # settings        Open settings                   │  │              ║
║           │  │  $ agent           Agent operations                │  │              ║
║           │  │  ! emergency       Emergency actions               │  │              ║
║           │  │  / search          Search logs and data            │  │              ║
║           │  │  : goto            Go to specific line/location    │  │              ║
║           │  │  * bookmark        Access bookmarks                │  │              ║
║           │  │  ?                 Show this help                  │  │              ║
║           │  │                                                    │  │              ║
║           │  ├────────────────────────────────────────────────────┤  │              ║
║           │  │  ⌨ KEYBOARD SHORTCUTS                              │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │                                                    │  │              ║
║           │  │  Ctrl+K / Cmd+K    Open Command Palette            │  │              ║
║           │  │  Escape            Close palette                   │  │              ║
║           │  │  ↑ ↓               Navigate results                │  │              ║
║           │  │  Enter             Execute selected command        │  │              ║
║           │  │  Ctrl+Enter        Execute in new window           │  │              ║
║           │  │  Tab               Auto-complete                   │  │              ║
║           │  │  Backspace         Clear one character             │  │              ║
║           │  │  Ctrl+Backspace    Clear entire search             │  │              ║
║           │  │  Ctrl+1-9          Quick navigate to result        │  │              ║
║           │  │                                                    │  │              ║
║           │  ├────────────────────────────────────────────────────┤  │              ║
║           │  │  🎨 CATEGORIES                                     │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │                                                    │  │              ║
║           │  │  Actions           Execute commands and operations │  │              ║
║           │  │  Navigation        Navigate between pages          │  │              ║
║           │  │  Settings          Adjust system settings          │  │              ║
║           │  │  Agents            Control LEGION agents           │  │              ║
║           │  │  Files             Open files and logs             │  │              ║
║           │  │  Bookmarks         Access saved locations          │  │              ║
║           │  │  Recent            Recently used commands          │  │              ║
║           │  │  Emergency         Critical system actions         │  │              ║
║           │  │                                                    │  │              ║
║           │  └────────────────────────────────────────────────────┘  │              ║
║           │                                                            │              ║
║           │  💡 Type any search prefix to see matching commands       │              ║
║           │                                                            │              ║
║           └────────────────────────────────────────────────────────────┘              ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝


╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  ALTERNATE VIEW: AGENT OPERATIONS (when user types "$")                              ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║           ┌───────────────────────────────────────────────────────────┐              ║
║           │  ⌘ COMMAND PALETTE - AGENT OPERATIONS           [ESC]    │              ║
║           ├───────────────────────────────────────────────────────────┤              ║
║           │                                                            │              ║
║           │  > $ alpha_                                                │              ║
║           │  ▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔▔  │              ║
║           │                                                            │              ║
║           │  ┌────────────────────────────────────────────────────┐  │              ║
║           │  │  ⚔ AGENTS MATCHING "ALPHA" (3)                     │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │  ▶ 🟢 AGENT-ALPHA                         [BUSY]   │  │              ║
║           │  │    Task: Research | CPU: 34% | RAM: 2.4GB          │  │              ║
║           │  │    Actions: [View] [Restart] [Stop] [Logs]         │  │              ║
║           │  │                                                    │  │              ║
║           │  ├────────────────────────────────────────────────────┤  │              ║
║           │  │  ⚔ AGENT QUICK ACTIONS                             │  │              ║
║           │  │  ──────────────────────────────────────────────────  │  │              ║
║           │  │    📊 View All Agents                              │  │              ║
║           │  │    Open LEGION agent management page               │  │              ║
║           │  │                                                    │  │              ║
║           │  │    + Deploy New Agent                              │  │              ║
║           │  │    Create and deploy a new agent                   │  │              ║
║           │  │                                                    │  │              ║
║           │  │    🔄 Restart All Agents                           │  │              ║
║           │  │    Restart all agents in fleet                     │  │              ║
║           │  │                                                    │  │              ║
║           │  │    ⏸ Pause All Agents                             │  │              ║
║           │  │    Temporarily pause all agent operations          │  │              ║
║           │  │                                                    │  │              ║
║           │  │    🎯 Assign Task to Agent                         │  │              ║
║           │  │    Manually assign task from queue                 │  │              ║
║           │  │                                                    │  │              ║
║           │  │    📈 Agent Performance Report                     │  │              ║
║           │  │    Generate fleet performance analysis             │  │              ║
║           │  │                                                    │  │              ║
║           │  └────────────────────────────────────────────────────┘  │              ║
║           │                                                            │              ║
║           │  💡 Type agent name to filter, or browse all actions      │              ║
║           │                                                            │              ║
║           └────────────────────────────────────────────────────────────┘              ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝
```

---

## COMPONENT SPECIFICATIONS

### 1. COMMAND PALETTE OVERLAY

**Dimensions:** 700px width x auto height (max 600px)  
**Position:** Center of screen, overlaying current page  
**Background:** Semi-transparent dark overlay (80% opacity) behind modal  

#### Modal Structure

**Header Bar:**
- **Title:** "⌘ COMMAND PALETTE" with command symbol
- **Close Button:** [ESC] indicator (not clickable, shows keyboard shortcut)
- **Height:** 40px
- **Background:** Dark header (#2d2d30)

**Search Input:**
- **Width:** Full width with padding
- **Height:** 50px
- **Font Size:** 18px
- **Placeholder:** "Type a command or search..."
- **Prefix Indicator:** "> " shows before cursor
- **Auto-focus:** Input automatically focused on open
- **Styling:**
  - Light background (#3c3c3c)
  - White text
  - Blinking cursor
  - Bottom border separator

**Results Container:**
- **Height:** Auto (up to 500px)
- **Scrollable:** If results exceed height
- **Padding:** 10px all sides

**Footer:**
- **Height:** 30px
- **Content:** Tips and hints
- **Font Size:** 12px
- **Color:** Muted gray
- **Examples:**
  - "💡 TIP: Use arrow keys to navigate, Enter to select"
  - "Type '?' for help with search syntax"
  - "Showing X of Y results"

---

### 2. SEARCH FUNCTIONALITY

#### Search Prefixes (Command Modifiers)

**Prefix System:**
Users can type special characters to filter by category:

| Prefix | Category | Example | Description |
|--------|----------|---------|-------------|
| `>` | All Commands | `> train` | Default, searches everything |
| `@` | Navigation | `@ training` | Navigate to pages only |
| `#` | Settings | `# theme` | System settings only |
| `$` | Agents | `$ alpha` | Agent operations only |
| `!` | Emergency | `! kill` | Critical actions only |
| `/` | Search | `/ error logs` | Search logs and data |
| `:` | Go To | `: line 100` | Jump to specific location |
| `*` | Bookmarks | `* checkpoint` | Saved bookmarks only |
| `?` | Help | `?` | Show help screen |

#### Search Algorithm

**Fuzzy Matching:**
- Matches partial strings
- Case-insensitive
- Supports typos (Levenshtein distance)
- Prioritizes:
  1. Exact matches
  2. Starts-with matches
  3. Contains matches
  4. Fuzzy matches

**Example:**
- Search: "tran stat"
- Matches: "Training Status", "View Training Statistics", "Translate Status"

**Scoring:**
- Exact match: 100 points
- Starts with: 90 points
- Word start: 80 points
- Contains: 70 points
- Fuzzy (1 char off): 60 points
- Fuzzy (2 chars off): 50 points

**Recent Commands:**
- Last 10 commands cached
- Boosted in search results
- Shown even without search input

---

### 3. RESULTS DISPLAY

#### Result Categories

Results grouped and displayed by category:

1. **🎯 ACTIONS** - Executable commands
2. **📍 NAVIGATION** - Page navigation
3. **⚙ SETTINGS** - Configuration options
4. **⚔ AGENTS** - Agent operations
5. **📄 FILES** - File and log access
6. **⭐ BOOKMARKS** - Saved locations
7. **🕐 RECENT** - Recently used
8. **🚨 EMERGENCY** - Critical actions

#### Result Item Structure

**Standard Result:**
```
▶ 🤖 View Training Status                Ctrl+T
  Open Training Console to view current status
```

**Components:**
- **Selection Indicator:** ▶ (shown on selected/hovered item)
- **Icon:** Emoji or icon representing action
- **Title:** Command name (bold, 14px)
- **Keyboard Shortcut:** Right-aligned (gray, 12px)
- **Description:** Brief description below (gray, 12px, italic)

**Agent Result (Special):**
```
▶ 🟢 AGENT-ALPHA                         [BUSY]
  Task: Research | CPU: 34% | RAM: 2.4GB
  Actions: [View] [Restart] [Stop] [Logs]
```

**Components:**
- Status indicator: 🟢 (green) / 🟡 (yellow) / 🔴 (red)
- Agent name
- Status badge: [BUSY] / [IDLE] / [FAILED]
- Live metrics in description
- Quick action buttons

#### Category Headers

**Format:**
```
📍 NAVIGATION (12)
──────────────────────────────────────────────────
```

**Styling:**
- Icon + category name + count
- Separator line below
- Collapsible (click to collapse/expand)
- Bold text
- Slightly larger font (15px)

#### Empty State

**When no results:**
```
┌────────────────────────────────────────────┐
│                                            │
│              🔍 No Results Found           │
│                                            │
│  Try different search terms or use         │
│  prefix modifiers (?, @, #, $, etc.)       │
│                                            │
│  [View All Commands]                       │
│                                            │
└────────────────────────────────────────────┘
```

---

### 4. COMMAND REGISTRY

#### Core Commands (100+ total)

**ACTIONS Category (30 commands):**
1. View Training Status
2. Pause Training
3. Start Training
4. Stop Training
5. Save Checkpoint
6. View Training Metrics
7. Generate Training Report
8. Restart Training Service
9. Configure Training Settings
10. Run Validation
11. Export Training Data
12. View TensorBoard
13. Adjust Hyperparameters
14. Force Checkpoint Save
15. Clear Training Cache
16. View Training History
17. Compare Training Runs
18. Start Sentinel Scan
19. View Security Report
20. Run Health Check
21. Sync Artifacts
22. Publish Package
23. Deploy Agent
24. Restart All Services
25. Backup System
26. Restore from Backup
27. Export System Data
28. Generate System Report
29. Clear All Caches
30. Refresh All Data

**NAVIGATION Category (10 commands):**
1. Mission Overview (Ctrl+1)
2. Training Console (Ctrl+2)
3. Sentinel Guard (Ctrl+3)
4. LEGION Agents (Ctrl+4)
5. Logs Explorer (Ctrl+L)
6. Artifact Operations (Ctrl+6)
7. Settings (Ctrl+,)
8. Help & Documentation (F1)
9. About GLADIUS
10. User Profile

**SETTINGS Category (20 commands):**
1. General Settings
2. Theme Settings
3. Display Settings
4. Notification Settings
5. Keyboard Shortcuts
6. User Preferences
7. Training Configuration
8. Security Settings
9. Agent Configuration
10. API Configuration
11. Database Settings
12. Cache Settings
13. Logging Settings
14. Performance Settings
15. Privacy Settings
16. Integration Settings
17. Backup Settings
18. Export Settings
19. Import Settings
20. Advanced Settings

**AGENTS Category (26 base + 6 fleet commands):**
- Individual commands for each of 26 agents (ALPHA-ZULU)
- View Agent Details
- Restart Agent
- Stop Agent
- View Agent Logs
- Assign Task to Agent
- View Agent Metrics
- Fleet Commands:
  1. View All Agents
  2. Deploy New Agent
  3. Restart All Agents
  4. Pause All Agents
  5. Agent Performance Report
  6. Configure Fleet

**EMERGENCY Category (8 commands):**
1. Emergency Kill Switch
2. Enable Lockdown Mode
3. System Restore
4. Escalate to Admin
5. Force Stop All Processes
6. Disconnect All Network
7. Emergency Backup
8. Activate Safe Mode

**FILES Category (Dynamic):**
- Recent Files (last 20)
- Log Files (all logs in tree)
- Config Files
- Data Files
- Checkpoint Files

**BOOKMARKS Category (Dynamic):**
- User-created bookmarks
- System bookmarks (key locations)

**RECENT Category (Dynamic):**
- Last 10 executed commands

---

### 5. INTERACTION PATTERNS

#### Opening Command Palette

**Methods:**
1. Press `Ctrl+K` (Windows/Linux) or `Cmd+K` (Mac)
2. Press `Ctrl+P` (alternate shortcut)
3. Click "Command Palette" in menu
4. Double-press `Shift` key (optional feature)

**Behavior:**
- Page content dims (80% opacity overlay)
- Modal appears with smooth animation (fade + scale)
- Search input auto-focused
- Can type immediately
- Recent commands pre-loaded

#### Navigation & Selection

**Keyboard Navigation:**
- `↑` - Previous result
- `↓` - Next result
- `Page Up` - Jump up 5 results
- `Page Down` - Jump down 5 results
- `Home` - First result
- `End` - Last result
- `Ctrl+1-9` - Quick select result 1-9
- `Enter` - Execute selected command
- `Ctrl+Enter` - Execute in new window/tab
- `Tab` - Auto-complete (if single match)
- `Escape` - Close palette

**Mouse Navigation:**
- Hover result to highlight
- Click result to execute
- Click outside modal to close
- Scroll results with mouse wheel

#### Executing Commands

**On Execute:**
1. Command palette closes (smooth fade out)
2. Command executes
3. Page navigates or action performs
4. Command added to recent history
5. Optional: Toast notification confirming action

**For Dangerous Actions:**
- Shows confirmation dialog
- Requires password/2FA
- Shows warning message
- User must confirm

---

### 6. SPECIAL MODES

#### Help Mode (?)

**Triggered by:** Typing `?` as first character

**Display:**
- Shows help screen instead of search results
- Organized sections:
  1. Search Syntax (all prefix modifiers)
  2. Keyboard Shortcuts
  3. Categories
  4. Tips & Tricks

**Interactions:**
- Can still navigate with arrow keys
- Enter on a syntax item shows examples
- Backspace returns to normal mode

#### Agent Mode ($)

**Triggered by:** Typing `$` as first character

**Display:**
- Shows all agents (if no filter)
- Shows filtered agents (if search term)
- Each agent shows live status
- Quick actions available per agent
- Agent quick actions at top

**Features:**
- Real-time agent status updates
- Click agent to open detailed view
- Quick action buttons inline
- Agent health indicators

#### Emergency Mode (!)

**Triggered by:** Typing `!` as first character

**Display:**
- Red-tinted modal background
- Shows only emergency commands
- Large warning icon
- "⚠ CRITICAL ACTIONS - USE WITH CAUTION" header
- Requires confirmation for all actions

**Security:**
- All actions require password
- Some require 2FA
- All actions logged in audit log
- Cooldown period between actions

#### Go To Mode (:)

**Triggered by:** Typing `:` as first character

**Usage:**
- `:100` - Go to line 100 (in current log/file)
- `:page 2` - Go to page 2
- `:agent alpha` - Go to agent ALPHA
- `:timestamp 14:30` - Go to timestamp in logs

---

### 7. CUSTOMIZATION & PERSISTENCE

#### User Preferences

**Customizable Settings:**
1. **Default Search Mode:** Start with specific prefix
2. **Result Count:** How many results to show (default: 50)
3. **Auto-complete:** Enable/disable Tab completion
4. **Fuzzy Matching:** Strictness level (loose, normal, strict)
5. **Recent Count:** How many recent commands to remember
6. **Animations:** Enable/disable modal animations
7. **Keyboard Shortcuts:** Customize all shortcuts
8. **Theme:** Command palette color scheme

#### Command History

**Storage:**
- Last 100 executed commands stored locally
- Timestamps recorded
- Execution count tracked
- Most-used commands prioritized

**Clearing History:**
- Manual clear option in settings
- Auto-clear after 30 days
- Privacy mode (don't track history)

#### Custom Commands

**User-Defined Commands:**
- Users can create custom commands
- Combines multiple actions
- Supports parameters
- Can share with team

**Example Custom Command:**
```
Name: Deploy to Production
Actions:
  1. Run validation
  2. Save checkpoint
  3. Publish packages
  4. Deploy agents
  5. Send notification
Shortcut: Ctrl+Shift+D
```

---

### 8. PERFORMANCE & OPTIMIZATION

**Performance Targets:**
- **Open Palette:** < 100ms
- **Search Latency:** < 50ms (as you type)
- **Result Render:** < 30ms for 100 results
- **Animation:** 60 FPS smooth
- **Memory:** < 50MB for palette
- **Command Execution:** < 200ms (navigation)

**Optimization Techniques:**
- Virtual scrolling for large result sets
- Debounced search (300ms)
- Cached command registry
- Lazy-load command descriptions
- Pre-render frequent commands
- Index commands for fast search

---

### 9. ACCESSIBILITY

**Keyboard-First Design:**
- Fully keyboard navigable
- No mouse required
- Clear focus indicators
- Logical tab order

**Screen Reader Support:**
- ARIA labels on all elements
- Results announced as you navigate
- Category headers announced
- Shortcut keys announced
- Action confirmations announced

**Visual Accessibility:**
- High contrast mode support
- Respects reduced motion
- Scalable fonts
- Clear focus states
- Color-blind safe (not just color)

---

### 10. ERROR HANDLING

**Command Execution Errors:**
- Shows error toast notification
- Logs error to console
- Suggests alternative commands
- Option to retry
- Option to report issue

**Search Errors:**
- Gracefully handles no results
- Suggests corrections
- Shows help if confused
- Never crashes

**Network Errors:**
- Shows offline indicator
- Caches available commands
- Can still navigate locally
- Auto-reconnect when online

---

## KEYBOARD SHORTCUTS REFERENCE

### Global Shortcuts
| Shortcut | Action |
|----------|--------|
| `Ctrl+K` / `Cmd+K` | Open Command Palette |
| `Ctrl+P` | Open Command Palette (alternate) |
| `Shift+Shift` | Open Command Palette (double-tap) |
| `Escape` | Close Command Palette |

### Within Palette
| Shortcut | Action |
|----------|--------|
| `↑` | Previous result |
| `↓` | Next result |
| `Page Up` | Jump up 5 results |
| `Page Down` | Jump down 5 results |
| `Home` | First result |
| `End` | Last result |
| `Ctrl+1-9` | Quick select result 1-9 |
| `Enter` | Execute selected command |
| `Ctrl+Enter` | Execute in new window |
| `Tab` | Auto-complete |
| `Backspace` | Delete character |
| `Ctrl+Backspace` | Clear entire search |

### Search Modifiers
| Shortcut | Action |
|----------|--------|
| `>` | All commands (default) |
| `@` | Navigation only |
| `#` | Settings only |
| `$` | Agents only |
| `!` | Emergency actions |
| `/` | Search logs/data |
| `:` | Go to location |
| `*` | Bookmarks |
| `?` | Help |

---

## STATE MANAGEMENT

### Command Palette State
```javascript
{
  isOpen: boolean,
  searchQuery: "string",
  selectedIndex: number,
  results: [
    {
      id: "string",
      category: "string",
      title: "string",
      description: "string",
      icon: "string",
      shortcut: "string",
      action: function,
      score: number // search relevance score
    }
  ],
  recentCommands: [
    {
      id: "string",
      timestamp: "ISO-8601",
      executionCount: number
    }
  ],
  mode: "normal" | "help" | "agent" | "emergency" | "goto",
  preferences: {
    resultCount: number,
    autoComplete: boolean,
    fuzzyStrength: "loose" | "normal" | "strict",
    animations: boolean
  }
}
```

---

## TESTING REQUIREMENTS

### Unit Tests
- Search algorithm accuracy
- Command execution logic
- Keyboard navigation
- Result filtering and sorting

### Integration Tests
- Command execution end-to-end
- Search across all command categories
- Prefix modifier functionality
- User preference persistence

### E2E Tests
- Complete user workflows
- Keyboard-only navigation
- Error handling scenarios
- Performance under load

---

## FUTURE ENHANCEMENTS

1. **Natural Language:** "Show me training logs from yesterday"
2. **Command Chaining:** Execute multiple commands in sequence
3. **Macros:** Record and replay command sequences
4. **Voice Commands:** Voice-activated command palette
5. **AI Suggestions:** ML-powered command recommendations
6. **Team Sharing:** Share custom commands with team
7. **Command Marketplace:** Download community commands
8. **Visual Builder:** Drag-and-drop command creator
9. **Analytics:** Track command usage patterns
10. **Mobile Version:** Touch-optimized command palette

---

**Document Status:** ✓ Ready for Implementation  
**Last Updated:** 2024  
**Blueprint Version:** 1.0.0
