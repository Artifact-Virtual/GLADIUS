#!/bin/bash
#
# GLADIUS Training Script
# =======================
#
# Starts GLADIUS training with automatic CPU/GPU detection.
# Uses unified trainer with shared checkpoints.
#
# Usage:
#   ./start_gladius_training.sh                    # Auto-detect settings
#   ./start_gladius_training.sh --params 150      # Train 150M model
#   ./start_gladius_training.sh --epochs 10       # 10 epochs
#   ./start_gladius_training.sh --resume          # Resume from checkpoint
#   ./start_gladius_training.sh --export-gguf     # Export GGUF after training
#
# Author: Artifact Virtual Systems

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLADIUS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_ROOT="$(dirname "$GLADIUS_DIR")"

# Try different venv locations
if [[ -f "$GLADIUS_DIR/training_venv/bin/python" ]]; then
    VENV_PYTHON="$GLADIUS_DIR/training_venv/bin/python"
elif [[ -f "$GLADIUS_DIR/tmp/venv/bin/python" ]]; then
    VENV_PYTHON="$GLADIUS_DIR/tmp/venv/bin/python"
else
    VENV_PYTHON="python3"
fi

TRAINER_SCRIPT="$SCRIPT_DIR/gladius_trainer.py"
LOG_DIR="$GLADIUS_DIR/tmp"

# Defaults
PARAMS=""
EPOCHS=3
RESUME=false
EXPORT_GGUF=false
FORCE_CPU=false
FORCE_GPU=false

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m'

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --params|-p)
            PARAMS="$2"
            shift 2
            ;;
        --epochs|-e)
            EPOCHS="$2"
            shift 2
            ;;
        --resume|-r)
            RESUME=true
            shift
            ;;
        --export-gguf)
            EXPORT_GGUF=true
            shift
            ;;
        --cpu)
            FORCE_CPU=true
            shift
            ;;
        --gpu)
            FORCE_GPU=true
            shift
            ;;
        --help|-h)
            echo "GLADIUS Training Script"
            echo ""
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --params, -p M    Target parameters in millions (auto if not set)"
            echo "  --epochs, -e N    Training epochs (default: 3)"
            echo "  --resume, -r      Resume from checkpoint"
            echo "  --export-gguf     Export GGUF after training"
            echo "  --cpu             Force CPU training"
            echo "  --gpu             Force GPU training"
            echo "  --help, -h        Show this help"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Banner
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}${WHITE}                    GLADIUS UNIFIED TRAINER                      ${NC}${CYAN}║${NC}"
echo -e "${CYAN}║${NC}${WHITE}            Automatic CPU/GPU · Shared Checkpoints               ${NC}${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
if [[ ! -f "$TRAINER_SCRIPT" ]]; then
    echo -e "  ${RED}ERROR: Trainer script not found at $TRAINER_SCRIPT${NC}"
    exit 1
fi

# Ensure log directory exists
mkdir -p "$LOG_DIR"

# Build command
CMD="$VENV_PYTHON $TRAINER_SCRIPT --epochs $EPOCHS"

if [[ -n "$PARAMS" ]]; then
    CMD="$CMD --params $PARAMS"
fi

if $RESUME; then
    CMD="$CMD --resume"
fi

if $EXPORT_GGUF; then
    CMD="$CMD --export-gguf"
fi

if $FORCE_CPU; then
    CMD="$CMD --force-cpu"
fi

if $FORCE_GPU; then
    CMD="$CMD --force-gpu"
fi

echo -e "  ${CYAN}Python:${NC}  $VENV_PYTHON"
echo -e "  ${CYAN}Epochs:${NC}  $EPOCHS"
echo -e "  ${CYAN}Params:${NC}  ${PARAMS:-auto}"
echo -e "  ${CYAN}Resume:${NC}  $RESUME"
echo -e "  ${CYAN}Export:${NC}  $EXPORT_GGUF"
echo ""
echo -e "  ${YELLOW}Press Ctrl+C to stop training (checkpoint will be saved)${NC}"
echo ""

# Handle Ctrl+C gracefully
trap 'echo ""; echo -e "  ${YELLOW}Training interrupted - checkpoint saved${NC}"; exit 0' INT TERM

# Run training
exec $CMD
