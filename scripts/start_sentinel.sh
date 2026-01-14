#!/bin/bash
#
# SENTINEL Startup Script
# =======================
#
# Starts the SENTINEL watchdog with all managed daemons.
#
# Usage:
#   ./start_sentinel.sh          - Start in foreground
#   ./start_sentinel.sh detached - Start as background daemon
#   ./start_sentinel.sh stop     - Stop with password
#   ./start_sentinel.sh status   - Check status
#
# Author: Artifact Virtual Systems
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLADIUS_ROOT="$(dirname "$SCRIPT_DIR")"
SENTINEL_DIR="$GLADIUS_ROOT/SENTINEL"
LOG_DIR="$SENTINEL_DIR/logs"
PID_FILE="$SENTINEL_DIR/sentinel.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Create log directory
mkdir -p "$LOG_DIR"

# Load environment
if [ -f "$GLADIUS_ROOT/.env" ]; then
    export $(grep -E '^SENTINEL_' "$GLADIUS_ROOT/.env" | xargs)
fi

# Set kill password hash if not set
if [ -z "$SENTINEL_KILL_PASSWORD" ]; then
    export SENTINEL_KILL_PASSWORD="bacaf2c00e6271497158bcd42f2c49fc5d10f0a82d24b2dd6389c03be3121583"
fi

start_foreground() {
    echo -e "${GREEN}Starting SENTINEL Watchdog...${NC}"
    cd "$SENTINEL_DIR"
    python3 services/watchdog.py start
}

start_detached() {
    echo -e "${GREEN}Starting SENTINEL Watchdog (detached)...${NC}"
    
    # Check if already running
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        echo -e "${YELLOW}SENTINEL already running (PID: $(cat $PID_FILE))${NC}"
        exit 1
    fi
    
    cd "$SENTINEL_DIR"
    
    # Start watchdog in background
    nohup python3 services/watchdog.py start > "$LOG_DIR/watchdog.log" 2>&1 &
    WATCHDOG_PID=$!
    
    echo "$WATCHDOG_PID" > "$PID_FILE"
    
    sleep 2
    
    if kill -0 "$WATCHDOG_PID" 2>/dev/null; then
        echo -e "${GREEN}✅ SENTINEL started successfully (PID: $WATCHDOG_PID)${NC}"
        echo -e "   Logs: $LOG_DIR/watchdog.log"
        echo -e "   PID file: $PID_FILE"
    else
        echo -e "${RED}❌ SENTINEL failed to start${NC}"
        cat "$LOG_DIR/watchdog.log"
        exit 1
    fi
}

stop_sentinel() {
    echo -e "${YELLOW}Stopping SENTINEL...${NC}"
    
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}No PID file found - SENTINEL may not be running${NC}"
        exit 0
    fi
    
    PID=$(cat "$PID_FILE")
    
    # Request password
    if [ -z "$1" ]; then
        read -s -p "Kill password: " KILL_PASSWORD
        echo
    else
        KILL_PASSWORD="$1"
    fi
    
    # Verify password
    PROVIDED_HASH=$(echo -n "$KILL_PASSWORD" | sha256sum | cut -d' ' -f1)
    if [ "$PROVIDED_HASH" != "$SENTINEL_KILL_PASSWORD" ]; then
        echo -e "${RED}❌ Invalid password${NC}"
        exit 1
    fi
    
    # Kill the process
    if kill -TERM "$PID" 2>/dev/null; then
        echo -e "${GREEN}✅ SENTINEL stopped (PID: $PID)${NC}"
        rm -f "$PID_FILE"
    else
        echo -e "${YELLOW}Process $PID not running${NC}"
        rm -f "$PID_FILE"
    fi
}

check_status() {
    echo -e "═══════════════════════════════════════════════"
    echo -e "          SENTINEL STATUS"
    echo -e "═══════════════════════════════════════════════"
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "  Watchdog:       ${GREEN}RUNNING${NC} (PID: $PID)"
        else
            echo -e "  Watchdog:       ${RED}DEAD${NC} (stale PID: $PID)"
        fi
    else
        echo -e "  Watchdog:       ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Check learning daemon
    if pgrep -f "learning_daemon.py" > /dev/null; then
        echo -e "  Learning Daemon: ${GREEN}RUNNING${NC}"
    else
        echo -e "  Learning Daemon: ${YELLOW}NOT RUNNING${NC}"
    fi
    
    # Show latest heartbeat
    HEARTBEAT_FILE="$SENTINEL_DIR/services/watchdog_heartbeat.log"
    if [ -f "$HEARTBEAT_FILE" ]; then
        LAST_HEARTBEAT=$(tail -1 "$HEARTBEAT_FILE" 2>/dev/null)
        if [ -n "$LAST_HEARTBEAT" ]; then
            echo -e ""
            echo -e "  Last heartbeat: $LAST_HEARTBEAT" | head -c 80
            echo ""
        fi
    fi
    
    echo -e "═══════════════════════════════════════════════"
}

run_tests() {
    echo -e "${GREEN}Running SENTINEL regression tests...${NC}"
    cd "$GLADIUS_ROOT"
    SENTINEL_KILL_PASSWORD="$SENTINEL_KILL_PASSWORD" python3 SENTINEL/tests/test_sentinel.py
}

# Main
case "${1:-foreground}" in
    foreground|start)
        start_foreground
        ;;
    detached|daemon|background)
        start_detached
        ;;
    stop)
        stop_sentinel "$2"
        ;;
    status)
        check_status
        ;;
    test|tests)
        run_tests
        ;;
    restart)
        stop_sentinel "$2" || true
        sleep 2
        start_detached
        ;;
    *)
        echo "Usage: $0 {start|detached|stop|status|test|restart}"
        echo ""
        echo "Commands:"
        echo "  start    - Start in foreground"
        echo "  detached - Start as background daemon"
        echo "  stop     - Stop with password"
        echo "  status   - Check status"
        echo "  test     - Run regression tests"
        echo "  restart  - Stop and start"
        exit 1
        ;;
esac
