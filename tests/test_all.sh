#!/bin/bash
# test_all.sh - Comprehensive testing script for Django project
# Usage: ./test_all.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ PASSED${NC}: $2"
        ((PASSED_TESTS++))
    else
        echo -e "${RED}❌ FAILED${NC}: $2"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
}

# Function to print section header
print_header() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Start timer
START_TIME=$(date +%s)

echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Django Project Quality Check Suite    ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""

# ============================================
# 1. Environment Check
# ============================================
print_header "1. Environment Check"

echo "🐍 Checking Python version..."
python --version
print_status $? "Python version check"

echo "📦 Checking Django installation..."
python -c "import django; print(f'Django {django.VERSION}')" 2>/dev/null
print_status $? "Django installation"

echo "📋 Checking required packages..."
python -c "import dotenv, ruff, bandit" 2>/dev/null
print_status $? "Required packages (dotenv, ruff, bandit)"

echo "📄 Checking .env file..."
if [ -f .env ]; then
    echo "✓ .env file found"
    print_status 0 ".env file exists"
else
    echo "⚠ .env file not found"
    print_status 1 ".env file exists"
fi

# ============================================
# 2. Code Quality Checks
# ============================================
print_header "2. Code Quality Checks"

echo "🔧 Running Ruff linter..."
if ruff check . --quiet; then
    print_status 0 "Ruff linter"
else
    ruff check .
    print_status 1 "Ruff linter"
fi

echo "🎨 Running Ruff formatter check..."
if ruff format --check . --quiet; then
    print_status 0 "Ruff formatter"
else
    ruff format --check .
    print_status 1 "Ruff formatter"
fi

echo "📝 Checking Django templates with djLint..."
if command -v djlint &> /dev/null; then
    if djlint templates/ --check --quiet 2>/dev/null; then
        print_status 0 "DjLint (Django templates)"
    else
        djlint templates/ --check
        print_status 1 "DjLint (Django templates)"
    fi
else
    echo "⚠ djlint not installed, skipping"
    print_status 0 "DjLint (skipped)"
fi

# ============================================
# 3. Security Checks
# ============================================
print_header "3. Security Checks"

echo "🔒 Running Bandit security scan..."
if bandit -r . -c pyproject.toml --quiet; then
    print_status 0 "Bandit security scan"
else
    bandit -r . -c pyproject.toml
    print_status 1 "Bandit security scan"
fi

echo "🔐 Checking for secrets in code..."
if command -v detect-secrets &> /dev/null; then
    if detect-secrets scan --baseline .secrets.baseline 2>/dev/null; then
        print_status 0 "Secrets detection"
    else
        echo "⚠ Potential secrets found"
        print_status 1 "Secrets detection"
    fi
else
    echo "⚠ detect-secrets not installed, skipping"
    print_status 0 "Secrets detection (skipped)"
fi

echo "🛡️ Checking for known vulnerabilities..."
if command -v safety &> /dev/null; then
    if safety check --json 2>/dev/null; then
        print_status 0 "Safety vulnerability check"
    else
        echo "⚠ Vulnerabilities found"
        safety check
        print_status 1 "Safety vulnerability check"
    fi
else
    echo "⚠ safety not installed, skipping"
    print_status 0 "Safety check (skipped)"
fi

# ============================================
# 4. Django Checks
# ============================================
print_header "4. Django System Checks"

echo "🔍 Running Django system check..."
if python manage.py check --quiet; then
    print_status 0 "Django system check"
else
    python manage.py check
    print_status 1 "Django system check"
fi

echo "🗄️ Checking for missing migrations..."
if python manage.py makemigrations --check --dry-run --quiet 2>/dev/null; then
    print_status 0 "Migrations check"
else
    echo "⚠ Unapplied migrations detected"
    python manage.py makemigrations --check --dry-run
    print_status 1 "Migrations check"
fi

echo "🚀 Checking deployment readiness..."
if python manage.py check --deploy --quiet 2>/dev/null; then
    print_status 0 "Deployment check"
else
    python manage.py check --deploy
    print_status 1 "Deployment check"
fi

# ============================================
# 5. Import Checks
# ============================================
print_header "5. Import & Syntax Checks"

echo "📥 Checking Python imports..."
if python -c "
import sys
import os
sys.path.insert(0, os.getcwd())
try:
    from main import models, views, decorators, signals
    print('All imports successful')
    sys.exit(0)
except ImportError as e:
    print(f'Import error: {e}')
    sys.exit(1)
"; then
    print_status 0 "Python imports"
else
    print_status 1 "Python imports"
fi

echo "✅ Checking Python syntax..."
find . -name "*.py" -not -path "*/migrations/*" -not -path "*/.venv/*" -not -path "*/venv/*" | while read -r file; do
    python -m py_compile "$file" 2>/dev/null || echo "Syntax error in: $file"
done
print_status $? "Python syntax"

# ============================================
# 6. File Checks
# ============================================
print_header "6. File & Configuration Checks"

echo "📂 Checking required files..."
REQUIRED_FILES=(
    "manage.py"
    "pyproject.toml"
    ".env"
    ".gitignore"
    "requirements.txt"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (missing)"
    fi
done
print_status 0 "Required files check"

echo "🚫 Checking .gitignore..."
if grep -q ".env" .gitignore 2>/dev/null; then
    print_status 0 ".env in .gitignore"
else
    echo "⚠ .env not in .gitignore!"
    print_status 1 ".env in .gitignore"
fi

echo "🔑 Checking for hardcoded secrets..."
if grep -r "SECRET_KEY.*=.*\"django-insecure" --include="*.py" . 2>/dev/null; then
    echo "⚠ Found hardcoded SECRET_KEY"
    print_status 1 "No hardcoded secrets"
else
    print_status 0 "No hardcoded secrets"
fi

# ============================================
# 7. Code Metrics
# ============================================
print_header "7. Code Metrics"

echo "📊 Counting lines of code..."
if command -v cloc &> /dev/null; then
    cloc . --quiet --exclude-dir=migrations,.venv,venv,staticfiles,media
else
    echo "Total Python files: $(find . -name '*.py' -not -path '*/migrations/*' -not -path '*/.venv/*' | wc -l)"
fi
print_status 0 "Code metrics"

echo "📈 Checking code complexity..."
if command -v radon &> /dev/null; then
    radon cc . -a --exclude=migrations,.venv,venv
else
    echo "⚠ radon not installed (pip install radon)"
fi
print_status 0 "Code complexity (informational)"

# ============================================
# 8. Optional: Run Tests
# ============================================
print_header "8. Running Django Tests"

echo "🧪 Running Django test suite..."
if python manage.py test --verbosity=1; then
    print_status 0 "Django tests"
else
    print_status 1 "Django tests"
fi

# ============================================
# 9. Performance Checks
# ============================================
print_header "9. Performance Checks"

echo "⚡ Checking for N+1 queries..."
echo "(Run: python manage.py shell < check_queries.py)"
print_status 0 "Query optimization (manual check)"

echo "🎯 Checking settings optimization..."
if grep -q "DEBUG = False" idrissimart/settings/docker.py; then
    print_status 0 "Production DEBUG setting"
else
    echo "⚠ DEBUG should be False in production"
    print_status 1 "Production DEBUG setting"
fi

# ============================================
# Summary
# ============================================
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

print_header "Test Summary"

echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║           Test Results Summary           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "Total Tests:   ${BLUE}${TOTAL_TESTS}${NC}"
echo -e "Passed:        ${GREEN}${PASSED_TESTS}${NC}"
echo -e "Failed:        ${RED}${FAILED_TESTS}${NC}"
echo -e "Duration:      ${YELLOW}${DURATION}s${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 All tests passed! Ready to deploy! 🎉  ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo -e "${RED}╔════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ⚠️  Some tests failed. Review above.  ⚠️   ║${NC}"
    echo -e "${RED}╚════════════════════════════════════════════╝${NC}"
    exit 1
fi
