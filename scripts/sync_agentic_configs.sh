#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

echo "==> Synchronizing Agentic AI Configurations across Claude, Antigravity/Gemini, Copilot, and OpenCode..."

# Ensure target directories exist
mkdir -p .claude/rules .claude/commands .opencode/rules .opencode/commands

# Cross-platform symlink helper using Python
create_symlink() {
  local target_file="$1"
  local link_dir="$2"
  local link_name="$3"

  python3 -c "
import os, sys
target = os.path.abspath(sys.argv[1])
link_dir = os.path.abspath(sys.argv[2])
link_path = os.path.join(link_dir, sys.argv[3])
rel_target = os.path.relpath(target, link_dir)
if os.path.islink(link_path) or os.path.exists(link_path):
    os.remove(link_path)
os.symlink(rel_target, link_path)
" "$target_file" "$link_dir" "$link_name"
}

# 1. Symlink Rules (.agents/rules -> .claude/rules & .opencode/rules)
for rule in .agents/rules/*.md; do
  [ -e "$rule" ] || continue
  base="$(basename "$rule")"
  create_symlink "$rule" ".claude/rules" "$base"
  create_symlink "$rule" ".opencode/rules" "$base"
done

# 2. Symlink Workflows (.agents/workflows -> .claude/commands & .opencode/commands)
for wf in .agents/workflows/*.md; do
  [ -e "$wf" ] || continue
  base="$(basename "$wf")"
  create_symlink "$wf" ".claude/commands" "$base"
  create_symlink "$wf" ".opencode/commands" "$base"
done

echo "==> Agentic configuration synchronization complete!"
