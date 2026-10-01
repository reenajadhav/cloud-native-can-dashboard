#!/bin/bash

FAILED_TESTS=0
FAILED_LIST=""

run_test() {
    TEST_NAME="$1"
    TEST_SCRIPT="$2"

    echo ""
    echo "=========================================="
    echo "Running: $TEST_NAME"
    echo "=========================================="

    if $TEST_SCRIPT; then
        echo "✅ PASS: $TEST_NAME"
    else
        echo "❌ FAIL: $TEST_NAME"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        FAILED_LIST="${FAILED_LIST}\n- ${TEST_NAME}"
    fi
}

echo "=========================================="
echo "CAN-CLOUD PLATFORM SMOKE TEST SUITE"
echo "=========================================="

run_test "Dashboard Reachable" \
./tests/smoke/dashboard_reachiable.sh

run_test "Dashboard Smoke" \
./tests/smoke/dashboard_smoke.sh

run_test "Parser Python Compilation" \
./tests/smoke/parser_python_compilation.sh

run_test "Parser Critical Imports" \
./tests/smoke/parser_critical_imports.sh

run_test "Parser Required Files" \
./tests/smoke/parser_required_files.sh

run_test "Parser Dependency Validation" \
./tests/smoke/parser_dependency_validation.sh

run_test "Parser Startup Banner" \
./tests/smoke/parser_startup_banner.sh

run_test "Simulator Starts" \
./tests/smoke/simulator_starts.sh

run_test "Simulator Generates CAN Data" \
./tests/smoke/simulator_generates_can_Data.sh

echo ""

if [ "$FAILED_TESTS" -eq 0 ]; then
    echo "=========================================="
    echo "ALL SMOKE TESTS PASSED"
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "FAILED TESTS"
    echo "=========================================="

    echo -e "$FAILED_LIST"

    echo ""
    echo "$FAILED_TESTS TEST(S) FAILED"

    exit 1
fi
