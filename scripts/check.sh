#!/usr/bin/env bash
# Run all quality checks (formatting check + offline tests). Non-zero exit on failure.
set -euo pipefail
cd "$(dirname "$0")/.."
echo "==> black --check"
uv run black --check backend main.py
echo "==> pytest (offline)"
(cd backend && uv run pytest test -m "not functional" -q)
echo "All quality checks passed."
