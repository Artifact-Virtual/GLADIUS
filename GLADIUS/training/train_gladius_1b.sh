#!/usr/bin/env bash
#
# GLADIUS 1B Parameter Continuous Trainer - Bash Wrapper
#
# Launches and manages the GLADIUS 1B training pipeline.
# Supports continuous training, status monitoring, and recovery.
#
# Usage:
#   ./train_gladius_1b.sh start [--hours N] [--batch-size N]
#   ./train_gladius_1b.sh status
#   ./train_gladius_1b.sh stop
#   ./train_gladius_1b.sh resume
#   ./train_gladius_1b.sh export
#
# Author: Artifact Virtual Systems

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TRAINER_SCRIPT="$SCRIPT_DIR/gladius_1b_trainer.py"
GLADIUS_ROOT="$(dirname "$(dirname "$(dirname "$SCRIPT_DIR")")")"
LOG_DIR="$GLADIUS_ROOT/logs/training"
PID_FILE="$LOG_DIR/trainer.pid"

# Defaults
HOURS=168
BASE_MODEL="Qwen/Qwen2.5-1.5B"
BATCH_SIZE=4

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

print_banner() {
    echo -e "${CYAN}"
    cat << 'EOF'

╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         G L A D I U S   1 B   T R A I N E R                  ║
║                                                              ║
║      Continuous Training Pipeline to 1 Billion Parameters   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

EOF
    echo -e "${NC}"
}

check_python() {
    if command -v python3 &> /dev/null; then
        echo -e "  ${GREEN}[OK]${NC} Python: $(python3 --version)"
        return 0
    elif command -v python &> /dev/null; then
        echo -e "  ${GREEN}[OK]${NC} Python: $(python --version)"
        return 0
    fi
    echo -e "  ${RED}[ERROR]${NC} Python not found"
    return 1
}

check_dependencies() {
    echo "Checking Dependencies..."
    
    local deps=("torch" "transformers" "peft" "accelerate" "datasets")
    local missing=()
    
    for dep in "${deps[@]}"; do
        if python3 -c "import $dep" 2>/dev/null; then
            echo -e "  ${GREEN}[OK]${NC} $dep"
        else
            echo -e "  ${YELLOW}[MISSING]${NC} $dep"
            missing+=("$dep")
        fi
    done
    
    if [ ${#missing[@]} -gt 0 ]; then
        echo ""
        echo "Installing missing dependencies..."
        pip install torch transformers peft accelerate datasets bitsandbytes --quiet
    fi
}

start_training() {
    echo "Starting GLADIUS 1B Training..."
    echo "  Max Hours: $HOURS"
    echo "  Base Model: $BASE_MODEL"
    echo "  Batch Size: $BATCH_SIZE"
    echo ""
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    LOG_FILE="$LOG_DIR/training_$(date +%Y%m%d_%H%M%S).log"
    
    # Start training in background
    nohup python3 "$TRAINER_SCRIPT" \
        --hours "$HOURS" \
        --base-model "$BASE_MODEL" \
        --batch-size "$BATCH_SIZE" \
        > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    echo -e "${GREEN}[STARTED]${NC} Training process PID: $pid"
    echo "  Log file: $LOG_FILE"
    echo ""
    echo "Monitor with: ./train_gladius_1b.sh status"
    echo "Stop with:    ./train_gladius_1b.sh stop"
    echo ""
    echo "Tail logs: tail -f $LOG_FILE"
}

get_status() {
    echo "Training Status"
    echo "─────────────────────────────────────────────"
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "  Process:     ${GREEN}RUNNING${NC} (PID: $pid)"
            local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null || echo "unknown")
            echo "  Started:     $start_time"
        else
            echo -e "  Process:     ${YELLOW}NOT RUNNING${NC}"
        fi
    else
        echo -e "  Process:     ${YELLOW}NOT STARTED${NC}"
    fi
    
    echo ""
    python3 "$TRAINER_SCRIPT" --status 2>/dev/null || true
}

stop_training() {
    echo "Stopping Training..."
    
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            # Send SIGTERM for graceful shutdown (saves checkpoint)
            kill -TERM "$pid" 2>/dev/null || true
            sleep 2
            
            # Force kill if still running
            if ps -p "$pid" > /dev/null 2>&1; then
                kill -9 "$pid" 2>/dev/null || true
            fi
            echo -e "  ${GREEN}[STOPPED]${NC} Process $pid terminated"
        else
            echo -e "  ${YELLOW}[INFO]${NC} Process already stopped"
        fi
        rm -f "$PID_FILE"
    else
        echo -e "  ${YELLOW}[INFO]${NC} No training process found"
    fi
}

resume_training() {
    echo "Resuming Training from Checkpoint..."
    
    # Stop any existing process
    stop_training
    
    # Create log directory
    mkdir -p "$LOG_DIR"
    
    LOG_FILE="$LOG_DIR/training_resume_$(date +%Y%m%d_%H%M%S).log"
    
    # Start with resume
    nohup python3 "$TRAINER_SCRIPT" \
        --resume \
        --hours "$HOURS" \
        > "$LOG_FILE" 2>&1 &
    
    local pid=$!
    echo "$pid" > "$PID_FILE"
    
    echo -e "${GREEN}[RESUMED]${NC} Training process PID: $pid"
}

export_model() {
    echo "Exporting Model to GGUF..."
    python3 "$TRAINER_SCRIPT" --export-only
}

show_help() {
    cat << 'EOF'
GLADIUS 1B Trainer - Commands
─────────────────────────────────────────────

  start     Start continuous training
  status    Show current training status  
  stop      Stop training (saves checkpoint)
  resume    Resume from last checkpoint
  export    Export trained model to GGUF

Options:
  --hours N       Maximum training hours (default: 168)
  --base-model M  Base model (default: Qwen/Qwen2.5-1.5B)
  --batch-size N  Training batch size (default: 4)

Examples:
  ./train_gladius_1b.sh start
  ./train_gladius_1b.sh --hours 48 start
  ./train_gladius_1b.sh status
  ./train_gladius_1b.sh stop

EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --hours)
            HOURS="$2"
            shift 2
            ;;
        --base-model)
            BASE_MODEL="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        start|status|stop|resume|export|help)
            ACTION="$1"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Default action
ACTION="${ACTION:-help}"

# Main
print_banner

if ! check_python; then
    exit 1
fi

case "$ACTION" in
    start)
        check_dependencies
        start_training
        ;;
    status)
        get_status
        ;;
    stop)
        stop_training
        ;;
    resume)
        check_dependencies
        resume_training
        ;;
    export)
        export_model
        ;;
    help)
        show_help
        ;;
esac
