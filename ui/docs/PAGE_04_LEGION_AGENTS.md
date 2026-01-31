# PAGE 04: LEGION AGENTS
## Distributed Agent Coordination & Task Management System

**Version:** 1.0.0  
**Status:** Production Blueprint  
**Purpose:** Real-time management and monitoring of distributed agent fleet

---

## ASCII BLUEPRINT LAYOUT

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  ⚔ LEGION COMMAND - Agent Fleet Management                [⚙] [←Back] [@user] [X]    ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║  ┌─ MESSAGE BUS STATUS ─────────────────────────────────────────────────────────────┐ ║
║  │                                                                                   │ ║
║  │  🔌 RabbitMQ Message Broker: 🟢 CONNECTED                                        │ ║
║  │  ────────────────────────────────────────────────────────────────────────────────  │ ║
║  │                                                                                   │ ║
║  │  Messages/sec: 147    Queue Depth: 1,247    Total Processed: 2,847,293          │ ║
║  │  Throughput:   ████████████████░░░░ 78%    Latency: 12ms avg (↓ 23%)            │ ║
║  │                                                                                   │ ║
║  │  ┌─ QUEUE BREAKDOWN ───────────────────────────────────────────────────────────┐│ ║
║  │  │                                                                              ││ ║
║  │  │  Queue Name          Messages  Consumers  Rate/s  Priority  Status         ││ ║
║  │  │  ──────────────────────────────────────────────────────────────────────────  ││ ║
║  │  │  high_priority              42        3      8.4    HIGH     ✓ DRAINING    ││ ║
║  │  │  normal_priority           847       12     64.2    NORMAL   ✓ FLOWING     ││ ║
║  │  │  low_priority              358        6     18.7    LOW      ✓ FLOWING     ││ ║
║  │  │  research_tasks             89        4     12.3    MEDIUM   ✓ FLOWING     ││ ║
║  │  │  data_processing           156        8     34.8    NORMAL   ✓ FLOWING     ││ ║
║  │  │  api_requests              455       10     58.2    HIGH     ✓ FLOWING     ││ ║
║  │  │  file_operations            78        3     14.6    LOW      ✓ FLOWING     ││ ║
║  │  │  database_sync             124        4     21.4    MEDIUM   ✓ FLOWING     ││ ║
║  │  │  ml_inference               98        5     19.8    HIGH     ✓ FLOWING     ││ ║
║  │  │                                                                              ││ ║
║  │  │  Total: 2,247 messages across 9 queues                                      ││ ║
║  │  │                                                                              ││ ║
║  │  └──────────────────────────────────────────────────────────────────────────────┘│ ║
║  │                                                                                   │ ║
║  │  Connection: amqp://localhost:5672 | Vhost: /gladius | User: legion_coordinator │ ║
║  │  Health: ✓ Healthy | Uptime: 72h 14m | Last Heartbeat: 2 seconds ago            │ ║
║  │                                                                                   │ ║
║  │  [↻ Refresh] [⚙ Configure] [📊 Metrics] [🔍 Inspect Queue] [⚡ Purge Queue]     │ ║
║  │                                                                                   │ ║
║  └───────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                       ║
║  ┌─ AGENT FLEET ─────────────────────────────────────────────────────────────────────┐║
║  │                                                                                   │║
║  │  Active: 26/26 | Idle: 8 | Busy: 18 | Failed: 0 | Total Tasks Today: 12,847    │║
║  │                                                                                   │║
║  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │║
║  │  │ ⚔ AGENT-ALPHA  │ │ ⚔ AGENT-BRAVO  │ │ ⚔ AGENT-CHARLIE│ │ ⚔ AGENT-DELTA  │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ 🟢 BUSY        │ │ 🟢 BUSY        │ │ 🟢 BUSY        │ │ ⚪ IDLE        │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ Task: Research │ │ Task: API Call │ │ Task: File Ops │ │ Task: None     │   │║
║  │  │ Progress: 67%  │ │ Progress: 23%  │ │ Progress: 89%  │ │ Tasks: 847     │   │║
║  │  │ ▓▓▓▓▓▓▓░░░░░░  │ │ ▓▓▓░░░░░░░░░░  │ │ ▓▓▓▓▓▓▓▓▓░░░░  │ │ Uptime: 72h    │   │║
║  │  │ ETA: 2m 34s    │ │ ETA: 8m 15s    │ │ ETA: 45s       │ │ CPU: 2.1%      │   │║
║  │  │ CPU: 34.2%     │ │ CPU: 18.7%     │ │ CPU: 12.4%     │ │ RAM: 124MB     │   │║
║  │  │ RAM: 2.4GB     │ │ RAM: 1.2GB     │ │ RAM: 847MB     │ │                │   │║
║  │  │ Health: ●●●●●● │ │ Health: ●●●●●● │ │ Health: ●●●●●○ │ │ Health: ●●●●●● │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ [Details]      │ │ [Details]      │ │ [Details]      │ │ [Details]      │   │║
║  │  └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘   │║
║  │                                                                                   │║
║  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │║
║  │  │ ⚔ AGENT-ECHO   │ │ ⚔ AGENT-FOX    │ │ ⚔ AGENT-GOLF   │ │ ⚔ AGENT-HOTEL  │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ 🟢 BUSY        │ │ 🟢 BUSY        │ │ ⚪ IDLE        │ │ 🟢 BUSY        │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ Task: DB Sync  │ │ Task: ML Inf.  │ │ Task: None     │ │ Task: Research │   │║
║  │  │ Progress: 45%  │ │ Progress: 91%  │ │ Tasks: 1,247   │ │ Progress: 12%  │   │║
║  │  │ ▓▓▓▓▓▓░░░░░░░  │ │ ▓▓▓▓▓▓▓▓▓▓▓░░  │ │ Uptime: 72h    │ │ ▓▓░░░░░░░░░░░  │   │║
║  │  │ ETA: 5m 12s    │ │ ETA: 38s       │ │ CPU: 1.2%      │ │ ETA: 12m 45s   │   │║
║  │  │ CPU: 23.8%     │ │ CPU: 78.4%     │ │ RAM: 98MB      │ │ CPU: 28.3%     │   │║
║  │  │ RAM: 1.8GB     │ │ RAM: 4.2GB     │ │                │ │ RAM: 2.1GB     │   │║
║  │  │ Health: ●●●●●● │ │ Health: ●●●●○○ │ │ Health: ●●●●●● │ │ Health: ●●●●●● │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ [Details]      │ │ [Details]      │ │ [Details]      │ │ [Details]      │   │║
║  │  └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘   │║
║  │                                                                                   │║
║  │  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐ ┌────────────────┐   │║
║  │  │ ⚔ AGENT-INDIA  │ │ ⚔ AGENT-JULIETT│ │ ⚔ AGENT-KILO   │ │ ⚔ AGENT-LIMA   │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ ⚪ IDLE        │ │ 🟢 BUSY        │ │ 🟢 BUSY        │ │ ⚪ IDLE        │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ Task: None     │ │ Task: Data Proc│ │ Task: API Call │ │ Task: None     │   │║
║  │  │ Tasks: 956     │ │ Progress: 34%  │ │ Progress: 56%  │ │ Tasks: 1,124   │   │║
║  │  │ Uptime: 72h    │ │ ▓▓▓▓░░░░░░░░░  │ │ ▓▓▓▓▓▓▓░░░░░░  │ │ Uptime: 72h    │   │║
║  │  │ CPU: 0.8%      │ │ ETA: 7m 23s    │ │ ETA: 4m 18s    │ │ CPU: 1.4%      │   │║
║  │  │ RAM: 87MB      │ │ CPU: 45.2%     │ │ CPU: 32.1%     │ │ RAM: 112MB     │   │║
║  │  │                │ │ RAM: 3.1GB     │ │ RAM: 2.7GB     │ │                │   │║
║  │  │ Health: ●●●●●● │ │ Health: ●●●●●○ │ │ Health: ●●●●●● │ │ Health: ●●●●●● │   │║
║  │  │                │ │                │ │                │ │                │   │║
║  │  │ [Details]      │ │ [Details]      │ │ [Details]      │ │ [Details]      │   │║
║  │  └────────────────┘ └────────────────┘ └────────────────┘ └────────────────┘   │║
║  │                                                                                   │║
║  │  [↓↓↓ Scroll for more agents (14 more) ↓↓↓]                                     │║
║  │                                                                                   │║
║  │  [+ Deploy Agent] [⚙ Configure Fleet] [📊 Performance Report] [🔄 Restart All]  │║
║  │                                                                                   │║
║  └───────────────────────────────────────────────────────────────────────────────────┘║
║                                                                                       ║
║  ┌─ PERFORMANCE METRICS ──────────────────────────────────────────────────────────┐  ║
║  │                                                                                 │  ║
║  │  Agent Performance Summary (Last 24 hours)                                      │  ║
║  │  ─────────────────────────────────────────────────────────────────────────────  │  ║
║  │                                                                                 │  ║
║  │  Agent         Tasks    Success  Failed  Avg Time  CPU Avg  RAM Peak  Score   │  ║
║  │  ─────────────────────────────────────────────────────────────────────────────  │  ║
║  │  ALPHA           847      845       2     2.4s      32.1%    2.8GB     ⭐⭐⭐⭐⭐  │  ║
║  │  BRAVO         1,247    1,245       2     1.8s      28.4%    1.4GB     ⭐⭐⭐⭐⭐  │  ║
║  │  CHARLIE         956      954       2     3.2s      18.7%    1.1GB     ⭐⭐⭐⭐⭐  │  ║
║  │  DELTA         1,124    1,122       2     2.1s      12.3%    847MB     ⭐⭐⭐⭐⭐  │  ║
║  │  ECHO          1,089    1,085       4     2.8s      34.2%    2.1GB     ⭐⭐⭐⭐   │  ║
║  │  FOX             784      782       2     4.2s      58.4%    4.8GB     ⭐⭐⭐⭐   │  ║
║  │  GOLF          1,247    1,247       0     1.2s       8.4%    512MB     ⭐⭐⭐⭐⭐  │  ║
║  │  HOTEL           689      686       3     3.4s      28.7%    2.4GB     ⭐⭐⭐⭐   │  ║
║  │  INDIA           956      956       0     1.9s       7.2%    432MB     ⭐⭐⭐⭐⭐  │  ║
║  │  JULIETT         847      843       4     2.7s      42.1%    3.4GB     ⭐⭐⭐⭐   │  ║
║  │  KILO          1,158    1,156       2     2.3s      28.9%    2.9GB     ⭐⭐⭐⭐⭐  │  ║
║  │  LIMA          1,124    1,124       0     1.4s       9.8%    687MB     ⭐⭐⭐⭐⭐  │  ║
║  │  MIKE            567      564       3     3.8s      32.4%    2.2GB     ⭐⭐⭐⭐   │  ║
║  │  NOVEMBER        892      890       2     2.6s      24.7%    1.8GB     ⭐⭐⭐⭐⭐  │  ║
║  │  OSCAR           734      732       2     2.9s      18.3%    1.5GB     ⭐⭐⭐⭐⭐  │  ║
║  │                                                                                 │  ║
║  │  Fleet Average: 948 tasks | 99.7% success rate | 2.4s avg time                 │  ║
║  │  Best Performer: GOLF (1,247 tasks, 0 failures) ⭐                              │  ║
║  │  Needs Attention: FOX (High CPU usage), JULIETT (4 failures)                   │  ║
║  │                                                                                 │  ║
║  │  [Export Report] [View Trends] [Configure Alerts] [Agent Comparison]           │  ║
║  │                                                                                 │  ║
║  └─────────────────────────────────────────────────────────────────────────────────┘  ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝

STATUS BAR: LEGION Active | Agents: 26/26 | Queue: 2,247 | Tasks/s: 47 | [F5] Refresh
```

---

## COMPONENT SPECIFICATIONS

### 1. HEADER BAR
**Location:** Top fixed position  
**Height:** 48px  

**Components:**
- **Title:** "⚔ LEGION COMMAND - Agent Fleet Management"
- **Settings [⚙]:** Fleet configuration panel
- **Back Button [←Back]:** Return to Mission Overview
- **User Menu [@user]:** User options
- **Close [X]:** Close window

---

### 2. MESSAGE BUS STATUS PANEL

**Dimensions:** Full width, 380px height  
**Position:** Top of page  

#### Header
**Display Components:**
- **Icon + Service:** "🔌 RabbitMQ Message Broker"
- **Status:** 🟢 CONNECTED | 🟡 DEGRADED | 🔴 DISCONNECTED | ⚫ OFFLINE
- **Connection String:** amqp://host:port
- **Vhost:** Virtual host name
- **User:** Connection username

#### Metrics Bar
**Real-time Metrics:**
- **Messages/sec:** Current message throughput rate
- **Queue Depth:** Total messages across all queues
- **Total Processed:** Lifetime message count
- **Throughput Bar:** Visual percentage bar (0-100%)
- **Latency:** Average message processing time with trend arrow (↓/↑/→)

#### Queue Breakdown Table
**Columns:**
1. **Queue Name** - Name of the message queue (20 chars)
2. **Messages** - Current message count in queue
3. **Consumers** - Number of active consumers
4. **Rate/s** - Messages processed per second
5. **Priority** - Queue priority (HIGH/MEDIUM/NORMAL/LOW)
6. **Status** - Queue health status

**Queue Types (9 default queues):**
1. **high_priority** - Urgent tasks requiring immediate processing
2. **normal_priority** - Standard task queue
3. **low_priority** - Background/maintenance tasks
4. **research_tasks** - Research and learning operations
5. **data_processing** - Data transformation and analysis
6. **api_requests** - External API calls and integrations
7. **file_operations** - File I/O operations
8. **database_sync** - Database operations and sync
9. **ml_inference** - Machine learning inference tasks

**Status Indicators:**
- ✓ DRAINING - Queue being actively processed, count decreasing
- ✓ FLOWING - Healthy flow, messages in/out balanced
- ⚠ BUILDING - Messages accumulating faster than processing
- ❌ STALLED - No processing activity
- ⏸ PAUSED - Queue manually paused

**Table Summary Footer:**
- Total messages across all queues
- Number of queues displayed

#### Connection Details
**Display:**
- Full connection string
- Virtual host
- Username
- Health status (✓ Healthy / ⚠ Degraded / ❌ Unhealthy)
- Uptime in hours
- Last heartbeat (relative time)

#### Action Buttons
1. **[↻ Refresh]** - Refresh queue statistics immediately
2. **[⚙ Configure]** - Configure message bus settings
3. **[📊 Metrics]** - Open detailed metrics dashboard
4. **[🔍 Inspect Queue]** - View messages in specific queue
5. **[⚡ Purge Queue]** - Clear messages from queue (with confirmation)

---

### 3. AGENT FLEET GRID

**Dimensions:** Full width, scrollable height (shows 12, total 26 agents)  
**Layout:** 4 columns x 7 rows (26 agents total)  

#### Fleet Summary Header
**Displays:**
- **Active:** Online agents / Total agents (e.g., 26/26)
- **Idle:** Count of idle agents
- **Busy:** Count of busy agents
- **Failed:** Count of failed/offline agents
- **Total Tasks Today:** Aggregate task count

#### Agent Card Specification

**Card Dimensions:** 180px x 180px  
**Spacing:** 15px gap  

**Card Layout:**
```
┌────────────────┐
│ ⚔ AGENT-NAME   │
│                │
│ 🟢 STATUS      │
│                │
│ Task: Type     │
│ Progress: NN%  │
│ ▓▓▓▓▓░░░░░░░░  │
│ ETA: Xm Xs     │
│ CPU: NN.N%     │
│ RAM: N.NGB     │
│ Health: ●●●●●● │
│                │
│ [Details]      │
└────────────────┘
```

**Card Components:**

1. **Header:** Agent name with icon (⚔)
   - NATO phonetic alphabet naming (ALPHA, BRAVO, CHARLIE, etc.)
   - 26 agents total (A-Z)

2. **Status Badge:** Color-coded status indicator
   - 🟢 BUSY - Actively processing task
   - ⚪ IDLE - Waiting for work
   - 🟡 STARTING - Initializing
   - 🔴 FAILED - Error state
   - ⚫ OFFLINE - Not connected

3. **Task Information:** (Only for BUSY agents)
   - **Task:** Type of current task (truncated at 15 chars)
   - **Progress:** Percentage complete (0-100%)
   - **Progress Bar:** Visual 12-segment bar
   - **ETA:** Estimated time remaining (Xm Xs format)

4. **Task Information:** (Only for IDLE agents)
   - **Task:** "None"
   - **Tasks:** Total tasks completed today
   - **Uptime:** Hours agent has been online

5. **Resource Usage:** (All agents)
   - **CPU:** CPU usage percentage (1 decimal)
   - **RAM:** Memory usage in MB or GB

6. **Health Indicator:** 6-dot visual health score
   - ●●●●●● (6 filled) - Perfect health
   - ●●●●●○ (5 filled) - Good
   - ●●●●○○ (4 filled) - Fair
   - ●●●○○○ (3 filled) - Warning
   - ●●○○○○ (2 filled) - Critical
   - ●○○○○○ (1 filled) - Emergency

7. **Action Button:** [Details] - Opens detailed agent view

**Card Interactions:**
- **Click Card:** Open detailed agent dashboard
- **Hover Card:** Show extended tooltip with more metrics
- **Right-Click Card:** Context menu
  - Restart agent
  - Pause agent
  - Assign task
  - View logs
  - Kill agent

**Card Color Coding:**
- **Green Border:** Healthy, operating normally
- **Yellow Border:** Warning state (high resource usage)
- **Red Border:** Critical state (errors, failures)
- **Gray Border:** Offline/disconnected

#### Scrolling
- Grid shows 12 agents at a time (3 rows)
- Scroll indicator shows "14 more" below
- Smooth scroll with mouse wheel or scrollbar
- Can use keyboard (Page Down/Up) to scroll

#### Fleet Action Buttons
1. **[+ Deploy Agent]** - Add new agent to fleet
2. **[⚙ Configure Fleet]** - Fleet-wide settings
3. **[📊 Performance Report]** - Generate performance report
4. **[🔄 Restart All]** - Restart all agents (with confirmation)

---

### 4. PERFORMANCE METRICS TABLE

**Dimensions:** Full width, 400px height  
**Position:** Bottom of page  

#### Header
**Title:** "Agent Performance Summary (Last 24 hours)"

#### Table Columns
1. **Agent** - Agent name (15 chars)
2. **Tasks** - Total tasks completed
3. **Success** - Successfully completed tasks
4. **Failed** - Failed tasks count
5. **Avg Time** - Average task completion time
6. **CPU Avg** - Average CPU usage percentage
7. **RAM Peak** - Peak memory usage
8. **Score** - Performance rating (1-5 stars: ⭐)

**Table Features:**
- **Sortable Columns:** Click header to sort
- **Default Sort:** By task count (descending)
- **Color Coding:**
  - Green row: Excellent performance (5 stars)
  - White row: Good performance (4 stars)
  - Yellow row: Fair performance (3 stars)
  - Red row: Poor performance (<3 stars)

**Scoring Algorithm:**
```
Score = (Success Rate × 0.4) + (Speed × 0.3) + (Resource Efficiency × 0.3)
- Success Rate: % of successful tasks
- Speed: Inverse of average time (faster = better)
- Resource Efficiency: Inverse of CPU/RAM usage
```

**Star Ratings:**
- ⭐⭐⭐⭐⭐ (5 stars): Score ≥ 90
- ⭐⭐⭐⭐ (4 stars): Score 75-89
- ⭐⭐⭐ (3 stars): Score 60-74
- ⭐⭐ (2 stars): Score 40-59
- ⭐ (1 star): Score < 40

#### Summary Footer
**Displays:**
- **Fleet Average:** Average tasks per agent
- **Success Rate:** Overall fleet success percentage
- **Avg Time:** Fleet-wide average completion time
- **Best Performer:** Agent with highest score
- **Needs Attention:** Agents requiring intervention

**Attention Triggers:**
- High CPU usage (>70% avg)
- High failure rate (>5%)
- Slow performance (>2x fleet avg time)
- High memory usage (>4GB peak)

#### Action Buttons
1. **[Export Report]** - Export table as CSV/PDF
2. **[View Trends]** - Open historical trend charts
3. **[Configure Alerts]** - Set performance alert thresholds
4. **[Agent Comparison]** - Side-by-side agent comparison

---

### 5. STATUS BAR

**Height:** 24px  
**Position:** Fixed bottom  

**Segments:**
1. **Status:** "LEGION Active"
2. **Agents:** "Agents: 26/26"
3. **Queue:** "Queue: 2,247"
4. **Tasks/s:** "Tasks/s: 47"
5. **Quick Action:** "[F5] Refresh"

---

## INTERACTION PATTERNS

### Agent Lifecycle Management

**Deploying New Agent:**
1. Click [+ Deploy Agent]
2. Modal opens with configuration form:
   - Agent name
   - Task types to handle
   - Resource limits (CPU/RAM)
   - Priority level
3. Click [Deploy] to create agent
4. Agent appears in grid with "STARTING" status
5. After initialization, status changes to "IDLE"

**Agent Task Assignment:**
- **Automatic:** Task queue system auto-assigns based on:
  - Agent availability (IDLE state)
  - Agent specialization (configured task types)
  - Queue priority
  - Agent performance history
- **Manual:** Right-click agent → "Assign Task" → Select from queue

**Agent Monitoring:**
- Real-time updates every 2 seconds
- Progress bars update smoothly
- Resource metrics update continuously
- Status changes trigger visual animation

**Agent Failure Handling:**
- When agent fails:
  1. Status changes to 🔴 FAILED
  2. Card border turns red
  3. Notification sent
  4. Current task re-queued
  5. Auto-restart attempted (3 attempts)
  6. After 3 failures, manual intervention required

### Message Queue Operations

**Queue Inspection:**
1. Click [🔍 Inspect Queue]
2. Select queue from dropdown
3. Modal shows:
   - First 100 messages in queue
   - Message content preview
   - Message priority
   - Time in queue
   - Target agent (if assigned)
4. Can delete, requeue, or reprioritize messages

**Queue Purging:**
1. Click [⚡ Purge Queue]
2. Select queue(s) to purge
3. Confirmation dialog shows:
   - Number of messages to be deleted
   - Queue names
   - Warning about data loss
4. Requires password confirmation
5. Messages permanently deleted
6. Audit log entry created

### Performance Analysis

**Viewing Trends:**
1. Click [View Trends]
2. Opens trend dashboard with charts:
   - Task completion over time (line chart)
   - Success rate trend (line chart)
   - CPU usage over time (area chart)
   - Memory usage over time (area chart)
   - Task type distribution (pie chart)
3. Configurable time range (1h, 6h, 24h, 7d, 30d)
4. Can export charts as images

**Agent Comparison:**
1. Click [Agent Comparison]
2. Select 2-4 agents to compare
3. Shows side-by-side comparison:
   - All metrics from performance table
   - Line charts of key metrics over time
   - Efficiency scores
   - Recommendations for optimization

### Fleet-wide Operations

**Restarting All Agents:**
1. Click [🔄 Restart All]
2. Confirmation dialog:
   - "This will restart all 26 agents"
   - "Active tasks will be re-queued"
   - "Estimated downtime: 30-60 seconds"
   - Requires password
3. Rolling restart (5 agents at a time)
4. Progress modal shows restart status
5. All agents back online within 60 seconds

---

## KEYBOARD SHORTCUTS

### Navigation & Refresh
| Shortcut | Action |
|----------|--------|
| `F5` | Refresh All Data |
| `Ctrl+R` | Refresh Agent Grid |
| `Ctrl+Shift+R` | Refresh Message Bus Status |
| `Ctrl+G` | Go to Agent (opens search) |
| `Alt+Left` | Back to Mission Overview |

### Agent Selection
| Shortcut | Action |
|----------|--------|
| `Arrow Keys` | Navigate between agent cards |
| `Enter` | Open selected agent details |
| `Space` | Toggle agent selection |
| `Ctrl+A` | Select all agents |
| `Ctrl+Click` | Multi-select agents |

### Agent Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+D` | Deploy new agent |
| `Ctrl+K` | Kill selected agent(s) |
| `Ctrl+P` | Pause selected agent(s) |
| `Ctrl+Shift+R` | Restart selected agent(s) |
| `Ctrl+L` | View logs for selected agent |
| `Ctrl+T` | Assign task to selected agent |

### Queue Operations
| Shortcut | Action |
|----------|--------|
| `Ctrl+I` | Inspect queue |
| `Ctrl+Shift+P` | Purge queue |
| `Ctrl+Q` | Quick queue stats |

### Performance & Reports
| Shortcut | Action |
|----------|--------|
| `Ctrl+E` | Export performance report |
| `Ctrl+Shift+T` | View trends |
| `Ctrl+Shift+C` | Agent comparison |
| `Ctrl+Shift+A` | Configure alerts |

### Quick Actions
| Shortcut | Action |
|----------|--------|
| `1-9` | Select queue by number |
| `Ctrl+1-9` | Jump to agent group (1=A-C, 2=D-F, etc.) |
| `Page Down/Up` | Scroll agent grid |

---

## DATA REFRESH RATES

| Component | Refresh Rate | Method |
|-----------|--------------|--------|
| Agent Cards | 2 seconds | WebSocket push |
| Message Bus Metrics | 1 second | WebSocket push |
| Queue Depth | 1 second | WebSocket push |
| Resource Metrics | 2 seconds | WebSocket push |
| Performance Table | 10 seconds | Polling |
| Task Progress | 500ms | WebSocket push |

---

## STATE MANAGEMENT

### Message Bus State
```javascript
{
  status: "connected" | "degraded" | "disconnected" | "offline",
  connection: {
    host: "string",
    port: number,
    vhost: "string",
    user: "string"
  },
  metrics: {
    messagesPerSecond: number,
    queueDepth: number,
    totalProcessed: number,
    throughput: number, // percentage
    latency: number // milliseconds
  },
  queues: [
    {
      name: "string",
      messages: number,
      consumers: number,
      rate: number, // messages/sec
      priority: "high" | "medium" | "normal" | "low",
      status: "draining" | "flowing" | "building" | "stalled" | "paused"
    }
  ],
  health: "healthy" | "degraded" | "unhealthy",
  uptime: number, // seconds
  lastHeartbeat: "ISO-8601"
}
```

### Agent State
```javascript
{
  id: "string",
  name: "string", // NATO phonetic
  status: "busy" | "idle" | "starting" | "failed" | "offline",
  currentTask: {
    type: "string",
    progress: number, // 0-100
    eta: number, // seconds remaining
    startTime: "ISO-8601"
  } | null,
  metrics: {
    tasksToday: number,
    cpu: number, // percentage
    ram: number, // bytes
    health: number // 0-6
  },
  uptime: number, // seconds
  performance: {
    totalTasks: number,
    successTasks: number,
    failedTasks: number,
    avgTime: number, // seconds
    avgCpu: number, // percentage
    peakRam: number, // bytes
    score: number // 0-100
  }
}
```

### Fleet State
```javascript
{
  totalAgents: number,
  activeAgents: number,
  idleAgents: number,
  busyAgents: number,
  failedAgents: number,
  totalTasksToday: number,
  agents: Agent[] // Array of agent states
}
```

---

## RESPONSIVE BREAKPOINTS

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Desktop XL | ≥1920px | 4-column agent grid |
| Desktop L | 1600-1919px | 4-column agent grid (standard) |
| Desktop M | 1200-1599px | 3-column agent grid |
| Tablet | 800-1199px | 2-column agent grid |
| Mobile | <800px | 1-column agent grid |

---

## ACCESSIBILITY FEATURES

- **Screen Reader:** Agent status changes announced
- **Keyboard Navigation:** Full keyboard control
- **High Contrast:** Clear status colors
- **Focus Indicators:** Visible focus on all cards
- **ARIA Labels:** Comprehensive labels on all elements
- **Reduced Motion:** Respects prefers-reduced-motion

---

## PERFORMANCE TARGETS

- **Agent Card Render:** < 50ms per card
- **Grid Update:** < 100ms for 26 agents
- **Message Bus Update:** < 50ms latency
- **Table Sort:** < 30ms for 1000 rows
- **Memory Usage:** < 500MB for page
- **CPU Usage:** < 12% when idle

---

## TESTING REQUIREMENTS

### Unit Tests
- Agent state calculations
- Performance scoring algorithm
- Queue status logic
- Resource usage formatting

### Integration Tests
- Agent deployment workflow
- Task assignment logic
- Queue operations
- Performance report generation

### E2E Tests
- Complete agent lifecycle
- Fleet-wide operations
- Queue management
- Performance analysis

---

## FUTURE ENHANCEMENTS

1. **Auto-scaling:** Automatically deploy/remove agents based on queue depth
2. **Agent Specialization:** Train agents for specific task types
3. **Load Balancing:** Advanced task distribution algorithms
4. **Predictive Scaling:** ML-based prediction of resource needs
5. **Agent Collaboration:** Agents working together on complex tasks
6. **Geographic Distribution:** Agents across multiple data centers
7. **Cost Optimization:** Track and optimize operational costs
8. **Advanced Analytics:** Deep performance analysis and recommendations
9. **Mobile App:** Manage fleet from mobile device
10. **Voice Commands:** Voice-activated fleet management

---

**Document Status:** ✓ Ready for Implementation  
**Last Updated:** 2024  
**Blueprint Version:** 1.0.0
