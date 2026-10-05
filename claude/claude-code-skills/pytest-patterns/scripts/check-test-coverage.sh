#!/usr/bin/env bash
# check-test-coverage.sh — Run pytest with coverage and fail if below threshold.
#
# Usage:
#   ./check-test-coverage.sh [--output-dir <dir>] [--fail-under <pct>] [--cov-source <pkg>]
#
# Options:
#   --output-dir <dir>   Directory to write coverage results (default: ./coverage-results)
#   --fail-under <pct>   Minimum coverage percentage (default: fail_under from the
#                        project's coverage config, so CI and a local run share one number)
#   --cov-source <pkg>   Package to measure (default: $COV_SOURCE or src)
#
# Environment:
#   PYTEST     pytest command (default: "uv run pytest")
#   COVERAGE   coverage command (default: "uv run coverage")
#
# Exit codes: 0 pass, 1 tests failed, 2 coverage below threshold,
#             3 pytest could not run (interrupted, usage error, no tests collected).

set -euo pipefail

# ─── Defaults ───────────────────────────────────────────────────────────────────
OUTPUT_DIR="./coverage-results"
FAIL_UNDER=""
COV_SOURCE="${COV_SOURCE:-src}"
read -r -a PYTEST_CMD <<< "${PYTEST:-uv run pytest}"
read -r -a COVERAGE_CMD <<< "${COVERAGE:-uv run coverage}"

# ─── Parse arguments ────────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --fail-under)
            FAIL_UNDER="$2"
            shift 2
            ;;
        --cov-source)
            COV_SOURCE="$2"
            shift 2
            ;;
        -h|--help)
            echo "Usage: $0 [--output-dir <dir>] [--fail-under <pct>] [--cov-source <pkg>]"
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# ─── Setup ───────────────────────────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_FILE="$OUTPUT_DIR/coverage-report-${TIMESTAMP}.txt"
HTML_DIR="$OUTPUT_DIR/htmlcov"

echo "=== Test Coverage Check ==="
echo "Fail-under threshold: ${FAIL_UNDER:-from coverage config}${FAIL_UNDER:+%}"
echo "Coverage source:      ${COV_SOURCE}"
echo "Output directory:     ${OUTPUT_DIR}"
echo ""

# ─── Run pytest with coverage ────────────────────────────────────────────────────
# --cov-fail-under=0 keeps pytest's exit code about the tests only (it would
# otherwise also return 1 for low coverage, including from fail_under in
# pyproject.toml); the threshold is checked separately with `coverage report`.
set +e
"${PYTEST_CMD[@]}" \
    --cov="${COV_SOURCE}" \
    --cov-report=term-missing \
    --cov-report="html:${HTML_DIR}" \
    --cov-report="json:${OUTPUT_DIR}/coverage.json" \
    --cov-fail-under=0 \
    -q \
    2>&1 | tee "$RESULTS_FILE"
PYTEST_EXIT=${PIPESTATUS[0]}
set -e

finish() {
    local status="$1" message="$2" code="$3"
    {
        echo ""
        echo "Timestamp: $(date -Iseconds)"
        echo "Threshold: ${FAIL_UNDER:-from coverage config}${FAIL_UNDER:+%}"
        echo "Status: ${status}"
    } >> "$RESULTS_FILE"
    echo ""
    echo "${status}: ${message}"
    echo "Full report: ${RESULTS_FILE}"
    exit "$code"
}

# ─── Report result ───────────────────────────────────────────────────────────────
case "$PYTEST_EXIT" in
    0) ;;
    1) finish "FAIL" "Tests failed; coverage was not evaluated." 1 ;;
    5) finish "ERROR" "No tests were collected." 3 ;;
    *) finish "ERROR" "pytest exited with code ${PYTEST_EXIT} (interrupted, internal or usage error)." 3 ;;
esac

REPORT_ARGS=()
[[ -n "$FAIL_UNDER" ]] && REPORT_ARGS=(--fail-under="${FAIL_UNDER}")
set +e
"${COVERAGE_CMD[@]}" report "${REPORT_ARGS[@]+"${REPORT_ARGS[@]}"}" > /dev/null
REPORT_EXIT=$?
set -e
case "$REPORT_EXIT" in
    0)
        echo "HTML report: ${HTML_DIR}/index.html"
        finish "PASS" "Tests passed and coverage meets the threshold." 0 ;;
    2)
        echo "Review missing coverage in: ${HTML_DIR}/index.html"
        finish "FAIL" "Coverage is below the threshold." 2 ;;
    *)
        finish "ERROR" "coverage report exited with code ${REPORT_EXIT}." 3 ;;
esac
