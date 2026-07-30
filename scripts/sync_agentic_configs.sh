#!/usr/bin/env bash
set -euo pipefail

# Ensure target directories exist
<<<<<<< HEAD
mkdir -p .claude/hooks .opencode .agents/hooks .github/hooks   .agents/rules .claude/rules .opencode/rules   .agents/agents .claude/agents .opencode/agents .github/agents

# Clean up broken symlinks in rules
find .claude/rules/ .opencode/rules/ -xtype l -delete 2>/dev/null || true
=======
mkdir -p .claude/hooks .opencode .agents/hooks .github/hooks .agents/rules .claude/rules .opencode/rules
>>>>>>> origin/UC-3697_platform_emulation_and_seeding

# Copy hook configs across platforms
cp -f .agents/hooks.json .claude/hooks.json 2>/dev/null || true

<<<<<<< HEAD
# Symlink AGENTS.md for platforms expecting CLAUDE.md.
# Never clobber a real CLAUDE.md, and never touch the inverse layout where
# AGENTS.md is itself a symlink to CLAUDE.md (ln -sf would fail, and under
# `set -e` that would abort the whole bootstrap).
if [ -f AGENTS.md ] && [ ! -L AGENTS.md ]; then
  if [ ! -e CLAUDE.md ]; then
    ln -s AGENTS.md CLAUDE.md
  elif [ -L CLAUDE.md ] && [ "$(readlink CLAUDE.md)" = "AGENTS.md" ]; then
    :  # already correct
  else
    echo "NOTE: CLAUDE.md exists and is not a link to AGENTS.md — left untouched."
  fi
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

# Recompile AI exclusion targets from .aiignore (no platform reads it directly)
if [ -f .aiignore ] && [ -f .agents/hooks/compile_aiignore.py ]; then
  python3 .agents/hooks/compile_aiignore.py || true
=======
# Symlink AGENTS.md for platforms expecting CLAUDE.md
if [ -f AGENTS.md ]; then
  ln -sf AGENTS.md CLAUDE.md
>>>>>>> origin/UC-3697_platform_emulation_and_seeding
fi

echo "Synced Quad-Agent configurations and rule structures successfully."
