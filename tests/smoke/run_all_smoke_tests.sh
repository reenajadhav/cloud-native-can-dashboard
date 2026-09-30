#!/bin/bash

FAILED_TESTS=0

echo "=========================================="
echo "CAN-CLOUD PLATFORM SMOKE TEST SUITE"
echo "=========================================="

echo ""
echo "Running Dashboard Smoke Tests..."
./tests/smoke/dashboard_reachiable.sh || ((FAILED_TESTS++))
./tests/smoke/dashboard_smoke.sh || ((FAILED_TESTS++))

echo ""
echo "Running Parser Smoke Tests..."
./tests/smoke/parser_python_compilation.sh || ((FAILED_TESTS++))
./tests/smoke/parser_critical_imports.sh || ((FAILED_TESTS++))
./tests/smoke/parser_required_files.sh || ((FAILED_TESTS++))
./tests/smoke/parser_dependency_validation.sh || ((FAILED_TESTS++))
./tests/smoke/parser_startup_banner.sh || ((FAILED_TESTS++))

echo ""
echo "Running Simulator Smoke Tests..."
./tests/smoke/simulator_starts.sh || ((FAILED_TESTS++))
./tests/smoke/simulator_generates_can_Data.sh || ((FAILED_TESTS++))

echo ""
echo "Failed Tests: $FAILED_TESTS"

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo "=========================================="
    echo "ALL SMOKE TESTS PASSED"
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "$FAILED_TESTS TEST(S) FAILED"
    echo "=========================================="
    exit 1
fi
