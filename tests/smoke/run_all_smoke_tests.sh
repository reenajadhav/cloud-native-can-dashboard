#!/bin/bash

set -e

echo "=========================================="
echo "CAN-CLOUD PLATFORM SMOKE TEST SUITE"
echo "=========================================="

echo ""
echo "Running Parser Smoke Tests..."
./tests/smoke/parser_smoke.sh
./tests/smoke/parser_python_compilation.sh
./tests/smoke/parser_critical_imports.sh
./tests/smoke/parser_required_files.sh
./tests/smoke/parser_dependency_validation.sh
./tests/smoke/parser_startup_banner.sh

echo ""
echo "Running Simulator Smoke Tests..."
./tests/smoke/simulator_starts.sh
./tests/smoke/simulator_generates_can_Data.sh
./tests/smoke/simulator_smoke.sh

echo ""
echo "=========================================="
echo "ALL SMOKE TESTS PASSED"
echo "=========================================="