#!/usr/bin/env bash
# Full local quality gate. Mirrors CI (.github/workflows/ci.yml).
set -euo pipefail
echo "▶ ruff format --check"; uv run ruff format --check .
echo "▶ ruff check";          uv run ruff check .
echo "▶ pyrefly check";       uv run pyrefly check
echo "▶ pytest";              uv run pytest -m "not aws and not integration" -q
echo "✅ quality gate passed"
