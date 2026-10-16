#!/usr/bin/env bash
set -euo pipefail

# Ensure target directories exist
mkdir -p .claude/hooks .opencode .agents/hooks .github/hooks .agents/rules .claude/rules .opencode/rules

# Copy hook configs across platforms
cp -f .agents/hooks.json .claude/hooks.json 2>/dev/null || true

# Symlink AGENTS.md for platforms expecting CLAUDE.md
if [ -f AGENTS.md ]; then
  ln -sf AGENTS.md CLAUDE.md
fi

echo "Synced Quad-Agent configurations and rule structures successfully."
