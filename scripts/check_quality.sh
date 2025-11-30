#!/usr/bin/env bash
# Code quality check script for HabitLedger
# This script runs all linting and testing tools to check code quality

set -e  # Exit on first error

# Fetch arg passed to script
# If "run-tests" is passed, run the test suite as well
RUN_TESTS=false
if [ "$1" == "run-tests" ]; then
    RUN_TESTS=true
fi


# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║        HABITLEDGER CODE QUALITY CHECK                     ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Track overall status
EXIT_CODE=0

# 1. Black - Code Formatting
echo -e "${BLUE}1️⃣  Checking code formatting (Black)...${NC}"
if black src/ tests/ --check --quiet; then
    echo -e "${GREEN}✅ Black: All files formatted correctly${NC}"
else
    echo -e "${RED}❌ Black: Formatting issues found${NC}"
    echo -e "${YELLOW}   Run: ./fix_quality.sh or black src/ tests/${NC}"
    EXIT_CODE=1
fi
echo ""

# 2. Ruff - Fast Python Linter
echo -e "${BLUE}2️⃣  Running linter (Ruff)...${NC}"
if ruff check src/ tests/ --quiet; then
    echo -e "${GREEN}✅ Ruff: All checks passed${NC}"
else
    echo -e "${RED}❌ Ruff: Linting issues found${NC}"
    echo -e "${YELLOW}   Run: ./fix_quality.sh or ruff check src/ tests/ --fix${NC}"
    EXIT_CODE=1
fi
echo ""

# 3. Mypy - Type Checking
echo -e "${BLUE}3️⃣  Checking types (Mypy)...${NC}"
if mypy src/ 2>&1 | grep -q "Success"; then
    echo -e "${GREEN}✅ Mypy: No type errors found${NC}"
else
    echo -e "${RED}❌ Mypy: Type errors found${NC}"
    mypy src/
    EXIT_CODE=1
fi
echo ""

# 4. Pylint - Code Analysis
echo -e "${BLUE}4️⃣  Running code analysis (Pylint)...${NC}"
PYLINT_SCORE=$(pylint src/ 2>&1 | grep -oP 'rated at \K[0-9.]+' | head -1)
if [ -n "$PYLINT_SCORE" ]; then
    # Check if score is >= 9.0
    if awk 'BEGIN {exit !('$PYLINT_SCORE' >= 9.0)}'; then
        echo -e "${GREEN}✅ Pylint: Score $PYLINT_SCORE/10${NC}"
    else
        echo -e "${YELLOW}⚠️  Pylint: Score $PYLINT_SCORE/10 (acceptable but could improve)${NC}"
    fi
else
    echo -e "${RED}❌ Pylint: Analysis failed${NC}"
    echo "$PYLINT_OUTPUT"
    EXIT_CODE=1
fi
echo ""


# 5. Pytest - Test Suite
if [ "$RUN_TESTS" = true ]; then
    echo -e "${BLUE}5️⃣  Running test suite (Pytest)...${NC}"
    if python -m pytest tests/ -q --tb=short 2>&1 | tee /tmp/pytest_output.txt | tail -1 | grep -q "passed"; then
        PASSED=$(grep -oP '\d+(?= passed)' /tmp/pytest_output.txt | tail -1)
        echo -e "${GREEN}✅ Pytest: $PASSED tests passed${NC}"
    else
        echo -e "${RED}❌ Pytest: Some tests failed${NC}"
        python -m pytest tests/ -v --tb=short
        EXIT_CODE=1
    fi
    echo ""
fi

# Summary
echo "════════════════════════════════════════════════════════════"
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}🎉 All quality checks passed!${NC}"
else
    echo -e "${RED}❌ Some checks failed. Run ./fix_quality.sh to auto-fix.${NC}"
fi
echo "════════════════════════════════════════════════════════════"

exit $EXIT_CODE
