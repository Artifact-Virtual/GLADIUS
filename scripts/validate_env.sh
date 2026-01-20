#!/bin/bash
# =============================================================================
# GLADIUS Environment Validation Script
# =============================================================================
#
# Validates that .env is properly configured with all required variables.
# Run this before starting GLADIUS to catch configuration issues early.
#
# Usage:
#   ./scripts/validate_env.sh
#
# Exit codes:
#   0 - All validations passed
#   1 - Validation failures found
#
# =============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GLADIUS_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$GLADIUS_ROOT/.env"
ENV_EXAMPLE="$GLADIUS_ROOT/.env.example"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         GLADIUS ENVIRONMENT VALIDATION                       ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

ERRORS=0
WARNINGS=0

# Check if .env file exists
echo -e "${BLUE}[1/5] Checking .env file existence...${NC}"
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}❌ ERROR: .env file not found at $ENV_FILE${NC}"
    echo ""
    if [ -f "$ENV_EXAMPLE" ]; then
        echo "   To fix: cp .env.example .env"
        echo "   Then edit .env and fill in your values"
    else
        echo -e "${RED}   ERROR: .env.example also missing!${NC}"
    fi
    ERRORS=$((ERRORS + 1))
    echo ""
    exit 1
else
    echo -e "${GREEN}✅ .env file found${NC}"
fi
echo ""

# Load environment variables
echo -e "${BLUE}[2/5] Loading environment variables...${NC}"
export $(grep -v '^#' "$ENV_FILE" | grep -v '^\s*$' | xargs 2>/dev/null) || true
echo -e "${GREEN}✅ Environment loaded${NC}"
echo ""

# Check critical security variables
echo -e "${BLUE}[3/5] Validating critical security variables...${NC}"

CRITICAL_VARS=(
    "SECRET_KEY"
    "DASHBOARD_SECRET_KEY"
    "JWT_SECRET_KEY"
    "LEGION_SECRET_KEY"
    "SENTINEL_KILL_PASSWORD"
)

for var in "${CRITICAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${RED}❌ CRITICAL: $var is not set${NC}"
        ERRORS=$((ERRORS + 1))
    else
        # Check if it's still a default/example value
        if [[ "${!var}" =~ (change|example|default|devpass|secret-key) ]]; then
            echo -e "${RED}❌ CRITICAL: $var appears to be a default/example value${NC}"
            echo "   Value: ${!var:0:30}..."
            ERRORS=$((ERRORS + 1))
        elif [ ${#!var} -lt 16 ]; then
            echo -e "${YELLOW}⚠️  WARNING: $var is too short (< 16 chars)${NC}"
            WARNINGS=$((WARNINGS + 1))
        else
            echo -e "${GREEN}✅ $var is set${NC}"
        fi
    fi
done
echo ""

# Check SMTP configuration
echo -e "${BLUE}[4/5] Validating SMTP configuration...${NC}"

SMTP_VARS=(
    "SMTP_HOST"
    "SMTP_PORT"
    "SMTP_USER"
    "SMTP_PASSWORD"
)

SMTP_MISSING=0
for var in "${SMTP_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${YELLOW}⚠️  $var is not set${NC}"
        SMTP_MISSING=$((SMTP_MISSING + 1))
    else
        echo -e "${GREEN}✅ $var is set${NC}"
    fi
done

if [ $SMTP_MISSING -gt 0 ]; then
    echo -e "${YELLOW}⚠️  WARNING: SMTP not fully configured (email notifications disabled)${NC}"
    WARNINGS=$((WARNINGS + 1))
fi
echo ""

# Check optional but recommended variables
echo -e "${BLUE}[5/5] Checking recommended optional variables...${NC}"

OPTIONAL_VARS=(
    "DISCORD_WEBHOOK_URL"
    "OPENAI_API_KEY"
    "GEMINI_API_KEY"
)

for var in "${OPTIONAL_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        echo -e "${YELLOW}ℹ️  $var is not set (optional)${NC}"
    else
        echo -e "${GREEN}✅ $var is set${NC}"
    fi
done
echo ""

# Summary
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}VALIDATION SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✅ All validations passed!${NC}"
    echo ""
    echo "Your environment is properly configured."
    echo "You can start GLADIUS with: ./gladius.sh start"
    echo ""
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    echo ""
    echo "Your environment is functional but has some warnings."
    echo "You can start GLADIUS, but consider addressing the warnings."
    echo ""
    exit 0
else
    echo -e "${RED}❌ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  $WARNINGS warning(s) found${NC}"
    fi
    echo ""
    echo "Please fix the errors before starting GLADIUS."
    echo ""
    echo "Quick fixes:"
    echo "  1. Generate secure keys: openssl rand -hex 32"
    echo "  2. Update .env with the generated keys"
    echo "  3. Run this validation again: ./scripts/validate_env.sh"
    echo ""
    exit 1
fi
