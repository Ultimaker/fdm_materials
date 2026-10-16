#!/usr/bin/env bash
set -e

# Run quick format/linter checks if available
if command -v flake8 >/dev/null 2>&1; then
  git diff --name-only --cached | grep -E '\.py$' | xargs -r flake8 --select=E9,F63,F7,F82 || true
fi
