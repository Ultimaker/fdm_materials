#!/usr/bin/env bash
set -euo pipefail

# Ensure target directories exist
mkdir -p .claude/hooks .opencode .agents/hooks .github/hooks   .agents/rules .claude/rules .opencode/rules   .agents/agents .claude/agents .opencode/agents .github/agents

# Copy hook configs across platforms
cp -f .agents/hooks.json .claude/hooks.json 2>/dev/null || true

# Symlink AGENTS.md for platforms expecting CLAUDE.md
if [ -f AGENTS.md ]; then
  ln -sf AGENTS.md CLAUDE.md
fi

# Symlink rules from .agents/rules to .claude/rules and .opencode/rules
if [ -d .agents/rules ]; then
  for rulefile in .agents/rules/*.md; do
    if [ -f "$rulefile" ]; then
      base="$(basename "$rulefile")"
      ln -sf "../../.agents/rules/$base"         ".claude/rules/$base" 2>/dev/null || true
      ln -sf "../../.agents/rules/$base"         ".opencode/rules/$base" 2>/dev/null || true
    fi
  done
fi

# Symlink subagent definitions across platforms
if [ -d .agents/agents/adversarial_pr_reviewer ]; then
  src="../../.agents/agents/adversarial_pr_reviewer/agent.md"
  ln -sf "$src" ".claude/agents/adversarial_pr_reviewer.md" 2>/dev/null || true
  ln -sf "$src" ".opencode/agents/adversarial_pr_reviewer.md" 2>/dev/null || true
  ln -sf "$src" ".github/agents/adversarial_pr_reviewer.md" 2>/dev/null || true
fi

# Symlink AGENTS.md for opencode rules
if [ -f AGENTS.md ]; then
  ln -sf "../../AGENTS.md" ".opencode/rules/agents.md" 2>/dev/null || true
fi

echo "Synced Quad-Agent configurations and rule structures successfully."
