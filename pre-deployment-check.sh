#!/bin/bash

# Comprehensive System Health Check for Deployment
# Run this script before deploying to production

set -e

echo "=========================================="
echo "AnomaaH Platform - Pre-Deployment Health Check"
echo "=========================================="
echo ""
echo "Checking system readiness for deployment..."
echo ""

ERRORS=0
WARNINGS=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print results
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    WARNINGS=$((WARNINGS + 1))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ERRORS=$((ERRORS + 1))
}

echo "1. CODE QUALITY CHECKS"
echo "----------------------"

# Check Python syntax
if find services -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -q "SyntaxError"; then
    check_fail "Python syntax errors found"
else
    check_pass "All Python files have valid syntax"
fi

# Check for critical TODO/FIXME
CRITICAL_TODOS=$(grep -r "FIXME\|BUG\|CRITICAL" services --include="*.py" | grep -v "^Binary" | wc -l)
if [ "$CRITICAL_TODOS" -gt 0 ]; then
    check_warn "$CRITICAL_TODOS critical TODO/FIXME comments found"
else
    check_pass "No critical TODO/FIXME comments"
fi

echo ""
echo "2. CONFIGURATION CHECKS"
echo "----------------------"

# Check environment file exists
if [ -f ".env" ]; then
    check_pass ".env file exists"
    
    # Check for default/insecure values
    if grep -q "postgres:postgres" .env 2>/dev/null; then
        check_warn "Default database password detected in .env"
    else
        check_pass "Database password is not default"
    fi
    
    if grep -q "SECRET_KEY.*demo" .env 2>/dev/null; then
        check_fail "Insecure SECRET_KEY detected in .env"
    elif grep -q "SECRET_KEY.*replace" .env 2>/dev/null; then
        check_fail "SECRET_KEY not set in .env"
    else
        check_pass "SECRET_KEY appears to be set"
    fi
else
    check_fail ".env file not found"
fi

# Check docker-compose.yml exists
if [ -f "docker-compose.yml" ]; then
    check_pass "docker-compose.yml exists"
else
    check_fail "docker-compose.yml not found"
fi

echo ""
echo "3. CRITICAL ENDPOINTS CHECK"
echo "--------------------------"

# Check if critical files exist
CRITICAL_FILES=(
    "services/api_gateway/main.py"
    "services/auth_service/main.py"
    "services/order_service/main.py"
    "services/payment_service/main.py"
    "shared/models.py"
    "shared/database.py"
)

for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        check_pass "Critical file exists: $file"
    else
        check_fail "Critical file missing: $file"
    fi
done

# Check for earnings endpoint
if grep -q "def get_rider_earnings" services/order_service/main.py; then
    check_pass "Earnings endpoint implemented in order service"
else
    check_fail "Earnings endpoint NOT found in order service"
fi

# Check for earnings routing in gateway
if grep -q "def get_rider_earnings\|/earnings/" services/api_gateway/main.py; then
    check_pass "Earnings routing in API gateway"
else
    check_warn "Earnings routing not found in API gateway"
fi

echo ""
echo "4. ANDROID APP CHECKS"
echo "--------------------"

# Check Android build files
if [ -f "rider-app/build.gradle" ]; then
    check_pass "Android build.gradle exists"
    
    # Check for optimizations
    if grep -q "org.gradle.jvmargs=-Xmx1024m" rider-app/gradle.properties; then
        check_pass "Gradle memory optimized (1024m)"
    else
        check_warn "Gradle memory not optimized"
    fi
    
    if grep -q "org.gradle.caching=true" rider-app/gradle.properties; then
        check_pass "Build cache enabled"
    else
        check_warn "Build cache not enabled"
    fi
else
    check_fail "Android build.gradle not found"
fi

# Check for API URLs
if grep -q "API_BASE_URL" rider-app/build.gradle; then
    check_pass "API URLs configured in build.gradle"
else
    check_warn "API URLs not found in build.gradle"
fi

echo ""
echo "5. DATABASE MODELS CHECK"
echo "-----------------------"

# Check for earnings field in Rider model
if grep -q "total_earnings" shared/models.py; then
    check_pass "Rider.total_earnings field exists"
else
    check_fail "Rider.total_earnings field missing"
fi

# Check for OrderStatus.DELIVERED
if grep -q "DELIVERED" shared/models.py; then
    check_pass "OrderStatus.DELIVERED exists"
else
    check_fail "OrderStatus.DELIVERED missing"
fi

echo ""
echo "6. DOCUMENTATION CHECK"
echo "---------------------"

DOCS=(
    "README.md"
    "BUILDING_ON_LOW_SPEC_PC.md"
    "EARNINGS_IMPLEMENTATION_GUIDE.md"
    "DEPLOYMENT_READINESS.md"
)

for doc in "${DOCS[@]}"; do
    if [ -f "$doc" ]; then
        check_pass "Documentation exists: $doc"
    else
        check_warn "Documentation missing: $doc"
    fi
done

echo ""
echo "7. SECURITY CHECKS"
echo "-----------------"

# Check for exposed secrets
if grep -r "password.*=.*'.*'" services --include="*.py" | grep -v "environ.get" | grep -q .; then
    check_warn "Potential hardcoded passwords found"
else
    check_pass "No hardcoded passwords detected"
fi

# Check for debug mode in production files
if grep -q "DEBUG.*=.*True" services/*/main.py; then
    check_warn "Debug mode might be enabled"
else
    check_pass "Debug mode not hardcoded to True"
fi

echo ""
echo "=========================================="
echo "SUMMARY"
echo "=========================================="
echo ""

if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}✓ ALL CHECKS PASSED!${NC}"
    echo ""
    echo "System is ready for deployment."
    echo ""
    echo "Next steps:"
    echo "1. Run integration tests (see DEPLOYMENT_READINESS.md)"
    echo "2. Test Android app with backend"
    echo "3. Backup database"
    echo "4. Deploy!"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo -e "${YELLOW}⚠ PASSED WITH WARNINGS${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "You can deploy but should review warnings."
    echo "See above for details."
    exit 0
else
    echo -e "${RED}✗ CHECKS FAILED${NC}"
    echo ""
    echo "Errors: $ERRORS"
    echo "Warnings: $WARNINGS"
    echo ""
    echo "Please fix errors before deploying."
    echo "See above for details."
    exit 1
fi
