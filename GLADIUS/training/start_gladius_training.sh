#!/bin/bash
#
# GLADIUS Continuous Training Script
# ===================================
#
# Starts GLADIUS training that runs indefinitely until manually stopped.
# Displays live growth dashboard showing progress, loss curves, and milestones.
#
# Usage:
#   ./start_gladius_training.sh                    # Indefinite training
#   ./start_gladius_training.sh --hours 24         # Train for 24 hours
#   ./start_gladius_training.sh --steps 5000       # 5000 steps per expert
#   ./start_gladius_training.sh --status           # Show status only
#
# Author: Artifact Virtual Systems
# Date: 2026-01-15

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLADIUS_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$GLADIUS_DIR/tmp/venv/bin/python"
TRAINER_SCRIPT="$GLADIUS_DIR/training/gladius_moe_trainer.py"
GROWTH_TRACKER="$GLADIUS_DIR/growth/growth_tracker.py"
LOG_DIR="$GLADIUS_DIR/tmp/logs"
STATE_FILE="$GLADIUS_DIR/tmp/checkpoints/moe_training_state.json"

# Defaults
HOURS=0
STEPS=1000
DASHBOARD=true
STATUS_ONLY=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
DIM='\033[2m'
NC='\033[0m'

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --hours|-h)
            HOURS="$2"
            shift 2
            ;;
        --steps|-s)
            STEPS="$2"
            shift 2
            ;;
        --no-dashboard)
            DASHBOARD=false
            shift
            ;;
        --status)
            STATUS_ONLY=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Banner
show_banner() {
    echo ""
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}${WHITE}                                                                          ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}${WHITE}             G L A D I U S   C O N T I N U O U S   T R A I N I N G        ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}${WHITE}                                                                          ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}${WHITE}         Multi-Expert Knowledge Distillation · Live Dashboard             ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}║${NC}${WHITE}                                                                          ${NC}${CYAN}║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════╝${NC}"
    echo ""
}

# Show status
show_status() {
    if [[ -f "$STATE_FILE" ]]; then
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
        echo -e "${WHITE}                    GLADIUS TRAINING STATUS${NC}"
        echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
        echo ""
        
        local status=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('status','unknown'))")
        local phase=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('phase',0))")
        local experts=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(','.join(d.get('experts_completed',[])))")
        local step=$(python3 -c "import json; d=json.load(open('$STATE_FILE')); print(d.get('step',0))")
        
        case "$status" in
            completed) color="${GREEN}" ;;
            training)  color="${YELLOW}" ;;
            failed)    color="${RED}" ;;
            *)         color="${DIM}" ;;
        esac
        
        echo -e "  Status:           ${color}${status^^}${NC}"
        echo -e "  Phase:            $phase/6"
        echo -e "  Step:             $step"
        echo -e "  Experts Done:     $experts"
        echo ""
        
        # Loss info
        python3 -c "
import json
d = json.load(open('$STATE_FILE'))
loss = d.get('loss_history', [])
if loss:
    first = round(loss[0], 4)
    last = round(loss[-1], 4)
    reduction = round((1 - last / first) * 100, 1) if first > 0 else 0
    print(f'  Initial Loss:     {first}')
    print(f'  Current Loss:     {last}')
    print(f'  Loss Reduction:   {reduction}%')
" 2>/dev/null || true
        
        echo ""
    else
        echo -e "  ${YELLOW}No training state found. Training has not started.${NC}"
        echo ""
    fi
}

# Update trainer config
update_trainer_config() {
    local steps=$1
    sed -i "s/max_steps_per_expert:\s*int\s*=\s*[0-9]*/max_steps_per_expert: int = $steps/" "$TRAINER_SCRIPT"
    echo -e "  ${GREEN}Updated steps per expert: $steps${NC}"
}

# Main training loop
start_training() {
    local start_time=$(date +%s)
    local end_time=0
    
    if [[ $HOURS -gt 0 ]]; then
        end_time=$((start_time + HOURS * 3600))
    fi
    
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${WHITE}                    STARTING GLADIUS TRAINING${NC}"
    echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  Duration:         $(if [[ $HOURS -eq 0 ]]; then echo 'Indefinite'; else echo "$HOURS hours"; fi)"
    echo -e "  Steps/Expert:     $STEPS"
    echo -e "  Dashboard:        $(if $DASHBOARD; then echo 'Enabled'; else echo 'Disabled'; fi)"
    echo -e "  Python:           $VENV_PYTHON"
    echo ""
    echo -e "  ${YELLOW}Press Ctrl+C to stop training (checkpoint will be saved)${NC}"
    echo ""
    
    # Update trainer config
    update_trainer_config $STEPS
    
    local cycle=0
    
    # Handle Ctrl+C gracefully
    trap 'echo ""; echo -e "  ${YELLOW}Training interrupted${NC}"; show_status; exit 0' INT TERM
    
    while true; do
        cycle=$((cycle + 1))
        local cycle_start=$(date +%s)
        
        # Check time limit
        if [[ $end_time -gt 0 ]] && [[ $(date +%s) -gt $end_time ]]; then
            echo ""
            echo -e "  ${GREEN}Time limit reached. Training complete.${NC}"
            break
        fi
        
        echo ""
        echo -e "${DIM}─────────────────────────────────────────────────────────────────────────${NC}"
        echo -e "  ${YELLOW}TRAINING CYCLE $cycle - $(date '+%Y-%m-%d %H:%M:%S')${NC}"
        echo -e "${DIM}─────────────────────────────────────────────────────────────────────────${NC}"
        
        # Clear previous state for new cycle
        if [[ $cycle -gt 1 ]] && [[ -f "$STATE_FILE" ]]; then
            rm -f "$STATE_FILE"
        fi
        
        # Start training
        local log_file="$LOG_DIR/training_cycle_${cycle}_$(date '+%Y%m%d_%H%M%S').log"
        
        if $DASHBOARD; then
            # Run training in background, show dashboard
            "$VENV_PYTHON" "$TRAINER_SCRIPT" > "$log_file" 2>&1 &
            local train_pid=$!
            
            # Monitor with dashboard updates
            while kill -0 $train_pid 2>/dev/null; do
                sleep 10
                
                if [[ -f "$STATE_FILE" ]]; then
                    clear
                    show_banner
                    "$VENV_PYTHON" "$GROWTH_TRACKER" 2>/dev/null || true
                fi
                
                # Check time limit
                if [[ $end_time -gt 0 ]] && [[ $(date +%s) -gt $end_time ]]; then
                    kill $train_pid 2>/dev/null || true
                    echo -e "  ${YELLOW}Time limit reached. Stopping...${NC}"
                    break
                fi
            done
            
            wait $train_pid 2>/dev/null || true
        else
            # Run training in foreground
            "$VENV_PYTHON" "$TRAINER_SCRIPT" 2>&1 | tee "$log_file"
        fi
        
        local cycle_end=$(date +%s)
        local cycle_duration=$(( (cycle_end - cycle_start) / 60 ))
        
        echo ""
        echo -e "  ${GREEN}Cycle $cycle completed in $cycle_duration minutes${NC}"
        
        # Brief pause between cycles
        echo -e "  ${DIM}Starting next cycle in 5 seconds...${NC}"
        sleep 5
    done
}

# Main execution
show_banner

if $STATUS_ONLY; then
    show_status
    exit 0
fi

# Check prerequisites
if [[ ! -f "$VENV_PYTHON" ]]; then
    echo -e "  ${RED}ERROR: Python venv not found at $VENV_PYTHON${NC}"
    echo -e "  ${YELLOW}Run: python3 -m venv $GLADIUS_DIR/tmp/venv${NC}"
    exit 1
fi

if [[ ! -f "$TRAINER_SCRIPT" ]]; then
    echo -e "  ${RED}ERROR: Trainer script not found at $TRAINER_SCRIPT${NC}"
    exit 1
fi

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Start training
start_training

echo ""
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
echo -e "${WHITE}                    TRAINING SESSION ENDED${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════════════${NC}"
echo ""

show_status
