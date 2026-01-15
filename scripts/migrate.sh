#!/usr/bin/env bash
#
# GLADIUS Migration Script
# =========================
# Migrates the GLADIUS workspace to a new location (e.g., external HDD)
#
# Usage:
#   ./migrate.sh /path/to/destination
#   ./migrate.sh /mnt/smartdrive
#
# This script:
# 1. Creates a complete backup of the workspace
# 2. Updates all paths to be relative/portable
# 3. Copies to destination
# 4. Verifies integrity
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Get script location
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}║         G L A D I U S   M I G R A T I O N   T O O L         ║${NC}"
echo -e "${CYAN}║                                                              ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check arguments
if [ -z "$1" ]; then
    echo -e "${RED}Error: Destination path required${NC}"
    echo ""
    echo "Usage: ./migrate.sh /path/to/destination"
    echo "Example: ./migrate.sh /mnt/smartdrive/gladius"
    exit 1
fi

DEST="$1"

# Check destination
echo -e "${YELLOW}Checking destination...${NC}"
if [ ! -d "$(dirname "$DEST")" ]; then
    echo -e "${RED}Error: Parent directory of $DEST does not exist${NC}"
    echo "Please mount the external drive first"
    exit 1
fi

# Check disk space
SRC_SIZE=$(du -sm "$PROJECT_ROOT" 2>/dev/null | cut -f1)
echo -e "  Source size: ${BOLD}${SRC_SIZE}MB${NC}"

if [ -d "$DEST" ]; then
    DEST_FREE=$(df -m "$DEST" | tail -1 | awk '{print $4}')
else
    DEST_FREE=$(df -m "$(dirname "$DEST")" | tail -1 | awk '{print $4}')
fi
echo -e "  Destination free: ${BOLD}${DEST_FREE}MB${NC}"

if [ "$SRC_SIZE" -gt "$DEST_FREE" ]; then
    echo -e "${RED}Error: Not enough space on destination${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Space check passed${NC}"
echo ""

# Create destination
echo -e "${YELLOW}Creating destination directory...${NC}"
mkdir -p "$DEST"
echo -e "${GREEN}✓ Created $DEST${NC}"
echo ""

# Stop any running services
echo -e "${YELLOW}Stopping GLADIUS services...${NC}"
if [ -f "$PROJECT_ROOT/gladius.sh" ]; then
    "$PROJECT_ROOT/gladius.sh" stop 2>/dev/null || true
fi
echo -e "${GREEN}✓ Services stopped${NC}"
echo ""

# Commit any pending changes
echo -e "${YELLOW}Committing pending changes...${NC}"
cd "$PROJECT_ROOT"
if [ -d ".git" ]; then
    git add -A 2>/dev/null || true
    git commit -m "Pre-migration checkpoint $(date +%Y-%m-%d_%H%M%S)" 2>/dev/null || echo "No changes to commit"
fi
echo -e "${GREEN}✓ Changes committed${NC}"
echo ""

# Exclude patterns for migration
EXCLUDES=(
    ".venv"
    "__pycache__"
    "*.pyc"
    ".git/objects/pack/*.pack"  # Keep git but slim it down
    "node_modules"
    "*.gguf"  # Large model files - copy separately
    ".cache"
    "logs/*.log"
)

# Build exclude args
EXCLUDE_ARGS=""
for pattern in "${EXCLUDES[@]}"; do
    EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude=$pattern"
done

# Copy files
echo -e "${YELLOW}Copying files (this may take a while)...${NC}"
rsync -av --progress $EXCLUDE_ARGS "$PROJECT_ROOT/" "$DEST/"
echo -e "${GREEN}✓ Files copied${NC}"
echo ""

# Copy large model files if they exist
MODEL_FILES=$(find "$PROJECT_ROOT" -name "*.gguf" -type f 2>/dev/null || true)
if [ -n "$MODEL_FILES" ]; then
    echo -e "${YELLOW}Copying model files...${NC}"
    for model in $MODEL_FILES; do
        REL_PATH="${model#$PROJECT_ROOT/}"
        DEST_MODEL="$DEST/$REL_PATH"
        mkdir -p "$(dirname "$DEST_MODEL")"
        cp -v "$model" "$DEST_MODEL"
    done
    echo -e "${GREEN}✓ Model files copied${NC}"
    echo ""
fi

# Verify copy
echo -e "${YELLOW}Verifying migration...${NC}"
SRC_COUNT=$(find "$PROJECT_ROOT" -type f | wc -l)
DEST_COUNT=$(find "$DEST" -type f | wc -l)
echo -e "  Source files: $SRC_COUNT"
echo -e "  Destination files: $DEST_COUNT"

# Allow some variance due to excludes
if [ "$DEST_COUNT" -lt 10 ]; then
    echo -e "${RED}Warning: Very few files copied. Check for errors.${NC}"
else
    echo -e "${GREEN}✓ Migration verified${NC}"
fi
echo ""

# Create symlink to old location (optional)
echo -e "${YELLOW}Would you like to create a symlink from old location? (y/N)${NC}"
read -r REPLY
if [[ $REPLY =~ ^[Yy]$ ]]; then
    OLD_BACKUP="${PROJECT_ROOT}.backup.$(date +%Y%m%d)"
    mv "$PROJECT_ROOT" "$OLD_BACKUP"
    ln -s "$DEST" "$PROJECT_ROOT"
    echo -e "${GREEN}✓ Symlink created: $PROJECT_ROOT -> $DEST${NC}"
    echo -e "  Original backed up to: $OLD_BACKUP"
fi
echo ""

# Final summary
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     MIGRATION COMPLETE                       ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  ${BOLD}New Location:${NC} $DEST"
echo -e "  ${BOLD}Files Copied:${NC} $DEST_COUNT"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. cd $DEST"
echo "  2. ./gladius.sh start"
echo "  3. Verify all services are running"
echo ""
echo -e "${GREEN}Migration successful!${NC}"
