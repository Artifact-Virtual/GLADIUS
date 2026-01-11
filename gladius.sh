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

GLADIUS_ROOT="/home/adam/worxpace/gladius"
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
    echo -e "${BLUE}║           ⚔️  GLADIUS CONTROL CENTER                          ║${NC}"
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

    # Web UI (5002) - template server
    if check_http "http://127.0.0.1:5002/api/status"; then
        local time=$(get_response_time "http://127.0.0.1:5002/api/status")
        echo -e "  ${GREEN}✅${NC} Web UI (5002)       ${GREEN}OK${NC}  [${time}s]"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Web UI (5002)       ${YELLOW}NOT RUNNING${NC}"
        all_ok=false
    fi
    
    # Frontend (3000) - optional
    if check_port 3000; then
        echo -e "  ${GREEN}✅${NC} Frontend (3000)      ${GREEN}OK${NC}"
    else
        echo -e "  ${YELLOW}⚠️${NC}  Frontend (3000)      ${YELLOW}NOT RUNNING${NC} (optional)"
    fi
    
    # Syndicate Daemon
    if pgrep -f "run.py.*--daemon" > /dev/null 2>&1; then
        local pid=$(pgrep -f "run.py.*--daemon")
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
    echo -e "${CYAN}[2/7] Dashboard Backend${NC}"
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

    # 3. Start Web UI (template server)
    echo -e "${CYAN}[3/7] Web UI${NC}"
    WEB_UI_PORT=${WEB_UI_PORT:-5002}
    if check_port "$WEB_UI_PORT"; then
        echo -e "  ${YELLOW}⚠️${NC}  Web UI already running on port $WEB_UI_PORT"
    else
        echo -e "  ${BLUE}→${NC} Starting Web UI on port $WEB_UI_PORT..."
        cd "$GLADIUS_ROOT/Artifact/deployment/automata/dashboard/frontend/web_ui"
        nohup env WEB_UI_PORT="$WEB_UI_PORT" "$PYTHON" start.py > "$LOG_DIR/web_ui.log" 2>&1 &
        echo $! > "$PID_DIR/web_ui.pid"
        sleep 2
        if check_http "http://127.0.0.1:${WEB_UI_PORT}/api/status"; then
            echo -e "  ${GREEN}✅${NC} Web UI started on port $WEB_UI_PORT"
        else
            echo -e "  ${YELLOW}⚠️${NC} Web UI may take a moment to start"
        fi
    fi

    # 4. Start Grafana (via Docker)
    echo -e "${CYAN}[4/7] Grafana${NC}"
    if check_port 3001; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 3001"
    elif ! command -v docker &> /dev/null; then
        echo -e "  ${YELLOW}⚠️${NC}  Docker not available - skipping Grafana"
    else
        echo -e "  ${BLUE}→${NC} Starting Grafana via Docker..."
        cd "$GLADIUS_ROOT/Artifact/syndicate/docker"
        # Modify grafana to use port 3001 to avoid conflict with frontend
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
    echo -e "${CYAN}[5/7] Prometheus${NC}"
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

    # 6. Start Dashboard Frontend (React)
    echo -e "${CYAN}[6/7] Dashboard Frontend${NC}"
    if check_port 3000; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running on port 3000"
    else
        echo -e "  ${BLUE}→${NC} Starting React Dashboard..."
        cd "$GLADIUS_ROOT/Artifact/deployment/automata/dashboard/frontend"
        nohup npm run dev > "$LOG_DIR/frontend_dev.log" 2>&1 &
        echo $! > "$PID_DIR/frontend_dev.pid"
        sleep 3
        if check_port 3000; then
            echo -e "  ${GREEN}✅${NC} Started on port 3000"
        else
            echo -e "  ${YELLOW}⚠️${NC}  May take a moment to start (check logs)"
        fi
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
        # Modify grafana to use port 3001 to avoid conflict with frontend
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
    echo -e "${CYAN}[6/6] Syndicate Daemon${NC}"
    if pgrep -f "run.py.*--daemon" > /dev/null 2>&1; then
        echo -e "  ${YELLOW}⚠️${NC}  Already running"
    else
        echo -e "  ${BLUE}→${NC} Starting Syndicate Daemon..."
        cd "$GLADIUS_ROOT/Artifact/syndicate"
        nohup env PREFER_OLLAMA=1 "$PYTHON" run.py --daemon > "$LOG_DIR/syndicate_daemon.log" 2>&1 &
        echo $! > "$PID_DIR/syndicate_daemon.pid"
        sleep 2
        echo -e "  ${GREEN}✅${NC} Daemon started"
    fi
    
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # Run health check
    echo -e "${BLUE}Running Health Check...${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    sleep 2
    do_health_check
    
    echo ""
    echo -e "${GREEN}🚀 Gladius Ready!${NC}"
    echo ""
    echo "   Access Points:"
    echo "   ─────────────────────────────────────────────"
    echo -e "   ${GREEN}Dashboard UI${NC}:     http://localhost:3000     (React)"
    echo -e "   ${GREEN}Web UI${NC}:           http://localhost:5002     (Flask templates)"
    echo -e "   ${GREEN}Infra API Docs${NC}:  http://localhost:7000/docs (FastAPI)"
    echo -e "   ${GREEN}Dashboard API${NC}:   http://localhost:5000      (Flask)"
    if check_port 3001; then
        echo -e "   ${GREEN}Grafana${NC}:         http://localhost:3001      (admin/admin)"
    fi
    if check_port 9090; then
        echo -e "   ${GREEN}Prometheus${NC}:      http://localhost:9090"
    fi
    echo ""
    echo "   Logs: tail -f $LOG_DIR/*.log"
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
    
    # Stop Frontend (3000)
    echo -e "${CYAN}[1/6] Dashboard Frontend${NC}"
    local pid=$(lsof -t -i:3000 2>/dev/null)
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

    # Stop Web UI (5002)
    echo -e "${CYAN}[3/7] Web UI${NC}"
    WEB_UI_PORT=${WEB_UI_PORT:-5002}
    pid=$(lsof -t -i:$WEB_UI_PORT 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi

    # Stop Infra API (7000)
    echo -e "${CYAN}[4/7] Infra API${NC}"
    pid=$(lsof -t -i:7000 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Grafana (Docker)
    echo -e "${CYAN}[4/6] Grafana${NC}"
    if docker ps -q -f name=gold_grafana 2>/dev/null | grep -q .; then
        docker stop gold_grafana > /dev/null 2>&1
        docker rm gold_grafana > /dev/null 2>&1
        echo -e "  ${GREEN}✅${NC} Stopped Grafana container"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Prometheus (Docker)
    echo -e "${CYAN}[5/6] Prometheus${NC}"
    if docker ps -q -f name=gold_prometheus 2>/dev/null | grep -q .; then
        docker stop gold_prometheus > /dev/null 2>&1
        docker rm gold_prometheus > /dev/null 2>&1
        echo -e "  ${GREEN}✅${NC} Stopped Prometheus container"
    else
        echo -e "  ${YELLOW}─${NC}  Not running"
    fi
    
    # Stop Syndicate Daemon
    echo -e "${CYAN}[6/6] Syndicate Daemon${NC}"
    pid=$(pgrep -f "run.py.*--daemon" 2>/dev/null)
    if [ -n "$pid" ]; then
        if [ "$force" = true ]; then kill -9 $pid 2>/dev/null; else kill $pid 2>/dev/null; fi
        echo -e "  ${GREEN}✅${NC} Stopped (PID: $pid)"
    else
        echo -e "  ${YELLOW}─${NC}  Syndicate Daemon was not running"
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
    
    if check_port 3000; then
        echo -e "  ${YELLOW}○${NC} Port 3000 still in use (may be another service)"
    else
        echo -e "  ${GREEN}✓${NC} Port 3000 clear"
    fi

    if check_port 5002; then
        echo -e "  ${RED}⚠️${NC}  Port 5002 still in use"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Port 5002 clear"
    fi
    
    if pgrep -f "run.py.*--daemon" > /dev/null 2>&1; then
        echo -e "  ${RED}⚠️${NC}  Syndicate daemon still running"
        remaining=$((remaining + 1))
    else
        echo -e "  ${GREEN}✓${NC} Syndicate daemon stopped"
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
    echo -e "${CYAN}Gladius Quick Status - $(date)${NC}"
    echo "─────────────────────────────────────────────────────────────────"
    
    # Quick port checks
    check_port 7000 && echo -e "  ${GREEN}●${NC} Infra API (7000)" || echo -e "  ${RED}○${NC} Infra API (7000)"
    check_port 5000 && echo -e "  ${GREEN}●${NC} Dashboard API (5000)" || echo -e "  ${RED}○${NC} Dashboard API (5000)"
    check_port 3000 && echo -e "  ${GREEN}●${NC} Dashboard UI (3000)" || echo -e "  ${YELLOW}○${NC} Dashboard UI (3000)"
    check_port 5002 && echo -e "  ${GREEN}●${NC} Web UI (5002)" || echo -e "  ${YELLOW}○${NC} Web UI (5002)"
    check_port 3001 && echo -e "  ${GREEN}●${NC} Grafana (3001)" || echo -e "  ${YELLOW}○${NC} Grafana (3001)"
    check_port 9090 && echo -e "  ${GREEN}●${NC} Prometheus (9090)" || echo -e "  ${YELLOW}○${NC} Prometheus (9090)"
    pgrep -f "run.py.*--daemon" > /dev/null 2>&1 && echo -e "  ${GREEN}●${NC} Syndicate Daemon" || echo -e "  ${YELLOW}○${NC} Syndicate Daemon"
    
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
# MAIN
# =============================================================================

case "${1:-help}" in
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
    *)
        echo ""
        echo -e "${BLUE}⚔️  Gladius Control Script${NC}"
        echo ""
        echo "Usage: ./gladius.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  start              Start all services + health check"
        echo "  stop [--force]     Stop all services + regression check"
        echo "  restart            Stop then start all services"
        echo "  status             Quick status check (all 6 services)"
        echo "  health             Full health check with endpoint tests"
        echo "  infra              Test Infra API specifically"
        echo "  logs               Tail all log files"
        echo ""
        echo "Services Started:"
        echo "  • Infra API (7000)      - Market data, assets, portfolios"
        echo "  • Dashboard Backend (5000) - Automata control, content"
        echo "  • Web UI (5002)         - Template-based UI and charts"
        echo "  • Dashboard Frontend (3000) - React UI"
        echo "  • Grafana (3001)        - Metrics dashboards (Docker)"
        echo "  • Prometheus (9090)     - Metrics collection (Docker)"
        echo "  • Syndicate Daemon      - Market intelligence (background)"
        echo ""
        echo "Examples:"
        echo "  ./gladius.sh start      # Start all services"
        echo "  ./gladius.sh stop       # Stop all services"
        echo "  ./gladius.sh status     # Quick port check"
        echo ""
        ;;
esac
