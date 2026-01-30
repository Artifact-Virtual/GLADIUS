# PAGE 05: LOGS EXPLORER
## Advanced Log Management & Real-Time Streaming Interface

**Version:** 1.0.0  
**Status:** Production Blueprint  
**Purpose:** Comprehensive log viewing, searching, and analysis across all GLADIUS systems

---

## ASCII BLUEPRINT LAYOUT

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  📁 LOGS EXPLORER - System Log Management                  [⚙] [←Back] [@user] [X]    ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║  ┌─ LOG FILE TREE ──────┐  ┌─ LIVE LOG STREAM ──────────────────────────────────────┐║
║  │                       │  │                                                         │║
║  │ 📁 logs/              │  │  [gladius-system.log] Auto-scroll: ON [⏸]              │║
║  │  ├─ 📁 gladius/       │  │  ────────────────────────────────────────────────────  │║
║  │  │  ├─ 📄 train.log   │  │                                                         │║
║  │  │  ├─ 📄 eval.log    │  │  2024-01-15 14:32:18.234 [INFO] Training epoch 47      │║
║  │  │  ├─ 📄 model.log   │  │  started with batch size 32                            │║
║  │  │  └─ 📄 export.log  │  │                                                         │║
║  │  ├─ 📁 sentinel/      │  │  2024-01-15 14:32:19.456 [DEBUG] Loading checkpoint    │║
║  │  │  ├─ 📄 watchdog    │  │  from: checkpoints/epoch_46_final.pt                   │║
║  │  │  ├─ 📄 learning    │  │                                                         │║
║  │  │  ├─ 📄 security    │  │  2024-01-15 14:32:20.789 [INFO] Checkpoint loaded      │║
║  │  │  └─ 📄 threats     │  │  successfully (2.4GB, 14B parameters)                  │║
║  │  ├─ 📁 legion/        │  │                                                         │║
║  │  │  ├─ 📄 coord.log   │  │  2024-01-15 14:32:21.012 [DEBUG] Initializing          │║
║  │  │  ├─ 📄 alpha.log   │  │  optimizer: AdamW (lr=1e-4, betas=[0.9, 0.999])        │║
║  │  │  ├─ 📄 bravo.log   │  │                                                         │║
║  │  │  ├─ 📄 charlie.log │  │  2024-01-15 14:32:22.345 [INFO] Starting forward pass  │║
║  │  │  └─ 📄 ... (22+)   │  │  on batch 1/12000                                      │║
║  │  ├─ 📁 syndicate/     │  │                                                         │║
║  │  │  ├─ 📄 market.log  │  │  2024-01-15 14:32:23.678 [DEBUG] Expert routing:       │║
║  │  │  ├─ 📄 research    │  │  E0=14% E1=13% E2=12% E3=13% E4=12% E5=13% E6=12% ...  │║
║  │  │  └─ 📄 api.log     │  │                                                         │║
║  │  ├─ 📁 automata/      │  │  2024-01-15 14:32:24.901 [INFO] Loss: 0.0234           │║
║  │  │  ├─ 📄 publish.log │  │  Expert losses: [0.021, 0.025, 0.023, 0.024, ...]     │║
║  │  │  ├─ 📄 sync.log    │  │                                                         │║
║  │  │  └─ 📄 deploy.log  │  │  2024-01-15 14:32:25.234 [WARN] Expert-4 load          │║
║  │  ├─ 📁 arty/          │  │  imbalance detected (8% utilization vs 12% avg)        │║
║  │  │  ├─ 📄 discord.log │  │                                                         │║
║  │  │  ├─ 📄 commands    │  │  2024-01-15 14:32:26.567 [INFO] Backward pass          │║
║  │  │  └─ 📄 events.log  │  │  completed. Gradient norm: 0.847                       │║
║  │  ├─ 📁 qwen/          │  │                                                         │║
║  │  │  ├─ 📄 api.log     │  │  2024-01-15 14:32:27.890 [DEBUG] Optimizer step        │║
║  │  │  ├─ 📄 inference   │  │  executed. Learning rate: 1.2e-5                       │║
║  │  │  └─ 📄 cache.log   │  │                                                         │║
║  │  ├─ 📁 database/      │  │  2024-01-15 14:32:28.123 [INFO] Batch 1 complete       │║
║  │  │  ├─ 📄 postgres    │  │  Time: 2.34s | Tokens/s: 2,847 | Memory: 142.3GB       │║
║  │  │  └─ 📄 redis.log   │  │                                                         │║
║  │  ├─ 📁 web/           │  │  2024-01-15 14:32:29.456 [INFO] Starting batch 2       │║
║  │  │  ├─ 📄 nginx.log   │  │                                                         │║
║  │  │  ├─ 📄 access.log  │  │  2024-01-15 14:32:30.789 [ERROR] CUDA out of memory    │║
║  │  │  └─ 📄 error.log   │  │  on GPU:0 during forward pass                          │║
║  │  └─ 📁 system/        │  │                                                         │║
║  │     ├─ 📄 syslog      │  │  2024-01-15 14:32:31.012 [ERROR] Attempting gradient   │║
║  │     ├─ 📄 auth.log    │  │  checkpointing to free memory                          │║
║  │     ├─ 📄 kernel.log  │  │                                                         │║
║  │     └─ 📄 hardware    │  │  2024-01-15 14:32:32.345 [INFO] Gradient checkpointing │║
║  │                       │  │  enabled. Memory usage: 138.7GB (-3.6GB)               │║
║  │  Logs: 247 files      │  │                                                         │║
║  │  Size: 45.2 GB        │  │  2024-01-15 14:32:33.678 [INFO] Resuming training      │║
║  │  Oldest: 30 days ago  │  │                                                         │║
║  │                       │  │  2024-01-15 14:32:34.901 [INFO] Batch 2 forward pass   │║
║  │  [⚙ Settings]        │  │  successful                                             │║
║  │  [🗑 Clean Old]       │  │                                                         │║
║  │  [📊 Analytics]       │  │  [█ More below ↓↓↓] Line 1,247,893 / 2,450,128 (51%)  │║
║  │  [📤 Export Tree]     │  │                                                         │║
║  │                       │  └─────────────────────────────────────────────────────────┘║
║  └───────────────────────┘                                                            ║
║                                                                                       ║
║  ┌─ SEARCH & FILTER ─────────────────────────────────────────────────────────────────┐║
║  │                                                                                   │║
║  │  Search: [ERROR|WARN                           ] [🔍 Search] [Clear]             │║
║  │                                                                                   │║
║  │  Filters:                                                                         │║
║  │  Log Level: [X] DEBUG  [X] INFO  [✓] WARN  [✓] ERROR  [X] FATAL                 │║
║  │  Date Range: [2024-01-15 00:00] to [2024-01-15 23:59]         [Today] [7 Days]  │║
║  │  Components: [✓] GLADIUS [✓] SENTINEL [✓] LEGION [✓] SYNDICATE [✓] AUTOMATA ... │║
║  │  Agents:     [All Selected ▼]                                                    │║
║  │                                                                                   │║
║  │  Advanced: [Regex Mode] [Case Sensitive] [Whole Word] [Invert Match]            │║
║  │                                                                                   │║
║  │  Results: 247 matches found | [Export Results] [Save Search] [Load Search]      │║
║  │                                                                                   │║
║  └───────────────────────────────────────────────────────────────────────────────────┘║
║                                                                                       ║
║  ┌─ BOOKMARKS & SAVED SEARCHES ──────────────────────────────────────────────────────┐║
║  │                                                                                   │║
║  │  ⭐ Bookmarks (5)                                      🔖 Saved Searches (3)      │║
║  │  ────────────────────────────────────────────────────────────────────────────────  │║
║  │                                                                                   │║
║  │  📌 CUDA OOM Error - Line 1,247,893                   🔎 Training Errors         │║
║  │     train.log @ 2024-01-15 14:32:30.789                  Query: "ERROR.*train"   │║
║  │     [Jump to] [Remove]                                    [Load] [Edit] [Delete] │║
║  │                                                                                   │║
║  │  📌 Expert Imbalance Warning                           🔎 Security Threats       │║
║  │     train.log @ 2024-01-15 14:32:25.234                  Query: "THREAT|BREACH"  │║
║  │     [Jump to] [Remove]                                    [Load] [Edit] [Delete] │║
║  │                                                                                   │║
║  │  📌 Checkpoint Save Success                            🔎 Agent Failures         │║
║  │     train.log @ 2024-01-15 14:25:18.456                  Query: "FAIL.*agent"    │║
║  │     [Jump to] [Remove]                                    [Load] [Edit] [Delete] │║
║  │                                                                                   │║
║  │  [+ Add Bookmark] [Manage All]                         [+ New Search]            │║
║  │                                                                                   │║
║  └───────────────────────────────────────────────────────────────────────────────────┘║
║                                                                                       ║
║  ┌─ LOG STATISTICS ───────────────────────────────────────────────────────────────┐  ║
║  │                                                                                 │  ║
║  │  Current Log: gladius-train.log | Size: 4.2 GB | Lines: 2,450,128              │  ║
║  │  Time Range: 2024-01-15 00:00:00 to 2024-01-15 14:32:34 (14.5 hours)           │  ║
║  │  ─────────────────────────────────────────────────────────────────────────────  │  ║
║  │                                                                                 │  ║
║  │  Log Level Distribution:                                                        │  ║
║  │  DEBUG: 1,245,892 (51%) ████████████████████████████░░░░░░░░░░░░░░░░░░░        │  ║
║  │  INFO:  1,124,847 (46%) █████████████████████████████░░░░░░░░░░░░░░░           │  ║
║  │  WARN:     78,142 (3%)  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │  ║
║  │  ERROR:     1,247 (<1%) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │  ║
║  │  FATAL:         0 (0%)  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░            │  ║
║  │                                                                                 │  ║
║  │  Top Error Messages:                                                            │  ║
║  │  1. CUDA out of memory (847 occurrences)                                        │  ║
║  │  2. Connection timeout (234 occurrences)                                        │  ║
║  │  3. Invalid checkpoint format (124 occurrences)                                 │  ║
║  │                                                                                 │  ║
║  │  Events per Hour: 168,975 avg | Peak: 247,892 @ 08:00 | Low: 89,234 @ 03:00    │  ║
║  │                                                                                 │  ║
║  │  [View Detailed Stats] [Generate Report] [Export Data]                          │  ║
║  │                                                                                 │  ║
║  └─────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝

STATUS BAR: Viewing gladius-train.log | Lines: 2.45M | Size: 4.2GB | [Ctrl+F] Search
```

---

## COMPONENT SPECIFICATIONS

### 1. HEADER BAR
**Location:** Top fixed position  
**Height:** 48px  

**Components:**
- **Title:** "📁 LOGS EXPLORER - System Log Management"
- **Settings [⚙]:** Log viewing preferences
- **Back Button [←Back]:** Return to Mission Overview
- **User Menu [@user]:** User options
- **Close [X]:** Close window

---

### 2. LOG FILE TREE PANEL

**Dimensions:** 300px width, full height (left sidebar)  
**Type:** Collapsible tree view  

#### Tree Structure
**Root Directory:** `/logs`

**Subdirectories (10 main categories):**
1. **gladius/** - Training and model logs
   - train.log - Training process logs
   - eval.log - Evaluation logs
   - model.log - Model architecture logs
   - export.log - Model export logs

2. **sentinel/** - Security and monitoring logs
   - watchdog.log - Process monitoring logs
   - learning.log - Learning daemon logs
   - security.log - Security scan logs
   - threats.log - Threat detection logs

3. **legion/** - Agent coordination logs
   - coordinator.log - Main coordinator logs
   - alpha.log through zulu.log - Individual agent logs (26 files)

4. **syndicate/** - Market research logs
   - market.log - Market data logs
   - research.log - Research task logs
   - api.log - API integration logs

5. **automata/** - Publishing automation logs
   - publish.log - Package publishing logs
   - sync.log - Repository sync logs
   - deploy.log - Deployment logs

6. **arty/** - Discord bot logs
   - discord.log - Main bot logs
   - commands.log - Command execution logs
   - events.log - Event handling logs

7. **qwen/** - Qwen API logs
   - api.log - API request/response logs
   - inference.log - Inference logs
   - cache.log - Cache operation logs

8. **database/** - Database logs
   - postgres.log - PostgreSQL logs
   - redis.log - Redis logs

9. **web/** - Web server logs
   - nginx.log - Nginx logs
   - access.log - HTTP access logs
   - error.log - HTTP error logs

10. **system/** - System-level logs
    - syslog - System logs
    - auth.log - Authentication logs
    - kernel.log - Kernel logs
    - hardware.log - Hardware monitoring logs

#### Tree Features
- **Expand/Collapse:** Click folder icon or arrow to toggle
- **File Count Badge:** Shows number of files in folder
- **File Size Indicator:** Color-coded by size
  - Green: < 100MB
  - Yellow: 100MB - 1GB
  - Red: > 1GB
- **Active File Highlight:** Currently viewed file highlighted in blue
- **Search Tree:** Quick search to find specific log files
- **Right-Click Menu:**
  - Open in new tab
  - Show file properties
  - Download file
  - Delete file (with confirmation)
  - Tail -f (follow mode)

#### Tree Footer
**Summary Statistics:**
- **Total Files:** Count of all log files
- **Total Size:** Aggregate size of all logs
- **Oldest Log:** Age of oldest log file

**Action Buttons:**
1. **[⚙ Settings]** - Configure log retention, rotation
2. **[🗑 Clean Old]** - Delete old logs (with date picker)
3. **[📊 Analytics]** - View aggregate log analytics
4. **[📤 Export Tree]** - Export tree structure

---

### 3. LIVE LOG STREAM PANEL

**Dimensions:** Flexible width (fills remaining space), 500px height  
**Position:** Top-right (main content area)  
**Type:** Terminal-style log viewer with syntax highlighting  

#### Header
**Components:**
- **Current File:** Displays active log filename in brackets
- **Auto-scroll Toggle:** ON/OFF switch with [⏸] pause icon
- **Line Counter:** Shows current line / total lines with percentage

#### Log Display Area
**Font:** Monospace (Fira Code or JetBrains Mono), 13px  
**Background:** Dark (#1e1e1e)  
**Text Colors:**
- Default: Light gray (#d4d4d4)
- Timestamp: Cyan (#569cd6)
- [DEBUG]: Gray (#808080)
- [INFO]: Blue (#4fc1ff)
- [WARN]: Yellow (#dcdcaa)
- [ERROR]: Red (#f48771)
- [FATAL]: Bright red + bold (#ff0000)

**Log Line Format:**
```
YYYY-MM-DD HH:MM:SS.mmm [LEVEL] Message text...
```

#### Features
1. **Syntax Highlighting:**
   - Timestamps colored cyan
   - Log levels color-coded
   - File paths in different color
   - Numbers highlighted
   - Strings in quotes highlighted

2. **Auto-scroll:**
   - Automatically scrolls to newest logs
   - Can be toggled on/off
   - Automatically pauses on manual scroll up
   - Resume button appears when paused

3. **Line Numbers:**
   - Optional line numbers in gutter
   - Can be toggled on/off
   - Click line number to bookmark

4. **Performance:**
   - Virtual scrolling for millions of lines
   - Only renders visible lines (viewport + buffer)
   - Smooth scrolling performance
   - Background loading for large files

5. **Interactions:**
   - **Click line:** Select line
   - **Double-click:** Select word
   - **Triple-click:** Select entire line
   - **Ctrl+Click:** Multi-select lines
   - **Right-click:** Context menu
     - Copy
     - Copy with timestamp
     - Bookmark line
     - Jump to previous/next error
     - Filter by this level
     - Search for this term

6. **Scroll Indicator:**
   - Shows current position in file (percentage)
   - Mini-map on right side (optional)
   - Error markers on scrollbar
   - Warning markers on scrollbar

#### Footer
**Status Display:**
- Line number: "Line 1,247,893 / 2,450,128"
- Percentage: "(51%)"
- Scroll indicator: "[█ More below ↓↓↓]"

---

### 4. SEARCH & FILTER PANEL

**Dimensions:** Full width, 180px height  
**Position:** Middle of page  

#### Search Bar
**Components:**
- **Search Input:** Text field with placeholder "Search logs..."
- **Search Button:** [🔍 Search] - Execute search
- **Clear Button:** [Clear] - Clear search and filters

**Search Features:**
- Plain text search
- Regex support (toggle)
- Case sensitive option
- Whole word matching
- Invert match (show non-matches)
- Search history (dropdown arrow)

#### Filter Controls

**Log Level Checkboxes:**
- [X] DEBUG - Show debug logs
- [X] INFO - Show info logs
- [✓] WARN - Show warnings (checked by default)
- [✓] ERROR - Show errors (checked by default)
- [X] FATAL - Show fatal errors

**Date Range Picker:**
- **Start Date/Time:** Date and time input
- **End Date/Time:** Date and time input
- **Quick Filters:**
  - [Today] - Last 24 hours
  - [7 Days] - Last week
  - [30 Days] - Last month
  - [Custom] - Custom range

**Component Filter:**
Checkboxes for each major component:
- [✓] GLADIUS
- [✓] SENTINEL
- [✓] LEGION
- [✓] SYNDICATE
- [✓] AUTOMATA
- [✓] ARTY
- [✓] QWEN
- [✓] DATABASE
- [✓] WEB
- [✓] SYSTEM

**Agent Filter:**
- Dropdown: [All Selected ▼]
- Can select specific agents (ALPHA, BRAVO, etc.)
- Multi-select with checkboxes

#### Advanced Options
**Toggle Buttons:**
- [Regex Mode] - Enable regex patterns
- [Case Sensitive] - Case-sensitive matching
- [Whole Word] - Match whole words only
- [Invert Match] - Show lines that DON'T match

#### Results Summary
**Display:**
- "Results: 247 matches found"
- Action buttons:
  - [Export Results] - Export matching lines
  - [Save Search] - Save search query for later
  - [Load Search] - Load saved search

---

### 5. BOOKMARKS & SAVED SEARCHES PANEL

**Dimensions:** Full width, 200px height  
**Position:** Below search panel  

#### Layout
**Two Columns:**
- Left: Bookmarks (50% width)
- Right: Saved Searches (50% width)

#### Bookmarks Section

**Header:** "⭐ Bookmarks (5)"

**Bookmark Card:**
```
📌 CUDA OOM Error - Line 1,247,893
   train.log @ 2024-01-15 14:32:30.789
   [Jump to] [Remove]
```

**Bookmark Properties:**
- **Icon:** 📌
- **Title:** Short description or log message excerpt
- **Line Number:** Exact line in file
- **File:** Log filename
- **Timestamp:** When bookmark was created
- **Actions:**
  - [Jump to] - Navigate to bookmarked line
  - [Remove] - Delete bookmark

**Features:**
- Can add bookmark via right-click menu
- Can add bookmark by clicking line number
- Automatically adds description from log line
- Can edit description
- Bookmarks persist across sessions
- Can export/import bookmarks

**Footer:**
- [+ Add Bookmark] - Add bookmark at current line
- [Manage All] - Open bookmark manager

#### Saved Searches Section

**Header:** "🔖 Saved Searches (3)"

**Saved Search Card:**
```
🔎 Training Errors
   Query: "ERROR.*train"
   [Load] [Edit] [Delete]
```

**Search Properties:**
- **Icon:** 🔎
- **Name:** User-defined search name
- **Query:** Search pattern/regex
- **Filters:** Saved filter settings (hidden, shown in edit)
- **Actions:**
  - [Load] - Load search and execute
  - [Edit] - Edit search parameters
  - [Delete] - Delete saved search

**Features:**
- Quick-load common searches
- Saves all filter settings
- Can organize into folders
- Can share searches (export/import)
- Search history automatic

**Footer:**
- [+ New Search] - Save current search

---

### 6. LOG STATISTICS PANEL

**Dimensions:** Full width, 280px height  
**Position:** Bottom of page  

#### Header
**File Summary:**
- Current log filename
- File size (human-readable)
- Line count
- Time range (first to last log entry)

#### Log Level Distribution

**Visual Bars:**
Shows breakdown of log levels with:
- Level name
- Count and percentage
- Visual progress bar (50 segments)
- Color coding matching log viewer

**Example:**
```
DEBUG: 1,245,892 (51%) ████████████████████████████░░░░░░░░░░░░░░░░░░░
INFO:  1,124,847 (46%) █████████████████████████████░░░░░░░░░░░░░░░
WARN:     78,142 (3%)  ███░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
ERROR:     1,247 (<1%) ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
FATAL:         0 (0%)  ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
```

#### Top Error Messages
**List Format:**
- Ranks error messages by frequency
- Shows top 3-5 most common errors
- Click error to search for all occurrences
- Shows occurrence count

**Example:**
```
1. CUDA out of memory (847 occurrences)
2. Connection timeout (234 occurrences)
3. Invalid checkpoint format (124 occurrences)
```

#### Activity Metrics
**Time-based Statistics:**
- **Events per Hour:** Average log entries per hour
- **Peak Hour:** Hour with most log activity + count
- **Low Hour:** Hour with least activity + count

#### Action Buttons
1. **[View Detailed Stats]** - Opens detailed analytics dashboard
2. **[Generate Report]** - Creates comprehensive log report
3. **[Export Data]** - Export statistics as CSV/JSON

---

### 7. STATUS BAR

**Height:** 24px  
**Position:** Fixed bottom  

**Segments:**
1. **Current File:** "Viewing gladius-train.log"
2. **Line Count:** "Lines: 2.45M"
3. **File Size:** "Size: 4.2GB"
4. **Quick Action:** "[Ctrl+F] Search"

---

## INTERACTION PATTERNS

### Opening Log Files

**From Tree:**
1. Click filename in tree
2. File loads in stream panel
3. Tree highlights active file
4. Statistics panel updates

**From Quick Search:**
1. Press Ctrl+O (or Cmd+O)
2. Quick search modal opens
3. Type filename to filter
4. Press Enter to open

### Searching Logs

**Quick Search:**
1. Press Ctrl+F
2. Search bar focuses
3. Type search term
4. Press Enter to search
5. Results highlight in viewer
6. Use F3/Shift+F3 to navigate results

**Advanced Search:**
1. Enter search term
2. Configure filters (level, date, component)
3. Click [🔍 Search]
4. Results displayed with count
5. Can export or save search

### Following Logs (Tail Mode)

**Enable Tail:**
1. Right-click log file → "Tail -f"
2. Auto-scroll enabled
3. Viewer jumps to end
4. New logs appear in real-time
5. Pause button available

**Behavior:**
- New lines highlighted briefly (fade animation)
- Stays at bottom unless manually scrolled
- Shows "Live" indicator in header
- Updates every 500ms

### Bookmarking

**Add Bookmark:**
1. Navigate to interesting line
2. Click line number OR right-click → "Bookmark"
3. Bookmark modal appears
4. Edit description if desired
5. Click [Save]
6. Bookmark appears in panel

**Use Bookmark:**
1. Click bookmark in panel
2. Viewer jumps to bookmarked line
3. Line highlighted for 2 seconds

### Exporting Logs

**Export Options:**
- **Visible Lines:** Export current view
- **Search Results:** Export matching lines
- **Entire File:** Export complete log
- **Date Range:** Export specific time period

**Export Formats:**
- Plain text (.txt)
- CSV (.csv) - structured format
- JSON (.json) - with metadata
- HTML (.html) - with syntax highlighting

### Multi-file Search

**Feature:**
- Can search across all log files
- Results grouped by file
- Click result to open file at that line
- Shows context (2 lines before/after)

---

## KEYBOARD SHORTCUTS

### Navigation
| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Quick open file |
| `Ctrl+W` | Close current file |
| `Ctrl+Tab` | Next open file |
| `Ctrl+Shift+Tab` | Previous open file |
| `Ctrl+G` | Go to line number |
| `Ctrl+End` | Jump to end of file |
| `Ctrl+Home` | Jump to start of file |
| `Page Up/Down` | Scroll by page |

### Search
| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Open search |
| `F3` | Find next |
| `Shift+F3` | Find previous |
| `Ctrl+H` | Find and replace |
| `Ctrl+Shift+F` | Multi-file search |
| `Escape` | Close search |

### Bookmarks
| Shortcut | Action |
|----------|--------|
| `Ctrl+B` | Add bookmark at current line |
| `F2` | Next bookmark |
| `Shift+F2` | Previous bookmark |
| `Ctrl+Shift+B` | Show all bookmarks |
| `Ctrl+K Ctrl+K` | Toggle bookmark (VSCode style) |

### View Controls
| Shortcut | Action |
|----------|--------|
| `Ctrl+L` | Toggle line numbers |
| `Ctrl+M` | Toggle minimap |
| `Ctrl+\\` | Toggle tree panel |
| `Ctrl+Shift+P` | Command palette |
| `F11` | Fullscreen |
| `Ctrl+Scroll` | Zoom in/out |

### Log Levels
| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Toggle DEBUG |
| `Ctrl+2` | Toggle INFO |
| `Ctrl+3` | Toggle WARN |
| `Ctrl+4` | Toggle ERROR |
| `Ctrl+5` | Toggle FATAL |
| `Ctrl+0` | Show all levels |

### Quick Actions
| Shortcut | Action |
|----------|--------|
| `Ctrl+R` | Refresh current file |
| `Ctrl+E` | Export visible content |
| `Ctrl+S` | Save search |
| `Ctrl+Shift+C` | Copy file path |
| `Ctrl+Shift+E` | Open in external editor |

---

## DATA REFRESH RATES

| Component | Refresh Rate | Method |
|-----------|--------------|--------|
| Live Log Stream (Tail mode) | 500ms | WebSocket push |
| File Tree | 5 seconds | Polling |
| Statistics Panel | 10 seconds | Polling |
| Search Results | On-demand | Event-driven |
| File Size Updates | 30 seconds | Polling |

---

## STATE MANAGEMENT

### Log Viewer State
```javascript
{
  currentFile: {
    path: "string",
    name: "string",
    size: number, // bytes
    lines: number,
    dateRange: {
      start: "ISO-8601",
      end: "ISO-8601"
    }
  },
  viewState: {
    scrollPosition: number,
    selectedLines: number[],
    autoScroll: boolean,
    tailMode: boolean,
    lineNumbers: boolean,
    minimap: boolean
  },
  search: {
    query: "string",
    regex: boolean,
    caseSensitive: boolean,
    wholeWord: boolean,
    invertMatch: boolean,
    results: number,
    currentMatch: number
  },
  filters: {
    levels: string[], // ["DEBUG", "INFO", etc.]
    dateRange: {
      start: "ISO-8601",
      end: "ISO-8601"
    },
    components: string[],
    agents: string[]
  },
  bookmarks: [
    {
      id: "string",
      line: number,
      file: "string",
      timestamp: "ISO-8601",
      description: "string"
    }
  ],
  savedSearches: [
    {
      id: "string",
      name: "string",
      query: "string",
      filters: object
    }
  ]
}
```

---

## ACCESSIBILITY FEATURES

- **Screen Reader:** Log level announcements
- **Keyboard Navigation:** Full keyboard control
- **High Contrast:** Readable syntax highlighting
- **Font Scaling:** Supports zoom up to 200%
- **Focus Indicators:** Clear focus states
- **ARIA Labels:** Comprehensive labels

---

## PERFORMANCE TARGETS

- **File Open:** < 500ms for files up to 1GB
- **Search:** < 1 second per 100MB file
- **Scroll Performance:** 60 FPS smooth scrolling
- **Memory Usage:** < 800MB for large files (virtual scrolling)
- **Tail Mode Latency:** < 50ms for new log lines
- **Multi-file Search:** < 5 seconds for 10GB of logs

---

## TESTING REQUIREMENTS

### Unit Tests
- Log parsing and formatting
- Search pattern matching
- Filter logic
- Bookmark management

### Integration Tests
- File loading and streaming
- Real-time log updates
- Search across files
- Export functionality

### E2E Tests
- Complete user workflows
- Performance with large files
- Concurrent file viewing
- Search and filter combinations

---

## FUTURE ENHANCEMENTS

1. **Log Analysis AI:** ML-powered error pattern detection
2. **Real-time Alerts:** Configurable alerts for specific log patterns
3. **Log Correlation:** Link related logs across files
4. **Visualization:** Charts and graphs from log data
5. **Log Replay:** Time-travel debugging through logs
6. **Collaborative Features:** Share bookmarks and searches with team
7. **Integration with Monitoring:** Link logs to metrics/traces
8. **Natural Language Search:** "Show me errors in the last hour"
9. **Log Compression:** On-the-fly decompression of archived logs
10. **Mobile App:** View logs on mobile devices

---

**Document Status:** ✓ Ready for Implementation  
**Last Updated:** 2024  
**Blueprint Version:** 1.0.0
