#!/bin/bash
# ARTIFACT QWEN OPERATIONAL TRAINER
# Train Qwen2.5-1.5B for Artifact infrastructure operations
# NOT GLADIUS - This is Artifact's operational AI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARTIFACT_ROOT="$(dirname "$SCRIPT_DIR")"

echo ""
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║     A R T I F A C T   Q W E N   O P E R A T I O N A L        ║"
echo "║                                                               ║"
echo "║   Infrastructure AI for Artifact Virtual Enterprise          ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Activate venv if exists
if [ -f "$ARTIFACT_ROOT/.venv/bin/activate" ]; then
    source "$ARTIFACT_ROOT/.venv/bin/activate"
fi

echo "Starting Artifact Qwen Operational Trainer..."
echo "Purpose: Infrastructure operations (NOT GLADIUS)"
echo ""

python3 "$SCRIPT_DIR/qwen_operational.py" --train

if [ $? -eq 0 ]; then
    echo ""
    echo "Qwen Operational training complete!"
    echo "Model ready for Artifact infrastructure operations."
else
    echo ""
    echo "Training encountered issues. Check logs."
fi
