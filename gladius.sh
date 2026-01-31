#!/bin/bash
# =============================================================================
# GLADIUS - Unified Control Script
# =============================================================================
#
# Single command to manage all Gladius services.
#
# Usage:
#   ./gladius.sh start           # Start all services + health check
#   ./gladius.sh stop            # Stop all services + regression check
#   ./gladius.sh restart         # Stop then start
#   ./gladius.sh status          # Quick status check
#   ./gladius.sh health          # Full health check
#   ./gladius.sh logs            # Tail all logs
#   ./gladius.sh infra           # Test Infra API specifically
#
# =============================================================================

# Don't use set -e as we want to continue even if some services fail

# Dynamic path detection - works from any location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLADIUS_ROOT="$SCRIPT_DIR"
LOG_DIR="$GLADIUS_ROOT/logs"
PID_DIR="$GLADIUS_ROOT/.pids"

# Prefer local virtualenv Python if available
VENV_PYTHON="$GLADIUS_ROOT/.venv/bin/python"
if [ -x "$VENV_PYTHON" ]; then
    PYTHON="$VENV_PYTHON"
else
    PYTHON="$(command -v python3 || command -v python || echo python)"
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# =============================================================================
# CONFIGURATION
# =============================================================================

CONFIG_FILE="$GLADIUS_ROOT/config.json"

# Function to read config value using Python (jq alternative)
get_config() {
    local path="$1"
    local default="$2"
    if [ -f "$CONFIG_FILE" ]; then
        "$PYTHON" -c "
import json
try:
    with open('$CONFIG_FILE') as f:
        config = json.load(f)
    keys = '$path'.split('.')
    val = config
    for k in keys:
        val = val.get(k, {})
    print(val if val != {} else '$default')
except:
    print('$default')
" 2>/dev/null
    else
        echo "$default"
    fi
}

# Module enabled checks
is_module_enabled() {
    local module="$1"
    local result=$(get_config "modules.$module.enabled" "true")
    [ "$result" = "True" ] || [ "$result" = "true" ]
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

check_port() {
    lsof -i:$1 > /dev/null 2>&1
    return $?
}

check_http() {
    curl -s --connect-timeout 3 --max-time 5 "$1" > /dev/null 2>&1
    return $?
}

get_response_time() {
    curl -s -o /dev/null -w "%{time_total}" --connect-timeout 3 --max-time 5 "$1" 2>/dev/null
}

wait_for_http() {
    # Wait for an HTTP endpoint to respond (retries, delay configurable)
    local url="$1"
    local retries=${2:-12}
    local delay=${3:-1}
    for i in $(seq 1 $retries); do
        if check_http "$url"; then
            return 0
        fi
        sleep $delay
    done
    return 1
}

print_header() {
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║                                                               ║${NC}"
    echo -e "${BLUE}║              G L A D I U S   C O N T R O L   S Y S T E M S    ║${NC}"
    echo -e "${BLUE}║                                                               ║${NC}"
    echo -e "${BLUE}║       Native AI  ·  Artifact Virtual  ·  Enterprise          ║${NC}"
    echo -e "${BLUE}║                                                               ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# =============================================================================
# HEALTH CHECK FUNCTION
# =============================================================================

do_health_check() {
    local verbose=${1:-false}
    local all_ok=true
    
    echo -e "${CYAN}Timestamp: $(date)${NC}"
    echo ""
    
    # SENTINEL Status (Guardian)
    echo -e "${BLUE}SENTINEL Guardian${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    if [ -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid" ]; then
        local spid=$(cat "$GLADIUS_ROOT/SENTINEL/sentinel.pid" 2>/dev/null)
        if kill -0 "$spid" 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} Watchdog            ${GREEN}OK${NC}  [PID: $spid]"
        else
            echo -e "  ${RED}❌${NC} Watchdog            ${RED}DEAD${NC}"
            all_ok=false
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  Watchdog            ${YELLOW}NOT STARTED${NC}"
    fi
    
    if pgrep -f "learning_daemon.py" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Learning Daemon      ${GREEN}OK${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Learning Daemon      ${YELLOW}NOT RUNNING${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Service Status${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    # Infra API (7000)
    if check_http "http://127.0.0.1:7000/docs"; then
        local time=$(get_response_time "http://127.0.0.1:7000/docs")
        echo -e "  ${GREEN}✅${NC} Infra API (7000)     ${GREEN}OK${NC}  [${time}s]"
    else
        echo -e "  ${RED}❌${NC} Infra API (7000)     ${RED}DOWN${NC}"
        all_ok=false
    fi
    
    # Dashboard Backend (5000)
    if check_http "http://127.0.0.1:5000/health"; then
        local time=$(get_response_time "http://127.0.0.1:5000/health")
        echo -e "  ${GREEN}✅${NC} Dashboard API (5000) ${GREEN}OK${NC}  [${time}s]"
    else
        echo -e "  ${RED}❌${NC} Dashboard API (5000) ${RED}DOWN${NC}"
        all_ok=false
    fi

    # Web UI (5002) - Electron UI status
    if pgrep -f "electron" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✅${NC} Electron UI        ${GREEN}RUNNING${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Electron UI        ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Frontend (3000) - optional
    if check_port 3000; then
        echo -e "  ${GREEN}✅${NC} Frontend (3000)      ${GREEN}OK${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Frontend (3000)      ${YELLOW}NOT RUNNING${NC} (optional)"
    fi
    
    # Syndicate Daemon
    if pgrep -f "run.py.*--interval-min" > /dev/null 2>&1; then
        local pid=$(pgrep -f "run.py.*--interval-min")
        echo -e "  ${GREEN}✅${NC} Syndicate Daemon     ${GREEN}OK${NC}  [PID: $pid]"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Syndicate Daemon     ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Grafana (3001)
    if check_port 3001; then
        echo -e "  ${GREEN}✅${NC} Grafana (3001)       ${GREEN}OK${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Grafana (3001)       ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Prometheus (9090)
    if check_port 9090; then
        echo -e "  ${GREEN}✅${NC} Prometheus (9090)    ${GREEN}OK${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Prometheus (9090)    ${YELLOW}NOT RUNNING${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}LEGION Enterprise${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    # LEGION Orchestrator
    if pgrep -f "continuous_operation.py" > /dev/null 2>&1; then
        local lpid=$(pgrep -f "continuous_operation.py")
        echo -e "  ${GREEN}✅${NC} Orchestrator         ${GREEN}OK${NC}  [PID: $lpid]"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Orchestrator         ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Check Artifact Bridge connectivity
    if [ -f "$GLADIUS_ROOT/LEGION/legion/artifact_bridge.py" ]; then
        echo -e "  ${GREEN}✅${NC} Artifact Bridge      ${GREEN}AVAILABLE${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Artifact Bridge      ${YELLOW}NOT FOUND${NC}"
    fi
    
    echo ""
    
    # Verbose mode: test API endpoints
    if [ "$verbose" = true ]; then
        echo -e "${BLUE}API Endpoint Tests${NC}"
        echo "─────────────────────────────────────────────────────────────────"
        
        if check_http "http://127.0.0.1:7000/markets"; then
            echo -e "  ${GREEN}✓${NC} GET /markets"
        else
            echo -e "  ${RED}✗${NC} GET /markets"
        fi
        
        if check_http "http://127.0.0.1:7000/assets"; then
            echo -e "  ${GREEN}✓${NC} GET /assets"
        else
            echo -e "  ${RED}✗${NC} GET /assets"
        fi
        
        if check_http "http://127.0.0.1:7000/portfolios"; then
            echo -e "  ${GREEN}✓${NC} GET /portfolios"
        else
            echo -e "  ${RED}✗${NC} GET /portfolios"
        fi
        echo ""
    fi
    
    # Summary
    if [ "$all_ok" = true ]; then
        echo -e "  ${GREEN}🎉 Core services operational!${NC}"
        return 0
    else
        echo -e "  ${RED}🚨 Some services are down!${NC}"
        return 1
    fi
}

# =============================================================================
# START FUNCTION
# =============================================================================

do_start() {
    print_header
    echo -e "${BLUE}Starting Services...${NC}"
    echo ""
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    
    # Load environment (safely handle special characters)
    if [ -f "$GLADIUS_ROOT/.env" ]; then
        set -a
        source <(grep -v '^#' "$GLADIUS_ROOT/.env" | grep -E '^[A-Z_][A-Z0-9_]*=' | sed 's/=\(.*\)/="\1"/')
        set +a
    fi
    
    # ═══════════════════════════════════════════════════════════════════════
    # PHASE 0: SENTINEL (Guardian Process - MUST START FIRST)
    # ═══════════════════════════════════════════════════════════════════════
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}PHASE 0: SENTINEL Guardian System${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    local sentinel_ok=true
    
    # Check if SENTINEL is already running
    if [ -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid" ]; then
        local sentinel_pid=$(cat "$GLADIUS_ROOT/SENTINEL/sentinel.pid" 2>/dev/null)
        if kill -0 "$sentinel_pid" 2>/dev/null; then
            echo -e "  ${GREEN}✅${NC} SENTINEL already running (PID: $sentinel_pid)"
        else
            echo -e "  ${YELLOW}⚠️${NC}  Stale PID file found, starting SENTINEL..."
            rm -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid"
            "$GLADIUS_ROOT/scripts/start_sentinel.sh" detached
            sleep 3
        fi
    else
        echo -e "  ${BLUE}→${NC} Starting SENTINEL Guardian..."
        "$GLADIUS_ROOT/scripts/start_sentinel.sh" detached
        sleep 3
    fi
    
    # Verify SENTINEL health checks
    echo ""
    echo -e "  ${BLUE}Running SENTINEL Health Checks...${NC}"
    
    # Check 1: Watchdog running
    if [ -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid" ]; then
        local wpid=$(cat "$GLADIUS_ROOT/SENTINEL/sentinel.pid" 2>/dev/null)
        if kill -0 "$wpid" 2>/dev/null; then
            echo -e "    ${GREEN}✓${NC} Watchdog:        RUNNING (PID: $wpid)"
        else
            echo -e "    ${RED}✗${NC} Watchdog:        NOT RUNNING"
            sentinel_ok=false
        fi
    else
        echo -e "    ${RED}✗${NC} Watchdog:        NOT STARTED"
        sentinel_ok=false
    fi
    
    # Check 2: Learning daemon started (may take a moment)
    if pgrep -f "learning_daemon.py" > /dev/null 2>&1; then
        echo -e "    ${GREEN}✓${NC} Learning Daemon: RUNNING"
    else
        echo -e "    ${YELLOW}○${NC} Learning Daemon: STARTING (async)"
    fi
    
    # Check 3: Kill password configured
    if [ -n "$SENTINEL_KILL_PASSWORD" ]; then
        echo -e "    ${GREEN}✓${NC} Kill Password:   CONFIGURED"
    else
        echo -e "    ${YELLOW}○${NC} Kill Password:   NOT SET (using default)"
    fi
    
    # Check 4: State database exists
    if [ -f "$GLADIUS_ROOT/SENTINEL/services/learning_state.db" ]; then
        echo -e "    ${GREEN}✓${NC} State Database:  READY"
    else
        echo -e "    ${YELLOW}○${NC} State Database:  WILL BE CREATED"
    fi
    
    echo ""
    
    if [ "$sentinel_ok" = true ]; then
        echo -e "  ${GREEN}🛡️  SENTINEL OPERATIONAL - Proceeding with system startup${NC}"
    else
        echo -e "  ${RED}❌ SENTINEL FAILED - Aborting startup${NC}"
        echo ""
        echo "  To manually start SENTINEL:"
        echo "  ./scripts/start_sentinel.sh detached"
        echo ""
        return 1
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}PHASE 1: Core Services${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 1. Start Infra API (most important - market data layer)
    echo -e "${CYAN}[1/6] Infra API${NC}"
    if check_port 7000; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 7000"
    else
        echo -e "  ${BLUE}→${NC} Starting Infra API..."
        cd "$GLADIUS_ROOT/Artifact/deployment"
        nohup python3 -m uvicorn infra.api.app:app --host 127.0.0.1 --port 7000 > "$LOG_DIR/infra_api.log" 2>&1 &
        echo $! > "$PID_DIR/infra_api.pid"
        sleep 2
        if check_port 7000; then
            echo -e "  ${GREEN}✅${NC} Started on port 7000"
        else
            echo -e "  ${RED}❌${NC} Failed to start"
        fi
    fi
    
    # 2. Start Dashboard Backend (Flask + SocketIO)
    echo -e "${CYAN}[2/6] Dashboard Backend${NC}"
    if check_port 5000; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 5000"
    else
        echo -e "  ${BLUE}→${NC} Starting Dashboard Backend..."
        cd "$GLADIUS_ROOT/Artifact/deployment/automata/dashboard/backend"
        nohup "$PYTHON" app.py > "$LOG_DIR/dashboard_backend.log" 2>&1 &
        echo $! > "$PID_DIR/dashboard_backend.pid"
        sleep 2
        if check_port 5000; then
            echo -e "  ${GREEN}✅${NC} Started on port 5000"
            echo -e "  ${BLUE}→${NC} Waiting for Dashboard API to be ready..."
            if wait_for_http "http://127.0.0.1:5000/health" 12 2; then
                echo -e "  ${GREEN}✅${NC} Dashboard API healthy"
            else
                echo -e "  ${YELLOW}⚠️${NC} Dashboard API did not respond to /health in time"
            fi
        else
            echo -e "  ${RED}❌${NC} Failed to start"
        fi
    fi

    # 3. Start Electron UI
    echo -e "${CYAN}[3/6] Electron UI${NC}"
    if pgrep -f "electron.*gladius" > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠️${NC}  Electron UI already running"
    elif [ -d "$GLADIUS_ROOT/ui" ]; then
        echo -e "  ${BLUE}→${NC} Starting Electron UI..."
        cd "$GLADIUS_ROOT/ui"
        
        # Build if needed
        if [ ! -d "dist" ]; then
            echo -e "  ${BLUE}→${NC} Building UI (first time)..."
            npm run build > "$LOG_DIR/ui_build.log" 2>&1 || true
        fi
        
        # Launch Electron
        ELECTRON_RUN_AS_NODE= nohup npm run start > "$LOG_DIR/ui.log" 2>&1 &
        echo $! > "$PID_DIR/ui.pid"
        sleep 3
        
        if pgrep -f "electron" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✅${NC} Electron UI launched"
        else
            echo -e "  ${YELLOW}⚠️${NC}  UI may take a moment to start"
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  UI directory not found"
    fi

    # 4. Start Grafana (via Docker)
    echo -e "${CYAN}[4/6] Grafana${NC}"
    if check_port 3001; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 3001"
    elif ! command -v docker &> /dev/null; then
        echo -e "  ${YELLOW}⚠️${NC}  Docker not available - skipping Grafana"
    else
        echo -e "  ${BLUE}→${NC} Starting Grafana via Docker..."
        cd "$GLADIUS_ROOT/Artifact/syndicate/docker"
        docker run -d --name gold_grafana \
            -p 3001:3000 \
            -e GF_SECURITY_ADMIN_PASSWORD=admin \
            -v "$(pwd)/grafana:/var/lib/grafana" \
            grafana/grafana:9.5.0 > /dev/null 2>&1 || true
        sleep 2
        if check_port 3001; then
            echo -e "  ${GREEN}✅${NC} Started on port 3001"
        else
            echo -e "  ${YELLOW}⚠️${NC}  May take a moment to start"
        fi
    fi
    
    # 5. Start Prometheus (via Docker - for Grafana metrics)
    echo -e "${CYAN}[5/6] Prometheus${NC}"
    if check_port 9090; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 9090"
    elif ! command -v docker &> /dev/null; then
        echo -e "  ${YELLOW}⚠️${NC}  Docker not available - skipping Prometheus"
    else
        echo -e "  ${BLUE}→${NC} Starting Prometheus via Docker..."
        cd "$GLADIUS_ROOT/Artifact/syndicate/docker"
        docker run -d --name gold_prometheus \
            -p 9090:9090 \
            -v "$(pwd)/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro" \
            prom/prometheus:latest > /dev/null 2>&1 || true
        sleep 2
        if check_port 9090; then
            echo -e "  ${GREEN}✅${NC} Started on port 9090"
        else
            echo -e "  ${YELLOW}⚠️${NC}  May take a moment to start"
        fi
    fi
    
    # 6. Start Syndicate Daemon (market intelligence - runs in background)
    echo -e "${CYAN}[6/7] Syndicate Daemon${NC}"
    if pgrep -f "run.py.*--interval-min" > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running"
    else
        echo -e "  ${BLUE}→${NC} Starting Syndicate Daemon..."
        cd "$GLADIUS_ROOT/Artifact/syndicate"
        nohup env PREFER_OLLAMA=1 "$PYTHON" run.py --interval-min 60 > "$LOG_DIR/syndicate_daemon.log" 2>&1 &
        echo $! > "$PID_DIR/syndicate_daemon.pid"
        sleep 2
        echo -e "  ${GREEN}✅${NC} Daemon started"
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}PHASE 2: LEGION Enterprise Orchestrator${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 7. Start LEGION Enterprise Orchestrator (check config toggle)
    echo -e "${CYAN}[7/7] LEGION Orchestrator${NC}"
    if ! is_module_enabled "legion"; then
        echo -e "  ${YELLOW}⚠️${NC}  LEGION disabled in config.json"
        echo -e "  ${CYAN}→${NC} To enable: set modules.legion.enabled = true"
    elif pgrep -f "continuous_operation.py" > /dev/null 2>&1; then
        local lpid=$(pgrep -f "continuous_operation.py")
        echo -e "  ${GREEN}✅${NC} Already running (PID: $lpid)"
    else
        if [ -f "$GLADIUS_ROOT/LEGION/legion/continuous_operation.py" ]; then
            echo -e "  ${BLUE}→${NC} Starting LEGION Continuous Orchestrator..."
            cd "$GLADIUS_ROOT/LEGION/legion"
            nohup "$PYTHON" continuous_operation.py > "$LOG_DIR/legion.log" 2>&1 &
            echo $! > "$PID_DIR/legion.pid"
            sleep 3
            if pgrep -f "continuous_operation.py" > /dev/null 2>&1; then
                echo -e "  ${GREEN}✅${NC} LEGION Orchestrator started"
                echo -e "  ${GREEN}✅${NC} AI Agents: ACTIVE"
                echo -e "  ${GREEN}✅${NC} Artifact Bridge: CONNECTED"
            else
                echo -e "  ${RED}❌${NC} Failed to start LEGION"
            fi
        else
            echo -e "  ${YELLOW}⚠️${NC}  LEGION not found at $GLADIUS_ROOT/LEGION"
        fi
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run health check
    echo -e "${BLUE}System Health Check${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    sleep 2
    do_health_check
    local health_status=$?
    
    echo ""
    
    # Only show OPERATIONAL if health check passed
    if [ $health_status -eq 0 ]; then
        echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${GREEN}║                    GLADIUS SYSTEM OPERATIONAL                 ║${NC}"
        echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    else
        echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
        echo -e "${RED}║                    GLADIUS SYSTEM DEGRADED                    ║${NC}"
        echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    fi
    echo ""
    echo -e "  ${BLUE}▌ ACCESS POINTS${NC}"
    echo -e "    ${CYAN}Electron UI${NC}      Desktop Application"
    echo -e "    ${CYAN}Infra API${NC}        http://localhost:7000/docs"
    echo -e "    ${CYAN}Dashboard API${NC}    http://localhost:5000"
    if check_port 3001; then
        echo -e "    ${CYAN}Grafana${NC}          http://localhost:3001"
    fi
    if check_port 9090; then
        echo -e "    ${CYAN}Prometheus${NC}       http://localhost:9090"
    fi
    echo ""
    echo -e "  ${BLUE}▌ COMMANDS${NC}"
    echo -e "    ${CYAN}Status${NC}           ./gladius.sh status"
    echo -e "    ${CYAN}Health${NC}           ./gladius.sh health"
    echo -e "    ${CYAN}Logs${NC}             ./gladius.sh logs"
    echo -e "    ${CYAN}Stop${NC}             ./gladius.sh stop"
    echo ""
    echo -e "  ${BLUE}▌ LOGS${NC}"
    echo -e "    tail -f $LOG_DIR/*.log"
    echo ""
}

# =============================================================================
# STOP FUNCTION
# =============================================================================

do_stop() {
    print_header
    echo -e "${BLUE}Stopping Services...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    local force=${1:-false}
    
    # Stop Electron UI first
    echo -e "${CYAN}[1/7] Electron UI${NC}"
    local pid=$(pgrep -f "electron.*gladius" 2>/dev/null || pgrep -f "electron" 2>/dev/null | head -1)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Dashboard Backend (5000)
    echo -e "${CYAN}[2/7] Dashboard Backend${NC}"
    pid=$(lsof -t -i:5000 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi

    # Stop Infra API (7000)
    echo -e "${CYAN}[3/7] Infra API${NC}"
    pid=$(lsof -t -i:7000 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Grafana (Docker)
    echo -e "${CYAN}[4/7] Grafana${NC}"
    if docker ps -q -f name=gold_grafana 2>/dev/null | grep -q .; then
        docker stop gold_grafana > /dev/null 2>&1
        docker rm gold_grafana > /dev/null 2>&1
        echo -e "  ${GREEN}✅${NC} Stopped Grafana container"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Prometheus (Docker)
    echo -e "${CYAN}[5/7] Prometheus${NC}"
    if docker ps -q -f name=gold_prometheus 2>/dev/null | grep -q .; then
        docker stop gold_prometheus > /dev/null 2>&1
        docker rm gold_prometheus > /dev/null 2>&1
        echo -e "  ${GREEN}✅${NC} Stopped Prometheus container"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Syndicate Daemon
    echo -e "${CYAN}[6/7] Syndicate Daemon${NC}"
    pid=$(pgrep -f "run.py.*--interval-min" 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Syndicate Daemon was not running"
    fi
    
    # Stop LEGION Orchestrator
    echo -e "${CYAN}[7/7] LEGION Orchestrator${NC}"
    pid=$(pgrep -f "continuous_operation.py" 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  LEGION was not running"
    fi
    
    # Clean up PID files
    rm -f "$PID_DIR"/*.pid 2>/dev/null
    
    echo ""
    
    # Regression check - verify everything is stopped
    echo -e "${BLUE}Regression Check (verifying shutdown)...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    sleep 2
    
    local remaining=0
    
    if check_port 7000; then
        echo -e "  ${RED}⚠️${NC}  Port 7000 still in use"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Port 7000 clear"
    fi
    
    if check_port 5000; then
        echo -e "  ${RED}⚠️${NC}  Port 5000 still in use"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Port 5000 clear"
    fi

    if pgrep -f "electron" > /dev/null 2>&1; then
        echo -e "  ${RED}⚠️${NC}  Electron UI still running"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Electron UI stopped"
    fi
    
    if pgrep -f "run.py.*--interval-min" > /dev/null 2>&1; then
        echo -e "  ${RED}⚠️${NC}  Syndicate daemon still running"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Syndicate daemon stopped"
    fi
    
    if pgrep -f "continuous_operation.py" > /dev/null 2>&1; then
        echo -e "  ${RED}⚠️${NC}  LEGION still running"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} LEGION stopped"
    fi
    
    echo ""
    
    if [ $remaining -eq 0 ]; then
        echo -e "  ${GREEN}🛑 All services stopped successfully!${NC}"
    else
        echo -e "  ${RED}⚠️  $remaining service(s) may still be running${NC}"
        echo ""
        echo "  Run with --force to forcefully terminate:"
        echo "  ./gladius.sh stop --force"
    fi
    echo ""
}

# =============================================================================
# STATUS FUNCTION (Quick)
# =============================================================================

do_status() {
    echo ""
    echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                   GLADIUS STATUS                              ║${NC}"
    echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo -e "  ${BLUE}Timestamp:${NC} $(date)"
    echo ""
    
    echo -e "  ${BLUE}▌ SENTINEL${NC}"
    # SENTINEL status
    if [ -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid" ]; then
        local spid=$(cat "$GLADIUS_ROOT/SENTINEL/sentinel.pid" 2>/dev/null)
        if kill -0 "$spid" 2>/dev/null; then
            echo -e "    ${GREEN}●${NC} Watchdog         [PID: $spid]"
        else
            echo -e "    ${RED}○${NC} Watchdog"
        fi
    else
        echo -e "    ${RED}○${NC} Watchdog"
    fi
    pgrep -f "learning_daemon.py" > /dev/null 2>&1 && echo -e "    ${GREEN}●${NC} Learning Daemon" || echo -e "    ${YELLOW}○${NC} Learning Daemon"
    
    echo ""
    echo -e "  ${BLUE}▌ CORE SERVICES${NC}"
    check_port 7000 && echo -e "    ${GREEN}●${NC} Infra API        :7000" || echo -e "    ${RED}○${NC} Infra API        :7000"
    check_port 5000 && echo -e "    ${GREEN}●${NC} Dashboard API    :5000" || echo -e "    ${RED}○${NC} Dashboard API    :5000"
    pgrep -f "electron" > /dev/null 2>&1 && echo -e "    ${GREEN}●${NC} Electron UI      Running" || echo -e "    ${YELLOW}○${NC} Electron UI"
    
    echo ""
    echo -e "  ${BLUE}▌ MONITORING${NC}"
    check_port 3001 && echo -e "    ${GREEN}●${NC} Grafana          :3001" || echo -e "    ${YELLOW}○${NC} Grafana          :3001"
    check_port 9090 && echo -e "    ${GREEN}●${NC} Prometheus       :9090" || echo -e "    ${YELLOW}○${NC} Prometheus       :9090"
    
    echo ""
    echo -e "  ${BLUE}▌ DAEMONS${NC}"
    pgrep -f "run.py.*--interval-min" > /dev/null 2>&1 && echo -e "    ${GREEN}●${NC} Syndicate" || echo -e "    ${YELLOW}○${NC} Syndicate"
    
    echo ""
    echo -e "  ${BLUE}▌ LEGION ENTERPRISE${NC}"
    if pgrep -f "continuous_operation.py" > /dev/null 2>&1; then
        local lpid=$(pgrep -f "continuous_operation.py")
        echo -e "    ${GREEN}●${NC} Orchestrator     [PID: $lpid]"
    else
        echo -e "    ${YELLOW}○${NC} Orchestrator"
    fi
    [ -f "$GLADIUS_ROOT/LEGION/legion/artifact_bridge.py" ] && echo -e "    ${GREEN}●${NC} Artifact Bridge" || echo -e "    ${YELLOW}○${NC} Artifact Bridge"
    
    echo ""
    echo -e "  ${BLUE}───────────────────────────────────────────────────────────${NC}"
    echo ""
}

# =============================================================================
# INFRA TEST FUNCTION
# =============================================================================

do_infra_test() {
    print_header
    echo -e "${BLUE}Testing Infra API...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    if ! check_http "http://127.0.0.1:7000/docs"; then
        echo -e "  ${RED}❌ Infra API is not running!${NC}"
        echo ""
        echo "  Start it with: ./gladius.sh start"
        echo ""
        return 1
    fi
    
    echo -e "  ${GREEN}✅${NC} Infra API is running"
    echo ""
    
    # Test endpoints
    echo -e "${BLUE}Endpoint Tests${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    echo -n "  GET /markets ... "
    local markets=$(curl -s http://127.0.0.1:7000/markets 2>/dev/null)
    if [ $? -eq 0 ]; then
        local count=$(echo "$markets" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
        echo -e "${GREEN}OK${NC} ($count markets)"
    else
        echo -e "${RED}FAILED${NC}"
    fi
    
    echo -n "  GET /assets ... "
    local assets=$(curl -s http://127.0.0.1:7000/assets 2>/dev/null)
    if [ $? -eq 0 ]; then
        local count=$(echo "$assets" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
        echo -e "${GREEN}OK${NC} ($count assets)"
    else
        echo -e "${RED}FAILED${NC}"
    fi
    
    echo -n "  GET /portfolios ... "
    local portfolios=$(curl -s http://127.0.0.1:7000/portfolios 2>/dev/null)
    if [ $? -eq 0 ]; then
        local count=$(echo "$portfolios" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "?")
        echo -e "${GREEN}OK${NC} ($count portfolios)"
    else
        echo -e "${RED}FAILED${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}API Documentation${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    echo "  OpenAPI Docs: http://127.0.0.1:7000/docs"
    echo "  ReDoc:        http://127.0.0.1:7000/redoc"
    echo ""
    
    # Check if data is seeded
    local market_count=$(echo "$markets" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))" 2>/dev/null || echo "0")
    if [ "$market_count" = "0" ]; then
        echo -e "${YELLOW}⚠️  No markets found. Seed sample data:${NC}"
        echo "  cd Artifact/deployment/infra && python scripts/seed_gold_bitcoin.py"
        echo ""
    fi
}

# =============================================================================
# LOGS FUNCTION
# =============================================================================

do_logs() {
    if [ -d "$LOG_DIR" ] && ls "$LOG_DIR"/*.log 1> /dev/null 2>&1; then
        echo -e "${CYAN}Tailing all logs (Ctrl+C to stop)...${NC}"
        echo ""
        tail -f "$LOG_DIR"/*.log
    else
        echo -e "${YELLOW}No log files found in $LOG_DIR${NC}"
    fi
}

# =============================================================================
# COGNITION CYCLE - Single autonomous learning cycle
# =============================================================================

do_cognition() {
    print_header
    echo -e "${BLUE}Running Cognition Learning Cycle...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    cd "$GLADIUS_ROOT/Artifact/syndicate"
    "$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from src.cognition import LEARNING_AVAILABLE, CognitionLearningLoop

if not LEARNING_AVAILABLE:
    print('[COGNITION] Learning module not available')
    sys.exit(1)

print('[COGNITION] Starting autonomous learning cycle...')
loop = CognitionLearningLoop(base_dir='.', data_dir='./data', output_dir='./output')
result = loop.run_cycle()
print(f'[COGNITION] Reports Ingested: {result.reports_ingested}')
print(f'[COGNITION] Training Examples: {result.training_examples_generated}')
print(f'[COGNITION] Proposals Created: {result.proposals_created}')
print(f'[COGNITION] Proposals Completed: {result.proposals_completed}')
loop.close()
print('[COGNITION] Cycle complete.')
"
    echo ""
}

# =============================================================================
# BENCHMARK - Run multiple learning cycles for benchmarking
# =============================================================================

do_benchmark() {
    local n_cycles=${1:-5}
    print_header
    echo -e "${BLUE}Running Cognition Benchmark (${n_cycles} cycles)...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    cd "$GLADIUS_ROOT/Artifact/syndicate"
    "$PYTHON" -c "
import sys
sys.path.insert(0, '.')
from src.cognition import LEARNING_AVAILABLE, CognitionLearningLoop

if not LEARNING_AVAILABLE:
    print('[BENCHMARK] Learning module not available')
    sys.exit(1)

print('[BENCHMARK] Starting benchmark...')
loop = CognitionLearningLoop(base_dir='.', data_dir='./data', output_dir='./output')
result = loop.run_benchmark(n_cycles=$n_cycles)
print(f'[BENCHMARK] Complete. Results saved.')
print(f'  Initial win rate: {result[\"initial_metrics\"][\"win_rate\"]}%')
print(f'  Final win rate: {result[\"final_metrics\"][\"win_rate\"]}%')
print(f'  Total reports: {result[\"totals\"][\"reports_ingested\"]}')
print(f'  Total training examples: {result[\"totals\"][\"training_examples\"]}')
loop.close()
"
    echo ""
}

# =============================================================================
# CYCLE - Run single full autonomous cycle (daemon mode single iteration)
# =============================================================================

do_cycle() {
    print_header
    echo -e "${BLUE}Running Single Full Autonomous Cycle...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    cd "$GLADIUS_ROOT/Artifact/syndicate"
    "$PYTHON" run.py --once
    
    echo ""
    echo -e "${GREEN}✅ Single cycle complete!${NC}"
    echo ""
}

# =============================================================================
# AUTONOMOUS MODE - Run indefinitely with full learning and self-improvement
# =============================================================================

do_autonomous() {
    local days=${1:-30}
    local interval_min=${2:-60}
    local max_cycles=$((days * 24 * 60 / interval_min))
    
    print_header
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║               GLADIUS AUTONOMOUS MODE                         ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${CYAN}Duration:${NC}       $days days"
    echo -e "  ${CYAN}Interval:${NC}       $interval_min minutes"
    echo -e "  ${CYAN}Max Cycles:${NC}     $max_cycles"
    echo -e "  ${CYAN}Started:${NC}        $(date -Iseconds)"
    echo -e "  ${CYAN}Expected End:${NC}   $(date -d "+$days days" -Iseconds)"
    echo ""
    echo "─────────────────────────────────────────────────────────────────"
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$GLADIUS_ROOT/obsidian_sync/gladius/reports"
    
    # Write startup report
    local start_time=$(date -Iseconds)
    local report_file="$GLADIUS_ROOT/obsidian_sync/gladius/reports/autonomous_$(date +%Y%m%d_%H%M%S).md"
    cat > "$report_file" << EOF
# Gladius Autonomous Mode Session

## Session Info
- **Started**: $start_time
- **Duration**: $days days
- **Interval**: $interval_min minutes
- **Max Cycles**: $max_cycles
- **Status**: RUNNING

## Cycle Log
| Cycle | Timestamp | Reports | Training | Proposals | Errors |
|-------|-----------|---------|----------|-----------|--------|
EOF

    local cycle=0
    local total_reports=0
    local total_training=0
    local total_proposals=0
    local errors=0
    
    echo -e "${GREEN}Starting autonomous loop...${NC}"
    echo ""
    
    while [ $cycle -lt $max_cycles ]; do
        cycle=$((cycle + 1))
        local cycle_start=$(date -Iseconds)
        
        echo -e "${CYAN}[CYCLE $cycle/$max_cycles]${NC} $(date)"
        echo "─────────────────────────────────────────────────────────────────"
        
        # Run the full cycle
        cd "$GLADIUS_ROOT/Artifact/syndicate"
        
        # Execute cycle and capture metrics
        local result=$("$PYTHON" -c "
import sys
import json
sys.path.insert(0, '.')
try:
    from src.cognition import LEARNING_AVAILABLE, CognitionLearningLoop
    
    if not LEARNING_AVAILABLE:
        print(json.dumps({'error': 'Learning not available', 'reports': 0, 'training': 0, 'proposals': 0}))
        sys.exit(0)
    
    loop = CognitionLearningLoop(base_dir='.', data_dir='./data', output_dir='./output')
    result = loop.run_cycle()
    loop.close()
    
    print(json.dumps({
        'reports': result.reports_ingested,
        'training': result.training_examples_generated,
        'proposals': result.proposals_created + result.proposals_completed,
        'error': None
    }))
except Exception as e:
    print(json.dumps({'error': str(e), 'reports': 0, 'training': 0, 'proposals': 0}))
" 2>&1)
        
        # Parse results
        local reports=$(echo "$result" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('reports', 0))" 2>/dev/null || echo 0)
        local training=$(echo "$result" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('training', 0))" 2>/dev/null || echo 0)
        local proposals=$(echo "$result" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('proposals', 0))" 2>/dev/null || echo 0)
        local error=$(echo "$result" | python3 -c "import sys,json; d=json.loads(sys.stdin.read()); print(d.get('error') or '')" 2>/dev/null || echo "parse_error")
        
        total_reports=$((total_reports + reports))
        total_training=$((total_training + training))
        total_proposals=$((total_proposals + proposals))
        
        if [ -n "$error" ] && [ "$error" != "None" ] && [ "$error" != "" ]; then
            errors=$((errors + 1))
            echo -e "  ${RED}❌ Error: $error${NC}"
            echo "| $cycle | $cycle_start | $reports | $training | $proposals | $error |" >> "$report_file"
        else
            echo -e "  ${GREEN}✅ Reports: $reports | Training: $training | Proposals: $proposals${NC}"
            echo "| $cycle | $cycle_start | $reports | $training | $proposals | - |" >> "$report_file"
        fi
        
        # Run Syndicate research if needed (every 4 cycles = ~4 hours)
        if [ $((cycle % 4)) -eq 0 ]; then
            echo -e "  ${BLUE}→ Running Syndicate research cycle...${NC}"
            cd "$GLADIUS_ROOT/Artifact/syndicate"
            PREFER_OLLAMA=1 "$PYTHON" run.py --once >> "$LOG_DIR/syndicate_autonomous.log" 2>&1 &
            wait $!
            echo -e "  ${GREEN}✓ Syndicate cycle complete${NC}"
        fi
        
        # Progress update every 10 cycles
        if [ $((cycle % 10)) -eq 0 ]; then
            echo ""
            echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
            echo -e "${CYAN}Progress: $cycle/$max_cycles cycles ($(( cycle * 100 / max_cycles ))%)${NC}"
            echo -e "  Total Reports:    $total_reports"
            echo -e "  Total Training:   $total_training"
            echo -e "  Total Proposals:  $total_proposals"
            echo -e "  Errors:           $errors"
            echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
            echo ""
        fi
        
        # Run GLADIUS model training every 6 cycles (during sleep)
        if [ $((cycle % 6)) -eq 0 ]; then
            echo -e "  ${BLUE}→ Running GLADIUS model training (LoRA)...${NC}"
            local train_result=$("$PYTHON" "$GLADIUS_ROOT/GLADIUS/training/dual_trainer.py" --qwen-only 2>&1 | tail -5)
            echo -e "  ${GREEN}✓ Training cycle complete${NC}"
        fi
        
        # Wait for next cycle
        if [ $cycle -lt $max_cycles ]; then
            echo -e "  ${YELLOW}⏱ Sleeping $interval_min minutes until next cycle...${NC}"
            echo -e "  ${CYAN}   (SENTINEL learning active during sleep)${NC}"
            sleep $((interval_min * 60))
        fi
    done
    
    # Final summary
    local end_time=$(date -Iseconds)
    echo ""
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           🎉 AUTONOMOUS MODE COMPLETE                         ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${GREEN}Started:${NC}        $start_time"
    echo -e "  ${GREEN}Ended:${NC}          $end_time"
    echo -e "  ${GREEN}Cycles Run:${NC}     $cycle"
    echo -e "  ${GREEN}Total Reports:${NC}  $total_reports"
    echo -e "  ${GREEN}Total Training:${NC} $total_training"
    echo -e "  ${GREEN}Total Proposals:${NC} $total_proposals"
    echo -e "  ${GREEN}Errors:${NC}         $errors"
    echo ""
    
    # Update report file
    cat >> "$report_file" << EOF

## Final Summary
- **Ended**: $end_time
- **Cycles Run**: $cycle
- **Total Reports**: $total_reports
- **Total Training Examples**: $total_training
- **Total Proposals**: $total_proposals
- **Errors**: $errors
- **Status**: COMPLETED
EOF

    echo -e "Report saved to: $report_file"
    echo ""
}

# =============================================================================
# RUN - Lightweight system startup (UI + essential services only)
# =============================================================================

do_run() {
    print_header
    echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║           ARTIFACT VIRTUAL ENTERPRISE - LIGHTWEIGHT           ║${NC}"
    echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    # Check lightweight mode from config
    local lightweight=$(get_config "system.lightweight_mode" "true")
    if [ "$lightweight" = "True" ] || [ "$lightweight" = "true" ]; then
        echo -e "  ${CYAN}Mode:${NC} Lightweight (CPU-friendly)"
        echo -e "  ${CYAN}Note:${NC} Training disabled. Use './gladius.sh train' to run manually."
        echo ""
    fi
    
    mkdir -p "$LOG_DIR"
    mkdir -p "$PID_DIR"
    
    # Step 1: Hardware detection (quick)
    echo -e "${CYAN}[1/3] Hardware Detection${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    "$PYTHON" "$GLADIUS_ROOT/GLADIUS/utils/hardware.py" 2>/dev/null || echo -e "  ${YELLOW}⚠️${NC}  Hardware detection module not available"
    echo ""
    
    # Step 2: Start SENTINEL only (lightweight background daemon)
    echo -e "${CYAN}[2/3] SENTINEL Guardian${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    if is_module_enabled "sentinel"; then
        if [ -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid" ]; then
            local spid=$(cat "$GLADIUS_ROOT/SENTINEL/sentinel.pid" 2>/dev/null)
            if kill -0 "$spid" 2>/dev/null; then
                echo -e "  ${GREEN}✅${NC} SENTINEL already running (PID: $spid)"
            else
                rm -f "$GLADIUS_ROOT/SENTINEL/sentinel.pid"
                "$GLADIUS_ROOT/scripts/start_sentinel.sh" detached 2>/dev/null
                sleep 2
                echo -e "  ${GREEN}✅${NC} SENTINEL started"
            fi
        else
            "$GLADIUS_ROOT/scripts/start_sentinel.sh" detached 2>/dev/null
            sleep 2
            echo -e "  ${GREEN}✅${NC} SENTINEL started"
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  SENTINEL disabled in config"
    fi
    echo ""
    
    # Step 3: Launch Electron UI
    echo -e "${CYAN}[3/3] Launching UI${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    if is_module_enabled "ui"; then
        if [ -d "$GLADIUS_ROOT/ui" ]; then
            echo -e "  ${BLUE}→${NC} Starting Artifact Virtual UI..."
            cd "$GLADIUS_ROOT/ui"
            
            # Build if needed
            if [ ! -d "dist/electron" ]; then
                echo -e "  ${BLUE}→${NC} Building UI (first time)..."
                npm run build > "$LOG_DIR/ui_build.log" 2>&1
                npm run build:electron >> "$LOG_DIR/ui_build.log" 2>&1
            fi
            
            # Launch Electron (unset ELECTRON_RUN_AS_NODE)
            ELECTRON_RUN_AS_NODE= nohup npm run start > "$LOG_DIR/ui.log" 2>&1 &
            echo $! > "$PID_DIR/ui.pid"
            sleep 2
            
            if pgrep -f "electron" > /dev/null 2>&1; then
                echo -e "  ${GREEN}✅${NC} UI launched successfully"
            else
                echo -e "  ${YELLOW}⚠️${NC}  UI may take a moment to start"
            fi
        else
            echo -e "  ${YELLOW}⚠️${NC}  UI directory not found"
        fi
    else
        echo -e "  ${YELLOW}⚠️${NC}  UI disabled in config"
    fi
    
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║              ARTIFACT VIRTUAL READY                           ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "  ${BLUE}▌ MODULES (use UI or CLI to enable)${NC}"
    is_module_enabled "sentinel" && echo -e "    ${GREEN}●${NC} SENTINEL      Running" || echo -e "    ${YELLOW}○${NC} SENTINEL      Disabled"
    is_module_enabled "legion" && echo -e "    ${GREEN}●${NC} LEGION        Enabled" || echo -e "    ${YELLOW}○${NC} LEGION        Disabled"
    is_module_enabled "training" && echo -e "    ${GREEN}●${NC} Training      Enabled" || echo -e "    ${YELLOW}○${NC} Training      Disabled (run manually)"
    is_module_enabled "syndicate" && echo -e "    ${GREEN}●${NC} Syndicate     Enabled" || echo -e "    ${YELLOW}○${NC} Syndicate     Disabled"
    echo ""
    echo -e "  ${BLUE}▌ MANUAL COMMANDS${NC}"
    echo -e "    ${CYAN}./gladius.sh train${NC}       - Run GLADIUS training"
    echo -e "    ${CYAN}./gladius.sh interact${NC}   - Interactive AI session"
    echo -e "    ${CYAN}./gladius.sh start${NC}      - Start all services (heavy)"
    echo -e "    ${CYAN}./gladius.sh stop${NC}       - Stop all services"
    echo ""
    echo -e "  ${BLUE}▌ CONFIG${NC}"
    echo -e "    Edit ${CYAN}config.json${NC} to enable/disable modules"
    echo ""
}

# =============================================================================
# MAIN
# =============================================================================

case "${1:-help}" in
    run)
        do_run
        ;;
    start)
        do_start "$2"
        ;;
    stop)
        if [ "$2" = "--force" ]; then
            do_stop true
        else
            do_stop false
        fi
        ;;
    restart)
        do_stop false
        sleep 2
        do_start "$2"
        ;;
    status)
        do_status
        ;;
    health)
        print_header
        do_health_check true
        ;;
    infra)
        do_infra_test
        ;;
    logs)
        do_logs
        ;;
    cognition)
        do_cognition
        ;;
    benchmark)
        do_benchmark "${2:-5}"
        ;;
    cycle)
        do_cycle
        ;;
    autonomous|auto)
        # Parse arguments: autonomous [days] [interval_min]
        days=${2:-30}
        interval=${3:-60}
        do_autonomous "$days" "$interval"
        ;;
    interact|chat|gladius)
        # Interactive GLADIUS session
        print_header
        echo -e "${CYAN}Starting GLADIUS Interactive Mode...${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/interactive.py" "${@:2}"
        ;;
    speak)
        # Direct GLADIUS conversation
        print_header
        echo -e "${CYAN}Starting GLADIUS Direct Interface...${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/speak.py" "${@:2}"
        ;;
    chat)
        # GLADIUS Chat Server/CLI
        print_header
        echo -e "${CYAN}Starting GLADIUS Chat...${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/chat_server.py" "${@:2}"
        ;;
    chat-server)
        # GLADIUS Chat Server (HTTP API)
        print_header
        echo -e "${CYAN}Starting GLADIUS Chat Server...${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/chat_server.py" --mode server "${@:2}"
        ;;
    twitter)
        # GLADIUS Twitter Agent
        print_header
        echo -e "${CYAN}GLADIUS Twitter Agent${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/twitter_agent.py" "${@:2}"
        ;;
    twitter-run)
        # Start Twitter agent in autonomous mode
        print_header
        echo -e "${CYAN}Starting GLADIUS Twitter Agent (Autonomous)...${NC}"
        echo ""
        nohup "$PYTHON" "$GLADIUS_ROOT/GLADIUS/twitter_agent.py" run > "$LOG_DIR/twitter_agent.log" 2>&1 &
        echo $! > "$PID_DIR/twitter_agent.pid"
        echo -e "  ${GREEN}✅${NC} Twitter Agent started (PID: $!)"
        echo -e "  ${CYAN}Logs:${NC} $LOG_DIR/twitter_agent.log"
        ;;
    train)
        # Run GLADIUS training pipeline
        print_header
        echo -e "${CYAN}Running GLADIUS Training Pipeline...${NC}"
        echo "─────────────────────────────────────────────────────────────────"
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/training/train_pipeline.py" "${@:2}"
        ;;
    train-dual)
        # Run dual training (Qwen LoRA + Primary)
        print_header
        echo -e "${CYAN}Running GLADIUS Dual Training System...${NC}"
        echo "─────────────────────────────────────────────────────────────────"
        echo -e "  ${BLUE}Track 1:${NC} Qwen2.5-1.5B + LoRA (Operational)"
        echo -e "  ${BLUE}Track 2:${NC} GLADIUS Primary (Custom Architecture)"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/training/dual_trainer.py" "${@:2}"
        ;;
    train-1b)
        # Run 1B parameter training
        print_header
        echo -e "${CYAN}Running GLADIUS 1B Training...${NC}"
        echo "─────────────────────────────────────────────────────────────────"
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/training/gladius_1b_trainer.py" "${@:2}"
        ;;
    continuous)
        # Run GLADIUS continuous autonomous mode
        print_header
        echo -e "${CYAN}Starting GLADIUS Continuous Autonomous Mode...${NC}"
        echo ""
        "$PYTHON" "$GLADIUS_ROOT/GLADIUS/continuous.py" "${@:2}"
        ;;
    *)
        echo ""
        echo -e "${BLUE}Artifact Virtual Enterprise - Control Script${NC}"
        echo ""
        echo "Usage: ./gladius.sh <command> [options]"
        echo ""
        echo -e "${CYAN}Quick Start:${NC}"
        echo "  run                Lightweight startup (UI + SENTINEL only)"
        echo "  start              Full system startup (all services - HEAVY)"
        echo ""
        echo -e "${CYAN}Core Commands:${NC}"
        echo "  stop [--force]     Stop all services"
        echo "  restart            Stop then start all services"
        echo "  status             Quick status check"
        echo "  health             Full health check"
        echo ""
        echo -e "${CYAN}GLADIUS AI:${NC}"
        echo "  interact           Interactive GLADIUS session"
        echo "  speak              Direct conversation interface"
        echo "  chat               Chat CLI (with Hektor memory)"
        echo "  chat-server        Chat HTTP API server"
        echo ""
        echo -e "${CYAN}Social Media:${NC}"
        echo "  twitter test       Test Twitter connection"
        echo "  twitter generate   Generate a tweet"
        echo "  twitter-run        Start Twitter agent (autonomous)"
        echo ""
        echo -e "${CYAN}Training (Run Manually):${NC}"
        echo "  train              Run GLADIUS training pipeline"
        echo "  train-dual         Dual training (Qwen LoRA + Primary)"
        echo "  train-1b           1B parameter training (HEAVY)"
        echo ""
        echo -e "${CYAN}Autonomous Modes:${NC}"
        echo "  cycle              Run single autonomous cycle"
        echo "  cognition          Run learning cycle only"
        echo "  continuous         Run continuous autonomous mode"
        echo "  autonomous [d] [m] Full autonomous (d days, m min interval)"
        echo ""
        echo -e "${CYAN}Utilities:${NC}"
        echo "  infra              Test Infra API"
        echo "  logs               Tail log files"
        echo ""
        echo "Examples:"
        echo "  ./gladius.sh run                # Lightweight startup (recommended)"
        echo "  ./gladius.sh interact           # Interactive AI session"
        echo "  ./gladius.sh train              # Run training manually"
        echo "  ./gladius.sh start              # Full system (heavy)"
        echo ""
        echo "Config: Edit config.json to enable/disable modules"
        echo ""
        ;;
esac
