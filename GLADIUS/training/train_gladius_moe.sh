#!/usr/bin/env bash
#
# GLADIUS Multi-Expert Training Pipeline
# ========================================
# Distills knowledge from Qwen + Llama + Phi + Gemma into GLADIUS
#
# Usage:
#   ./train_gladius_moe.sh           # Full training (72 hours max)
#   ./train_gladius_moe.sh 24        # Custom time limit (hours)
#   ./train_gladius_moe.sh status    # Check status
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                      ║${NC}"
echo -e "${CYAN}║          G L A D I U S   M U L T I - E X P E R T   T R A I N E R    ║${NC}"
echo -e "${CYAN}║                                                                      ║${NC}"
echo -e "${CYAN}║     Building 1B Parameter Model with Custom Weights                  ║${NC}"
echo -e "${CYAN}║     Expert Teachers: Qwen + Llama + Phi + Gemma                      ║${NC}"
echo -e "${CYAN}║                                                                      ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Parse arguments
HOURS=72
ACTION="train"

if [ "$1" = "status" ]; then
    ACTION="status"
elif [ "$1" = "help" ] || [ "$1" = "-h" ]; then
    echo -e "${YELLOW}Usage:${NC}"
    echo "  ./train_gladius_moe.sh           # Full training (72h max)"
    echo "  ./train_gladius_moe.sh 24        # Custom time limit (hours)"
    echo "  ./train_gladius_moe.sh status    # Check training status"
    echo ""
    echo -e "${YELLOW}Expert Teachers:${NC}"
    echo "  - Qwen2.5-1.5B:  Tool-calling, structured output"
    echo "  - Llama-3.2-1B:  Reasoning, fluency"
    echo "  - Phi-3-mini:    Mathematics, code"
    echo "  - Gemma-2-2b:    Safety, instruction following"
    exit 0
elif [ -n "$1" ]; then
    HOURS=$1
fi

# Setup venv
VENV_PATH="${SCRIPT_DIR}/.venv"
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Creating training virtual environment...${NC}"
    python3 -m venv "$VENV_PATH"
fi

# Activate and use venv python
source "${VENV_PATH}/bin/activate" 2>/dev/null || true
PYTHON="${VENV_PATH}/bin/python"
if [ ! -f "$PYTHON" ]; then
    PYTHON="python3"
fi

# Run
if [ "$ACTION" = "status" ]; then
    echo -e "${YELLOW}Checking training status...${NC}"
    $PYTHON "${SCRIPT_DIR}/gladius_moe_trainer.py" --status
else
    echo -e "${GREEN}Starting GLADIUS Multi-Expert Training${NC}"
    echo -e "  Time limit: ${HOURS} hours"
    echo -e "  Project root: ${PROJECT_ROOT}"
    echo ""
    
    $PYTHON "${SCRIPT_DIR}/gladius_moe_trainer.py" --hours "$HOURS"
fi

echo ""
echo -e "${CYAN}Training session ended.${NC}"
