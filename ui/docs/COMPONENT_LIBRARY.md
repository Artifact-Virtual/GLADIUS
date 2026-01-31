# GLADIUS Command Terminal — Component Library

**Version**: 2.0  
**Last Updated**: 2026-01-30  
**Purpose**: Reusable UI components for the Electron dashboard

---

## OVERVIEW

This document defines the complete component library for the GLADIUS Command Terminal. All components follow enterprise design patterns with accessibility, keyboard navigation, and consistent styling.

### Design Principles

1. **Reusability**: Components can be used across multiple pages
2. **Accessibility**: WCAG 2.1 AA compliant
3. **Type Safety**: Full TypeScript support
4. **Performance**: Optimized rendering and memory usage
5. **Consistency**: Unified visual language

---

## CORE COMPONENTS

### 1. StatusCard

**Purpose**: Display system status, metrics, and quick information

**Props**:
```typescript
interface StatusCardProps {
  title: string;
  status: 'online' | 'offline' | 'warning' | 'error' | 'degraded';
  value?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  metrics?: Array<{ label: string; value: string }>;
  actions?: Array<{ label: string; onClick: () => void }>;
  onClick?: () => void;
  className?: string;
}
```

**Visual Example**:
```
┌────────────────────────┐
│  🧠 GLADIUS            │
│                        │
│  Status: ● ONLINE      │
│  Model: 1B (75%)       │
│  Inference: 2.1ms      │
│  Router: 100%          │
│                        │
│  [Details]  [Train]    │
└────────────────────────┘
```

**Accessibility**:
- Role: `article`
- ARIA label: Card title
- Keyboard: Tab to focus, Enter to click
- Status announced to screen readers

---

### 2. MetricChart

**Purpose**: Visualize time-series data, metrics, and distributions

**Props**:
```typescript
interface MetricChartProps {
  type: 'line' | 'bar' | 'doughnut' | 'area';
  data: ChartData;
  options?: ChartOptions;
  height?: number;
  width?: number;
  refreshInterval?: number; // ms
  animated?: boolean;
}
```

**Features**:
- Chart.js 4 integration
- Real-time data updates
- Responsive sizing
- Export to PNG/SVG
- Zoom and pan controls

---

### 3. LogStream

**Purpose**: Real-time log tailing with search and filtering

**Props**:
```typescript
interface LogStreamProps {
  source: string; // file path or stream ID
  follow: boolean;
  maxLines?: number; // default: 500
  searchTerm?: string;
  levelFilter?: 'ALL' | 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR';
  colorize?: boolean;
  showTimestamps?: boolean;
  onBookmark?: (line: string, timestamp: Date) => void;
}
```

**Visual Example**:
```
┌──────────────────────────────────────────┐
│  LIVE LOG: interactive.log     [Follow ✓]│
│  ────────────────────────────────────────│
│  [16:48:25] INFO  Pattern matched        │
│  [16:48:24] DEBUG Tool routed            │
│  [16:48:23] INFO  Query processed        │
│  [16:48:22] INFO  Response generated     │
│  ...                                     │
└──────────────────────────────────────────┘
```

---

### 4. CommandButton

**Purpose**: Execute backend commands with feedback

**Props**:
```typescript
interface CommandButtonProps {
  label: string;
  command: string;
  args?: string[];
  onComplete?: (result: CommandResult) => void;
  onError?: (error: Error) => void;
  requiresConfirm?: boolean;
  confirmMessage?: string;
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
}
```

**Behavior**:
1. Click button
2. Optional confirmation dialog
3. Execute command via IPC
4. Show loading state
5. Display result/error
6. Reset to ready state

---

### 5. AgentCard

**Purpose**: Display agent information and controls

**Props**:
```typescript
interface AgentCardProps {
  name: string;
  status: 'online' | 'offline' | 'degraded' | 'error';
  tasksQueued: number;
  tasksCompleted: number;
  lastActivity: Date;
  healthScore: number; // 0-100
  actions?: Array<{ label: string; action: string }>;
  onAction: (action: string) => void;
}
```

**Visual Example**:
```
┌────────────────────┐
│ Anomaly Detection  │
│ ● ONLINE           │
│ Tasks: 3 queued    │
│ Last: 45s ago      │
│ Health: ✓ 98%      │
│ [Details] [Stop]   │
└────────────────────┘
```

---

## LAYOUT COMPONENTS

### 6. DashboardGrid

**Purpose**: Responsive grid layout for cards and panels

**Props**:
```typescript
interface DashboardGridProps {
  columns: 1 | 2 | 3 | 4 | 'auto';
  gap?: 'sm' | 'md' | 'lg'; // 8px, 16px, 24px
  children: React.ReactNode;
  responsive?: boolean; // adapt to screen size
  minCardWidth?: number; // pixels
}
```

**Responsive Behavior**:
- **>1920px**: 4 columns
- **1440-1920px**: 3 columns
- **1024-1440px**: 2 columns
- **<1024px**: 1 column

---

### 7. SplitPanel

**Purpose**: Resizable split layout (horizontal or vertical)

**Props**:
```typescript
interface SplitPanelProps {
  left: React.ReactNode;
  right: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  initialSplit?: number; // percentage (0-100)
  minLeft?: number; // pixels
  minRight?: number; // pixels
  onResize?: (leftSize: number, rightSize: number) => void;
}
```

**Features**:
- Drag to resize
- Double-click to reset
- Keyboard resize (Shift + Arrow keys)
- Remember size in local storage

---

### 8. TabPanel

**Purpose**: Tabbed content areas

**Props**:
```typescript
interface TabPanelProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  orientation?: 'horizontal' | 'vertical';
  showCloseButton?: boolean;
  onTabClose?: (tabId: string) => void;
}

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  content: React.ReactNode;
  closeable?: boolean;
  badge?: string | number;
}
```

---

## INPUT COMPONENTS

### 9. SearchBox

**Purpose**: Fuzzy search with autocomplete

**Props**:
```typescript
interface SearchBoxProps {
  placeholder?: string;
  suggestions?: string[];
  onSearch: (query: string) => void;
  onSuggestionSelect?: (suggestion: string) => void;
  debounce?: number; // ms
  autoFocus?: boolean;
}
```

---

### 10. FilterBar

**Purpose**: Multi-criteria filtering

**Props**:
```typescript
interface FilterBarProps {
  filters: Filter[];
  activeFilters: Map<string, any>;
  onFilterChange: (filterId: string, value: any) => void;
  onClearAll: () => void;
}

interface Filter {
  id: string;
  type: 'select' | 'multiselect' | 'range' | 'date' | 'toggle';
  label: string;
  options?: Array<{ value: any; label: string }>;
  defaultValue?: any;
}
```

---

## DATA DISPLAY COMPONENTS

### 11. DataTable

**Purpose**: Sortable, filterable data table

**Props**:
```typescript
interface DataTableProps {
  columns: Column[];
  data: any[];
  sortable?: boolean;
  filterable?: boolean;
  selectable?: boolean;
  onRowClick?: (row: any) => void;
  onSelectionChange?: (selectedRows: any[]) => void;
  pageSize?: number;
  pagination?: boolean;
}

interface Column {
  key: string;
  header: string;
  width?: number;
  sortable?: boolean;
  filterable?: boolean;
  render?: (value: any, row: any) => React.ReactNode;
}
```

---

### 12. ProgressBar

**Purpose**: Visual progress indicator

**Props**:
```typescript
interface ProgressBarProps {
  value: number; // 0-100
  max?: number;
  label?: string;
  showPercentage?: boolean;
  variant?: 'default' | 'success' | 'warning' | 'error';
  animated?: boolean;
  indeterminate?: boolean; // for unknown progress
}
```

**Visual Example**:
```
Progress: ▓▓▓▓▓▓▓░░░ 75%
```

---

### 13. StatusIndicator

**Purpose**: Visual status dot with label

**Props**:
```typescript
interface StatusIndicatorProps {
  status: 'online' | 'offline' | 'warning' | 'error' | 'degraded';
  label?: string;
  pulse?: boolean;
  size?: 'sm' | 'md' | 'lg';
}
```

**Visual Example**:
```
● ONLINE    ⚠ WARNING    ● OFFLINE    ● ERROR
```

---

## MODAL COMPONENTS

### 14. Modal

**Purpose**: Overlay dialog for confirmations and forms

**Props**:
```typescript
interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  closeOnEscape?: boolean;
  closeOnOverlayClick?: boolean;
}
```

---

### 15. ConfirmDialog

**Purpose**: Simple confirmation dialog

**Props**:
```typescript
interface ConfirmDialogProps {
  isOpen: boolean;
  title: string;
  message: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  variant?: 'default' | 'danger';
}
```

---

## UTILITY COMPONENTS

### 16. Tooltip

**Purpose**: Contextual help text on hover

**Props**:
```typescript
interface TooltipProps {
  content: string | React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number; // ms
  children: React.ReactNode;
}
```

---

### 17. Toast

**Purpose**: Temporary notification message

**Props**:
```typescript
interface ToastProps {
  message: string;
  variant?: 'info' | 'success' | 'warning' | 'error';
  duration?: number; // ms, 0 = permanent
  position?: 'top-left' | 'top-center' | 'top-right' | 'bottom-left' | 'bottom-center' | 'bottom-right';
  onClose?: () => void;
}
```

---

### 18. Spinner

**Purpose**: Loading indicator

**Props**:
```typescript
interface SpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  color?: string;
  label?: string;
}
```

---

## STYLING PATTERNS

### Color System

```typescript
const colors = {
  // Status
  online: '#10B981',
  offline: '#6B7280',
  warning: '#F59E0B',
  error: '#EF4444',
  degraded: '#F59E0B',
  
  // Semantic
  primary: '#3B82F6',
  success: '#10B981',
  info: '#8B5CF6',
  
  // Backgrounds
  bg: {
    primary: '#0A0E27',
    secondary: '#151B3B',
    accent: '#1E2749',
  },
  
  // Text
  text: {
    primary: '#E4E7EB',
    secondary: '#9CA3AF',
    muted: '#6B7280',
  },
  
  // Border
  border: '#2D3748',
  focus: '#60A5FA',
};
```

### Typography

```typescript
const typography = {
  fontFamily: {
    sans: "'Inter', system-ui, sans-serif",
    mono: "'Fira Code', 'Courier New', monospace",
  },
  
  fontSize: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
  },
  
  fontWeight: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
};
```

### Spacing

```typescript
const spacing = {
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
};
```

---

## ACCESSIBILITY GUIDELINES

### Keyboard Navigation

All components must support:
- **Tab**: Focus next element
- **Shift+Tab**: Focus previous element
- **Enter/Space**: Activate buttons, select items
- **Arrow keys**: Navigate lists, tables, menus
- **Escape**: Close modals, cancel actions

### Screen Reader Support

- Use semantic HTML elements
- Provide ARIA labels for icons
- Announce state changes
- Use live regions for dynamic content
- Provide skip links

### Visual Accessibility

- Minimum contrast ratio: 4.5:1 for text
- Focus indicators: 2px solid outline
- Text resizable to 200%
- No color-only indicators
- Support high contrast mode

---

## PERFORMANCE GUIDELINES

### Optimization Strategies

1. **Virtualization**: For large lists (use react-window)
2. **Memoization**: Expensive calculations (useMemo, React.memo)
3. **Lazy Loading**: Code splitting for routes
4. **Debouncing**: Search inputs, scroll handlers
5. **Throttling**: Resize handlers, real-time updates

### Memory Management

- Clean up WebSocket connections
- Unsubscribe from events
- Cancel pending requests
- Clear timers and intervals
- Limit log buffer size

---

## TESTING REQUIREMENTS

### Unit Tests

- Component rendering
- Props validation
- Event handlers
- Edge cases
- Error states

### Integration Tests

- User interactions
- State management
- API calls
- Navigation flows

### Accessibility Tests

- Keyboard navigation
- Screen reader support
- Color contrast
- Focus management

---

## USAGE EXAMPLES

### StatusCard Example

```typescript
import { StatusCard } from '@/components';

function Example() {
  return (
    <StatusCard
      title="GLADIUS"
      status="online"
      icon={<BrainIcon />}
      value="Model: 1B (75%)"
      metrics={[
        { label: 'Inference', value: '2.1ms' },
        { label: 'Router', value: '100%' },
      ]}
      actions={[
        { label: 'Details', onClick: () => navigate('/training') },
        { label: 'Train', onClick: () => startTraining() },
      ]}
    />
  );
}
```

### MetricChart Example

```typescript
import { MetricChart } from '@/components';

function Example() {
  const data = {
    labels: ['0', '10', '20', '30', '40'],
    datasets: [{
      label: 'Loss',
      data: [0.8, 0.6, 0.5, 0.4, 0.32],
      borderColor: '#3B82F6',
    }],
  };

  return (
    <MetricChart
      type="line"
      data={data}
      height={300}
      refreshInterval={5000}
    />
  );
}
```

---

**End of Component Library**

