#!/usr/bin/env bash
# Code quality fix script for HabitLedger
# This script automatically fixes formatting and linting issues

set -e  # Exit on first error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════════════════════════╗"
echo "║        HABITLEDGER CODE QUALITY AUTO-FIX                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# 1. Black - Auto-format code
echo -e "${BLUE}1️⃣  Auto-formatting code (Black)...${NC}"
if black src/ tests/; then
    echo -e "${GREEN}✅ Black: Code formatted${NC}"
else
    echo -e "${RED}❌ Black: Formatting failed${NC}"
    exit 1
fi
echo ""

# 2. Ruff - Auto-fix linting issues
echo -e "${BLUE}2️⃣  Auto-fixing linting issues (Ruff)...${NC}"
RUFF_OUTPUT=$(ruff check src/ tests/ --fix 2>&1)
if echo "$RUFF_OUTPUT" | grep -q "fixed"; then
    FIXED=$(echo "$RUFF_OUTPUT" | grep -oP '\d+(?= fixed)' | head -1)
    echo -e "${GREEN}✅ Ruff: Fixed $FIXED issues${NC}"
elif echo "$RUFF_OUTPUT" | grep -q "All checks passed"; then
    echo -e "${GREEN}✅ Ruff: No issues to fix${NC}"
else
    echo -e "${YELLOW}⚠️  Ruff: Some issues remain (manual fix needed)${NC}"
    ruff check src/ tests/
fi
echo ""

# 3. Check remaining issues
echo -e "${BLUE}3️⃣  Checking for remaining issues...${NC}"
echo ""

# Mypy check
echo -e "${YELLOW}📌 Mypy (type checking - manual fixes may be needed):${NC}"
if mypy src/ --no-error-summary 2>&1 | grep -q "Success"; then
    echo -e "${GREEN}✅ No type errors${NC}"
else
    echo -e "${RED}❌ Type errors found (requires manual fix):${NC}"
    mypy src/
fi
echo ""

# Pylint check
echo -e "${YELLOW}📌 Pylint (code quality - informational):${NC}"
PYLINT_SCORE=$(pylint src/ 2>&1 | grep -oP 'rated at \K[0-9.]+' | head -1)
if [ -n "$PYLINT_SCORE" ]; then
    echo -e "${GREEN}✅ Score: $PYLINT_SCORE/10${NC}"
fi
echo ""

# Run tests to ensure nothing broke
echo -e "${BLUE}4️⃣  Running tests to verify fixes...${NC}"
if python -m pytest tests/ -q --tb=short 2>&1 | tail -1 | grep -q "passed"; then
    PASSED=$(python -m pytest tests/ -q 2>&1 | grep -oP '\d+(?= passed)' | tail -1)
    echo -e "${GREEN}✅ All $PASSED tests still pass${NC}"
else
    echo -e "${RED}❌ Tests failed after fixes! Please review changes.${NC}"
    python -m pytest tests/ -v --tb=short
    exit 1
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════"
echo -e "${GREEN}✨ Auto-fix complete!${NC}"
echo ""
echo "What was fixed:"
echo "  • Code formatting (Black)"
echo "  • Auto-fixable linting issues (Ruff)"
echo ""
echo "What may need manual attention:"
echo "  • Type errors (Mypy)"
echo "  • Complex code quality issues (Pylint)"
echo ""
echo "Run ./check_quality.sh to see the current status."
echo "════════════════════════════════════════════════════════════"
