#!/usr/bin/env bash
# Auto-format all Python code with black.
set -euo pipefail
cd "$(dirname "$0")/.."
uv run black backend main.py
