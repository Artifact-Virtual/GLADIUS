# PAGE 02: TRAINING CONSOLE
## Real-Time Model Training Monitoring & Control Interface

**Version:** 1.0.0  
**Status:** Production Blueprint  
**Purpose:** Live monitoring and control of GLADIUS model training operations

---

## ASCII BLUEPRINT LAYOUT

```
╔═══════════════════════════════════════════════════════════════════════════════════════╗
║  🤖 GLADIUS TRAINING CONSOLE                        [⏸] [⏹] [⚙] [←Back] [@user] [X] ║
╠═══════════════════════════════════════════════════════════════════════════════════════╣
║                                                                                       ║
║  ┌─ LIVE TRAINING STREAM ──────────────────────────────────────────────────────────┐ ║
║  │                                                                                  │ ║
║  │  [gladius@training-server ~]$ python train.py --config qwen_moe.yaml           │ ║
║  │                                                                                  │ ║
║  │  Initializing GLADIUS Training Pipeline v2.0                                    │ ║
║  │  ════════════════════════════════════════════════════════════════════            │ ║
║  │  ✓ Config loaded: qwen_moe.yaml                                                 │ ║
║  │  ✓ Dataset: /data/synthetic_conversations (847,293 examples)                   │ ║
║  │  ✓ Model: Qwen2.5-14B-Instruct-MoE (14B params, 8 experts)                     │ ║
║  │  ✓ Tokenizer: Qwen2Tokenizer (vocab_size=151,643)                              │ ║
║  │  ✓ Device: 2x NVIDIA A100-80GB (160GB total VRAM)                              │ ║
║  │                                                                                  │ ║
║  │  Starting training: Epoch 47/100, Batch 8450/12000                              │ ║
║  │  ────────────────────────────────────────────────────────────────────           │ ║
║  │                                                                                  │ ║
║  │  Epoch 47 | Batch 8450 | Loss: 0.0234 | Expert-0: 0.021 | Expert-1: 0.025     │ ║
║  │  Throughput: 2,847 tokens/sec | Memory: 142.3GB/160GB | Temp: 67°C/73°C       │ ║
║  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░ 70.4% complete      │ ║
║  │                                                                                  │ ║
║  │  [INFO] Expert routing distribution: E0:14% E1:13% E2:12% E3:13% E4:12% ...    │ ║
║  │  [INFO] Learning rate: 1.2e-5 (cosine schedule)                                │ ║
║  │  [WARN] Expert-4 load imbalance detected (8% utilization)                      │ ║
║  │  [INFO] Gradient accumulation: 4 steps                                         │ ║
║  │  [INFO] Checkpoint saved: checkpoints/epoch_47_batch_8450.pt                   │ ║
║  │                                                                                  │ ║
║  │  Epoch 47 | Batch 8451 | Loss: 0.0231 | Expert-0: 0.020 | Expert-1: 0.024     │ ║
║  │  Throughput: 2,852 tokens/sec | Memory: 142.5GB/160GB | Temp: 67°C/73°C       │ ║
║  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░ 70.5% complete      │ ║
║  │                                                                                  │ ║
║  │  Epoch 47 | Batch 8452 | Loss: 0.0229 | Expert-0: 0.019 | Expert-1: 0.023     │ ║
║  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░ 70.6% complete      │ ║
║  │                                                                                  │ ║
║  │  [█ Auto-scroll: ON] [↓↓↓ more below ↓↓↓]                                      │ ║
║  └──────────────────────────────────────────────────────────────────────────────────┘ ║
║                                                                                       ║
║  ┌─ TRAINING METRICS ────────────────────────────────────────────────────────────┐   ║
║  │                                                                                │   ║
║  │  ┌──── LOSS CURVE ────────┐  ┌──── EXPERT COVERAGE ─────┐                    │   ║
║  │  │                         │  │                           │                    │   ║
║  │  │  0.15├                  │  │  100%┤    ┌──┬──┬──┬──┐  │                    │   ║
║  │  │      │                  │  │      │  ┌─┤  │  │  │  │  │                    │   ║
║  │  │  0.10├     ╲            │  │   75%├──┤ │  │  │  │  │  │                    │   ║
║  │  │      │      ╲           │  │      │  │ │  │  │  │  │  │                    │   ║
║  │  │  0.05├       ╲____      │  │   50%├  │ │  │  │  │  │  │                    │   ║
║  │  │      │            ╲___  │  │      │  │ │  │  │  │  │  │                    │   ║
║  │  │  0.00├────────────────┬ │  │   25%├  │ │  │  │  │  │  │                    │   ║
║  │  │      0    25    50   100│  │      │  │ │  │  │  │  │  │                    │   ║
║  │  │         Epoch          │  │    0%└──┴─┴──┴──┴──┴──┴─ │                    │   ║
║  │  │                         │  │      E0 E1 E2 E3 E4 E5 E6│                    │   ║
║  │  │  Current: 0.0234        │  │                           │                    │   ║
║  │  │  Best: 0.0187 (E42)     │  │  Avg Coverage: 89.3%      │                    │   ║
║  │  │  Delta: -0.0003         │  │  Imbalance: 6.2%          │                    │   ║
║  │  └─────────────────────────┘  └───────────────────────────┘                    │   ║
║  │                                                                                │   ║
║  │  ┌──── THROUGHPUT ─────────┐  ┌──── MEMORY USAGE ────────┐                   │   ║
║  │  │                          │  │                           │                   │   ║
║  │  │  3k├─╮ ╭──╮╭──╮         │  │  160├──────────────┬──────┤                   │   ║
║  │  │    │ │ │  ││  │         │  │     │              │      │                   │   ║
║  │  │  2k├─╰─╯  ╰╯  ╰─╮       │  │  120├          ┌───┼───┐  │                   │   ║
║  │  │    │            │       │  │     │      ┌───┤   │   │  │                   │   ║
║  │  │  1k├            ╰─╮     │  │   80├──────┤   │   │   │  │                   │   ║
║  │  │    │              │     │  │     │      │   │   │   │  │                   │   ║
║  │  │   0├──────────────┴────┬│  │   40├      │   │   │   │  │                   │   ║
║  │  │    0m   1m   2m   3m  4m│  │     │      │   │   │   │  │                   │   ║
║  │  │      Time Window        │  │    0└──────┴───┴───┴───┴──┤                   │   ║
║  │  │                          │  │     GPU0 GPU1 CPU RAM SWP│                   │   ║
║  │  │  Current: 2,847 tok/s   │  │                           │                   │   ║
║  │  │  Average: 2,781 tok/s   │  │  GPU: 142.3GB / 160GB     │                   │   ║
║  │  │  Peak: 3,024 tok/s      │  │  System: 78% utilized     │                   │   ║
║  │  └──────────────────────────┘  └───────────────────────────┘                   │   ║
║  │                                                                                │   ║
║  └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
║  ┌─ TRAINING CONTROLS ────────────────────┐  ┌─ PROGRESS OVERVIEW ──────────────┐   ║
║  │                                         │  │                                   │   ║
║  │  Status: ⚡ TRAINING                    │  │  Overall Progress: 70.4%          │   ║
║  │  Mode: DISTRIBUTED (2x GPU)            │  │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░               │   ║
║  │                                         │  │                                   │   ║
║  │  ┌────────────────────────────────────┐│  │  Epoch: 47/100 (47%)              │   ║
║  │  │ [⏸ PAUSE TRAINING]                ││  │  Batch: 8,452/12,000 (70.4%)      │   ║
║  │  └────────────────────────────────────┘│  │                                   │   ║
║  │  ┌────────────────────────────────────┐│  │  Time Elapsed: 147h 23m           │   ║
║  │  │ [⏹ STOP TRAINING]                 ││  │  Time Remaining: ~4.2 hours       │   ║
║  │  └────────────────────────────────────┘│  │  ETA: Today at 18:45              │   ║
║  │  ┌────────────────────────────────────┐│  │                                   │   ║
║  │  │ [💾 SAVE CHECKPOINT]              ││  │  Checkpoints: 47 saved            │   ║
║  │  └────────────────────────────────────┘│  │  Last Save: 2 minutes ago         │   ║
║  │  ┌────────────────────────────────────┐│  │  Next Save: in 8 minutes          │   ║
║  │  │ [🔄 RELOAD CONFIG]                ││  │                                   │   ║
║  │  └────────────────────────────────────┘│  │  Total Samples: 847,293           │   ║
║  │  ┌────────────────────────────────────┐│  │  Samples Processed: 596,524       │   ║
║  │  │ [📊 EXPORT METRICS]               ││  │  Samples Remaining: 250,769       │   ║
║  │  └────────────────────────────────────┘│  │                                   │   ║
║  │  ┌────────────────────────────────────┐│  │  Validation Accuracy: 94.7%       │   ║
║  │  │ [🔧 ADJUST HYPERPARAMS]           ││  │  Test Accuracy: 93.2%             │   ║
║  │  └────────────────────────────────────┘│  │  Best Accuracy: 94.9% (E42)       │   ║
║  │  ┌────────────────────────────────────┐│  │                                   │   ║
║  │  │ [🎯 RUN VALIDATION]               ││  │  GPU Temperature: 67°C / 73°C     │   ║
║  │  └────────────────────────────────────┘│  │  Status: ✓ Within limits          │   ║
║  │  ┌────────────────────────────────────┐│  │                                   │   ║
║  │  │ [📈 VIEW TENSORBOARD]             ││  │  Learning Rate: 1.2e-5            │   ║
║  │  └────────────────────────────────────┘│  │  Gradient Norm: 0.847             │   ║
║  │                                         │  │  Weight Decay: 0.01               │   ║
║  │  Quick Actions:                         │  │                                   │   ║
║  │  [F2] Pause  [F3] Stop  [F5] Save      │  └───────────────────────────────────┘   ║
║  │  [F8] Validate  [F9] TensorBoard        │                                          ║
║  │                                         │                                          ║
║  └─────────────────────────────────────────┘                                          ║
║                                                                                       ║
║  ┌─ CONFIGURATION SNAPSHOT ──────────────────────────────────────────────────────┐   ║
║  │                                                                                │   ║
║  │  Config File: qwen_moe.yaml                        Last Modified: 3 days ago   │   ║
║  │  ────────────────────────────────────────────────────────────────────────────  │   ║
║  │  Model: Qwen2.5-14B-Instruct-MoE    Experts: 8    Active per token: 2         │   ║
║  │  Batch Size: 32 (per GPU)            Gradient Accum: 4    Effective: 256      │   ║
║  │  Learning Rate: 1e-4 (start)         Schedule: Cosine    Warmup: 500 steps    │   ║
║  │  Optimizer: AdamW                    Beta1: 0.9    Beta2: 0.999    Eps: 1e-8  │   ║
║  │  Max Length: 2048 tokens             Precision: Mixed FP16    Seed: 42        │   ║
║  │  Checkpoint: Every 10 minutes        Validation: Every 1000 steps              │   ║
║  │                                                                                │   ║
║  │  [Edit Config] [View Full Config] [Load Preset] [Save as Template]            │   ║
║  └────────────────────────────────────────────────────────────────────────────────┘   ║
║                                                                                       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝

STATUS BAR: Training Active | Epoch 47/100 | Loss: 0.0234 | GPU: 67°C | [F2] Pause
```

---

## COMPONENT SPECIFICATIONS

### 1. HEADER BAR
**Location:** Top fixed position  
**Height:** 48px  

**Components:**
- **Title:** "🤖 GLADIUS TRAINING CONSOLE" - Bold with emoji icon
- **Pause Button [⏸]:** Pause training (shortcut: F2)
- **Stop Button [⏹]:** Stop training with confirmation (shortcut: F3)
- **Settings [⚙]:** Open training settings overlay
- **Back Button [←Back]:** Return to Mission Overview
- **User Menu [@user]:** Quick user options
- **Close [X]:** Close window/return to overview

**State Indicators:**
- Pause button becomes Resume [▶] when paused
- Stop button disabled when not training
- Buttons show tooltips with keyboard shortcuts

---

### 2. LIVE TRAINING STREAM TERMINAL

**Dimensions:** Full width, 320px height  
**Type:** Terminal emulator with auto-scroll  
**Font:** Monospace (Fira Code or JetBrains Mono)  
**Background:** Dark terminal theme (#1e1e1e)  
**Text:** Light gray (#d4d4d4) with ANSI color support

**Features:**
- **Real-time Output:** Streams training logs in real-time
- **Auto-scroll:** Automatically scrolls to latest output (toggle available)
- **Search:** Ctrl+F to search within terminal output
- **Copy:** Right-click or Ctrl+C to copy selected text
- **Clear:** Button to clear terminal (preserves log file)
- **Export:** Save terminal output to file
- **Syntax Highlighting:** Color-coded log levels:
  - `[INFO]` - Blue
  - `[WARN]` - Yellow
  - `[ERROR]` - Red
  - `[SUCCESS]` - Green

**Log Format:**
```
Epoch {n} | Batch {n} | Loss: {float} | Expert-{n}: {float} ...
Throughput: {n} tokens/sec | Memory: {used}/{total}GB | Temp: {n}°C/{n}°C
[LEVEL] Message text...
```

**Interactions:**
- Click auto-scroll toggle to enable/disable
- Scroll up manually to pause auto-scroll
- Double-click any line to highlight/bookmark
- Right-click for context menu (Copy, Export, Find)

---

### 3. TRAINING METRICS PANEL (4 Charts)

**Dimensions:** Full width, 350px height  
**Layout:** 2x2 grid  

#### Chart A: LOSS CURVE (Top-Left)
**Type:** Line chart with trend line  
**X-Axis:** Epochs (0-100)  
**Y-Axis:** Loss value (0.00-0.15)  

**Data Display:**
- Current loss value (large text, 4 decimal places)
- Best loss achieved (with epoch number)
- Delta from previous epoch (± format)
- Moving average trend line (dotted)
- Validation loss overlay (optional, different color)

**Interactions:**
- Hover over line to see exact value
- Click point to jump to that epoch's logs
- Right-click for export options
- Zoom: Scroll wheel to zoom X-axis

#### Chart B: EXPERT COVERAGE (Top-Right)
**Type:** Bar chart with 8 bars (one per expert)  
**X-Axis:** Expert IDs (E0-E7)  
**Y-Axis:** Utilization percentage (0-100%)  

**Data Display:**
- Average coverage percentage across all experts
- Imbalance score (std deviation)
- Bar colors indicate health:
  - Green: 80-100% (optimal)
  - Yellow: 60-79% (acceptable)
  - Red: <60% (underutilized)

**Interactions:**
- Hover bar to see detailed expert stats
- Click bar to view expert-specific training data
- Right-click for expert analysis tools

#### Chart C: THROUGHPUT (Bottom-Left)
**Type:** Real-time line chart with 4-minute window  
**X-Axis:** Time (0-4 minutes, rolling)  
**Y-Axis:** Tokens per second (0-3000)  

**Data Display:**
- Current throughput (large text)
- Average throughput over window
- Peak throughput achieved
- Color-coded line (green=good, yellow=slow, red=stalled)

**Auto-update:** Every 1 second  
**Window:** Rolling 4-minute display

#### Chart D: MEMORY USAGE (Bottom-Right)
**Type:** Stacked bar chart  
**Bars:** GPU0, GPU1, CPU, RAM, Swap  
**Y-Axis:** GB (0-160 for GPUs, 0-256 for system)  

**Data Display:**
- GPU memory: Used/Total per GPU
- System memory: CPU + RAM + Swap utilization
- Overall system utilization percentage
- Color coding:
  - Green: <70% utilization
  - Yellow: 70-85% utilization
  - Red: >85% utilization (warning)

**Interactions:**
- Hover bars for exact memory values
- Click to expand detailed memory breakdown

---

### 4. TRAINING CONTROLS PANEL

**Dimensions:** 400px width x 450px height  
**Position:** Bottom-left quadrant  

**Status Display:**
- **Status Badge:** Current training state with icon
  - ⚡ TRAINING (green)
  - ⏸ PAUSED (yellow)
  - ⏹ STOPPED (gray)
  - ⚠ ERROR (red)
- **Mode:** Training mode (Single GPU, Distributed, Multi-node)

**Control Buttons (8 total):**

1. **[⏸ PAUSE TRAINING]** (F2)
   - Pauses training at next batch boundary
   - Saves checkpoint automatically
   - Becomes [▶ RESUME TRAINING] when paused

2. **[⏹ STOP TRAINING]** (F3)
   - Shows confirmation dialog
   - Saves final checkpoint
   - Generates training summary report

3. **[💾 SAVE CHECKPOINT]** (F5)
   - Immediately saves checkpoint
   - Shows save progress
   - Confirms save success

4. **[🔄 RELOAD CONFIG]**
   - Reloads training config from file
   - Shows diff if config changed
   - Requires training restart to apply

5. **[📊 EXPORT METRICS]**
   - Exports metrics to CSV/JSON
   - Opens file save dialog
   - Includes all charts and logs

6. **[🔧 ADJUST HYPERPARAMS]**
   - Opens hyperparameter tuning panel
   - Live adjustments (learning rate, batch size)
   - Some changes require restart

7. **[🎯 RUN VALIDATION]** (F8)
   - Runs validation on test set
   - Pauses training during validation
   - Shows accuracy and loss metrics

8. **[📈 VIEW TENSORBOARD]** (F9)
   - Opens TensorBoard in browser
   - Shows advanced visualizations
   - Real-time metric streaming

**Quick Actions Footer:**
- Shows most-used shortcuts
- F2, F3, F5, F8, F9 quick reference

---

### 5. PROGRESS OVERVIEW PANEL

**Dimensions:** Flexible width, 450px height  
**Position:** Bottom-right quadrant  

**Overall Progress:**
- **Percentage:** Large text (70.4%)
- **Progress Bar:** 20-segment visual bar
- **Status:** Color-coded (green/yellow/red)

**Detailed Metrics:**

**Training Progress:**
- **Epoch:** Current/Total with percentage
- **Batch:** Current/Total with percentage
- Visual sub-progress bars for each

**Time Metrics:**
- **Time Elapsed:** Hours and minutes
- **Time Remaining:** Estimated completion time
- **ETA:** Predicted completion timestamp
- **Update Frequency:** Recalculated every minute

**Checkpoint Information:**
- **Checkpoints Saved:** Total count
- **Last Save:** Relative time (e.g., "2 minutes ago")
- **Next Save:** Countdown timer
- **Auto-save Frequency:** From config

**Dataset Statistics:**
- **Total Samples:** Full dataset size
- **Samples Processed:** Completed count
- **Samples Remaining:** Pending count
- **Progress:** Percentage through dataset

**Validation Metrics:**
- **Validation Accuracy:** Latest validation run
- **Test Accuracy:** Latest test run
- **Best Accuracy:** Best achieved with epoch
- **Updated:** After each validation run

**System Health:**
- **GPU Temperature:** Current/Max for all GPUs
- **Status Indicator:** ✓ (good) / ⚠ (warning) / ❌ (critical)
- **Thermal Throttling:** Shows if throttled

**Optimization State:**
- **Learning Rate:** Current LR value
- **Gradient Norm:** L2 norm of gradients
- **Weight Decay:** Regularization parameter

---

### 6. CONFIGURATION SNAPSHOT PANEL

**Height:** 120px  
**Position:** Bottom of page  

**Header:**
- **Config File:** Filename displayed
- **Last Modified:** Relative timestamp
- **Edit Indicator:** Shows if modified since training started

**Configuration Display (Inline):**
Shows key configuration parameters in a compact, readable format:
- **Model Details:** Name, expert count, active experts
- **Batch Configuration:** Per-GPU, accumulation steps, effective batch size
- **Learning Rate:** Start value, schedule type, warmup steps
- **Optimizer:** Type and key parameters (betas, epsilon)
- **Training Settings:** Max length, precision, random seed
- **Checkpointing:** Frequency for checkpoints and validation

**Action Buttons:**
1. **[Edit Config]** - Opens config editor
2. **[View Full Config]** - Shows complete YAML in modal
3. **[Load Preset]** - Load predefined config template
4. **[Save as Template]** - Save current config as reusable template

---

### 7. STATUS BAR

**Height:** 24px  
**Position:** Fixed bottom  

**Segments:**
1. **Training Status:** "Training Active" | "Paused" | "Stopped"
2. **Progress:** "Epoch 47/100"
3. **Current Loss:** "Loss: 0.0234"
4. **GPU Temperature:** "GPU: 67°C"
5. **Quick Action:** "[F2] Pause" (context-sensitive)

---

## INTERACTION PATTERNS

### Training Lifecycle

**Starting Training:**
1. User clicks [▶ START TRAINING] from Mission Overview
2. Console page opens with initialization sequence
3. Terminal shows startup logs
4. Metrics panels populate with initial data
5. Progress indicators activate

**During Training:**
- Terminal streams logs in real-time
- Charts update every 1-2 seconds
- Progress bars increment smoothly
- Temperature and memory monitored continuously

**Pausing Training:**
1. User clicks [⏸ PAUSE] or presses F2
2. Training pauses at next batch boundary
3. Checkpoint auto-saves
4. Terminal shows "PAUSED" status
5. All metrics freeze at last values
6. Button becomes [▶ RESUME]

**Resuming Training:**
1. User clicks [▶ RESUME]
2. Training continues from checkpoint
3. Terminal shows "RESUMED" status
4. Metrics resume updating

**Stopping Training:**
1. User clicks [⏹ STOP] or presses F3
2. Confirmation dialog appears
3. On confirm:
   - Final checkpoint saved
   - Training summary generated
   - Terminal shows completion stats
   - Can export metrics or return to overview

### Error Handling

**Training Errors:**
- Terminal shows error in red
- Status changes to ⚠ ERROR
- Training auto-pauses
- Error notification displayed
- User can:
  - View error details
  - Attempt recovery
  - Stop training
  - Export error logs

**GPU Errors:**
- Thermal throttling: Warning notification
- OOM (Out of Memory): Training pauses, suggests reducing batch size
- GPU disconnection: Emergency stop, notification

**Connection Loss:**
- If backend disconnects, shows "Connection Lost" overlay
- Attempts auto-reconnect
- Preserves last known state
- On reconnect, syncs current state

---

## KEYBOARD SHORTCUTS

### Training Control
| Shortcut | Action |
|----------|--------|
| `F2` | Pause/Resume Training |
| `F3` | Stop Training |
| `F5` | Save Checkpoint Now |
| `F8` | Run Validation |
| `F9` | Open TensorBoard |
| `Ctrl+Shift+R` | Reload Configuration |
| `Ctrl+Shift+H` | Adjust Hyperparameters |

### Terminal Controls
| Shortcut | Action |
|----------|--------|
| `Ctrl+F` | Search Terminal |
| `Ctrl+L` | Clear Terminal |
| `Ctrl+C` | Copy Selected Text |
| `Ctrl+A` | Select All Terminal Text |
| `Page Up/Down` | Scroll Terminal |
| `Home` | Jump to Top of Terminal |
| `End` | Jump to Bottom of Terminal |
| `Ctrl+↑/↓` | Scroll by 5 lines |

### Chart Interactions
| Shortcut | Action |
|----------|--------|
| `Ctrl+E` | Export Current Chart |
| `Ctrl+Z` | Zoom Chart In |
| `Ctrl+Shift+Z` | Zoom Chart Out |
| `Ctrl+0` | Reset Chart Zoom |
| `1-4` | Focus Chart (1=Loss, 2=Experts, 3=Throughput, 4=Memory) |

### Navigation
| Shortcut | Action |
|----------|--------|
| `Ctrl+K` | Open Command Palette |
| `Alt+Left` | Back to Mission Overview |
| `Tab` | Cycle through controls |
| `Escape` | Close any modal/overlay |

### Quick Export
| Shortcut | Action |
|----------|--------|
| `Ctrl+S` | Quick save checkpoint |
| `Ctrl+Shift+E` | Export all metrics |
| `Ctrl+Shift+L` | Export terminal logs |
| `Ctrl+Shift+S` | Screenshot entire console |

---

## DATA REFRESH RATES

| Component | Refresh Rate | Method |
|-----------|--------------|--------|
| Terminal Output | Real-time | WebSocket push |
| Loss Chart | 2 seconds | WebSocket push |
| Expert Coverage | 5 seconds | WebSocket push |
| Throughput Chart | 1 second | WebSocket push |
| Memory Chart | 2 seconds | Polling |
| Progress Indicators | 1 second | WebSocket push |
| Temperature | 5 seconds | Polling |
| Configuration Display | On change | Event-driven |

---

## STATE MANAGEMENT

### Training State
```javascript
{
  status: "training" | "paused" | "stopped" | "error",
  epoch: {
    current: number,
    total: number,
    progress: number // 0-1
  },
  batch: {
    current: number,
    total: number,
    progress: number // 0-1
  },
  metrics: {
    loss: number,
    experts: number[], // Per-expert loss
    throughput: number, // tokens/sec
    learningRate: number,
    gradientNorm: number
  },
  system: {
    gpus: [
      { id: 0, temp: number, memory: { used: number, total: number } },
      { id: 1, temp: number, memory: { used: number, total: number } }
    ],
    cpu: number, // percentage
    ram: { used: number, total: number }
  },
  timing: {
    elapsed: number, // seconds
    remaining: number, // seconds
    eta: string // ISO timestamp
  }
}
```

### Configuration State
```javascript
{
  filename: "string",
  modified: "ISO-8601",
  model: {
    name: "string",
    experts: number,
    activeExperts: number,
    parameters: number
  },
  training: {
    batchSize: number,
    gradientAccumulation: number,
    maxLength: number,
    precision: "fp16" | "fp32" | "bf16"
  },
  optimization: {
    learningRate: number,
    schedule: "string",
    warmupSteps: number,
    optimizer: "string",
    betas: [number, number],
    epsilon: number,
    weightDecay: number
  },
  checkpointing: {
    frequency: number, // minutes
    validationFrequency: number // steps
  }
}
```

---

## RESPONSIVE BREAKPOINTS

| Breakpoint | Width | Layout Changes |
|------------|-------|----------------|
| Desktop XL | ≥1920px | Full layout with expanded charts |
| Desktop L | 1600-1919px | Standard layout as shown |
| Desktop M | 1200-1599px | Reduced chart padding |
| Tablet | 800-1199px | Stack controls + progress vertically |
| Mobile | <800px | Single column, collapsible terminal |

**Note:** Training Console is optimized for desktop use (minimum 1200px recommended)

---

## ACCESSIBILITY FEATURES

- **Screen Reader:** Announces training progress updates every 30 seconds
- **Keyboard Navigation:** Full keyboard control of all features
- **High Contrast:** Respects system high-contrast mode
- **Focus Indicators:** Clear focus states on all controls
- **Terminal Accessibility:** Screen reader support for log output
- **Alert Announcements:** Critical events announced via ARIA live regions

---

## ERROR STATES & ALERTS

### Critical Errors
```
╔═══════════════════════════════════════════╗
║  ⚠ TRAINING ERROR                         ║
║                                           ║
║  Out of Memory (OOM) on GPU 0             ║
║  Training has been paused automatically.  ║
║                                           ║
║  Suggestions:                             ║
║  • Reduce batch size (current: 32)       ║
║  • Enable gradient checkpointing          ║
║  • Reduce max sequence length             ║
║                                           ║
║  [View Logs]  [Adjust Settings]  [Stop]  ║
╚═══════════════════════════════════════════╝
```

### Warning Alerts
- **High Temperature:** Shows when GPU temp > 80°C
- **Memory Pressure:** Shows when memory > 90% used
- **Expert Imbalance:** Shows when coverage variance > 15%
- **Slow Throughput:** Shows when throughput drops > 20% from average
- **Checkpoint Failed:** Shows when checkpoint save fails

### Info Notifications
- Checkpoint saved successfully
- Validation completed
- Configuration reloaded
- Epoch milestone reached (every 10 epochs)

---

## PERFORMANCE TARGETS

- **Terminal Output:** < 10ms latency for log streaming
- **Chart Updates:** < 50ms render time per update
- **Metric Refresh:** < 100ms end-to-end latency
- **UI Responsiveness:** < 16ms frame time (60 FPS)
- **Memory Usage:** < 400MB for page
- **CPU Usage:** < 10% when idle, < 20% during active training

---

## IMPLEMENTATION NOTES

### Technology Stack
- **Terminal:** Xterm.js for terminal emulation
- **Charts:** Chart.js with real-time plugin
- **WebSocket:** Socket.io for training stream
- **State:** Redux with websocket middleware
- **Styling:** CSS Grid + Flexbox

### Component Hierarchy
```
TrainingConsole (Page)
├── HeaderBar
├── TerminalPanel
│   ├── XtermTerminal
│   ├── ScrollToggle
│   └── SearchBar
├── MetricsGrid
│   ├── LossChart
│   ├── ExpertCoverageChart
│   ├── ThroughputChart
│   └── MemoryChart
├── ControlsPanel
│   └── ControlButton (x8)
├── ProgressPanel
│   ├── ProgressBar
│   ├── MetricDisplay (x10)
│   └── HealthIndicator
├── ConfigSnapshot
│   └── ConfigDisplay
└── StatusBar
```

### File Structure
```
src/pages/TrainingConsole/
├── index.tsx
├── components/
│   ├── TerminalPanel.tsx
│   ├── MetricsGrid.tsx
│   ├── ControlsPanel.tsx
│   ├── ProgressPanel.tsx
│   └── ConfigSnapshot.tsx
├── charts/
│   ├── LossChart.tsx
│   ├── ExpertCoverageChart.tsx
│   ├── ThroughputChart.tsx
│   └── MemoryChart.tsx
├── hooks/
│   ├── useTrainingStream.ts
│   ├── useMetrics.ts
│   └── useTrainingControls.ts
├── services/
│   └── trainingAPI.ts
└── types.ts
```

---

## TESTING REQUIREMENTS

### Unit Tests
- Training control actions work correctly
- Metrics calculations are accurate
- Chart rendering with mock data
- Terminal output parsing

### Integration Tests
- WebSocket connection handling
- Training pause/resume cycle
- Checkpoint save/load
- Error recovery flows

### E2E Tests
- Complete training session
- User controls during training
- Error scenarios
- Performance under load

---

## FUTURE ENHANCEMENTS

1. **Multi-model Training:** Monitor multiple training jobs simultaneously
2. **Experiment Comparison:** Side-by-side comparison of training runs
3. **Auto-tuning:** Automatic hyperparameter optimization
4. **Collaborative Training:** Multi-user monitoring and control
5. **Mobile App:** Remote training monitoring on mobile devices
6. **Advanced Visualizations:** 3D loss landscapes, attention heatmaps
7. **Alert System:** Configurable alerts for training events
8. **Training Scheduler:** Queue and schedule training jobs
9. **Resource Prediction:** ML-powered ETA and resource prediction
10. **Integration with MLOps:** Export to MLflow, Weights & Biases, etc.

---

**Document Status:** ✓ Ready for Implementation  
**Last Updated:** 2024  
**Blueprint Version:** 1.0.0
