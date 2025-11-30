#!/usr/bin/env bash
# Setup verification script for HabitLedger Agent
# Ensures Python 3.13.2, .venv, and nbstripout are properly configured

set -e  # Exit on error

echo "🔍 HabitLedger Agent - Environment Setup Verification"
echo "=================================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "1️⃣  Checking Python version..."
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.13.2"

if [ "$PYTHON_VERSION" = "$REQUIRED_VERSION" ]; then
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION (correct)"
else
    echo -e "${RED}✗${NC} Python $PYTHON_VERSION (expected $REQUIRED_VERSION)"
    echo -e "${YELLOW}⚠️  Please install Python $REQUIRED_VERSION${NC}"
    exit 1
fi
echo ""

# Check if .venv exists
echo "2️⃣  Checking virtual environment..."
if [ -d ".venv" ]; then
    echo -e "${GREEN}✓${NC} .venv directory exists"

    # Check if .venv is activated
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}✓${NC} Virtual environment is activated"

        # Check if python in venv matches required version
        VENV_PYTHON_VERSION=$(.venv/bin/python --version 2>&1 | awk '{print $2}')
        if [ "$VENV_PYTHON_VERSION" = "$REQUIRED_VERSION" ]; then
            echo -e "${GREEN}✓${NC} .venv uses Python $VENV_PYTHON_VERSION"
        else
            echo -e "${YELLOW}⚠️${NC} .venv uses Python $VENV_PYTHON_VERSION (expected $REQUIRED_VERSION)"
            echo -e "${YELLOW}   Consider recreating .venv with: python -m venv .venv${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️${NC} Virtual environment is not activated"
        echo -e "${YELLOW}   Run: source .venv/bin/activate${NC}"
    fi
else
    echo -e "${RED}✗${NC} .venv directory not found"
    echo -e "${YELLOW}   Create it with: python -m venv .venv${NC}"
    exit 1
fi
echo ""

# Check if dependencies are installed
echo "3️⃣  Checking dependencies..."
if [ -f "requirements.txt" ]; then
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        # Check a few key packages
        MISSING_DEPS=0
        for pkg in "pytest" "black" "ruff" "nbstripout"; do
            if python -c "import $pkg" 2>/dev/null; then
                echo -e "${GREEN}✓${NC} $pkg installed"
            else
                echo -e "${RED}✗${NC} $pkg not found"
                MISSING_DEPS=1
            fi
        done

        if [ $MISSING_DEPS -eq 1 ]; then
            echo -e "${YELLOW}⚠️  Install dependencies with: pip install -r requirements.txt${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️${NC} Cannot check dependencies (venv not activated)"
    fi
else
    echo -e "${YELLOW}⚠️${NC} requirements.txt not found"
fi
echo ""

# Check nbstripout installation
echo "4️⃣  Checking nbstripout setup..."
if command -v nbstripout &> /dev/null; then
    echo -e "${GREEN}✓${NC} nbstripout is installed"

    # Check if nbstripout is configured in git
    if git config --get filter.nbstripout.clean &> /dev/null; then
        echo -e "${GREEN}✓${NC} nbstripout is configured in git"
    else
        echo -e "${YELLOW}⚠️${NC} nbstripout not configured in git"
        echo -e "${YELLOW}   Run: nbstripout --install${NC}"
    fi
else
    echo -e "${RED}✗${NC} nbstripout not installed"
    echo -e "${YELLOW}   Install it with: pip install nbstripout${NC}"
    echo -e "${YELLOW}   Then configure: nbstripout --install${NC}"
fi
echo ""

# Check pre-commit hooks (optional)
echo "5️⃣  Checking pre-commit hooks (optional)..."
if command -v pre-commit &> /dev/null; then
    echo -e "${GREEN}✓${NC} pre-commit is installed"

    if [ -f ".git/hooks/pre-commit" ]; then
        echo -e "${GREEN}✓${NC} pre-commit hooks are installed"
    else
        echo -e "${YELLOW}ℹ️${NC} pre-commit hooks not installed"
        echo -e "${YELLOW}   Install them with: pre-commit install${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️${NC} pre-commit not installed (optional but recommended)"
    echo -e "${YELLOW}   Install it with: pip install pre-commit && pre-commit install${NC}"
fi
echo ""

# Check configuration files
echo "6️⃣  Checking configuration files..."
CONFIG_FILES=(".python-version" "pyproject.toml" ".pre-commit-config.yaml" ".vscode/settings.json")
for file in "${CONFIG_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file exists"
    else
        echo -e "${YELLOW}⚠️${NC} $file not found"
    fi
done
echo ""

# Summary
echo "=================================================="
echo "✅ Setup verification complete!"
echo ""
echo "📝 Next steps (if needed):"
echo "   1. Activate venv: source .venv/bin/activate"
echo "   2. Install deps: pip install -r requirements.txt"
echo "   3. Setup nbstripout: nbstripout --install"
echo "   4. (Optional) Install pre-commit: pre-commit install"
echo ""
echo "🚀 Once setup is complete, you can start coding!"
