#!/usr/bin/env bash
set -euo pipefail

echo "==> Running Pre-PR Verification & Quality Gate Audit..."
if command -v pre-commit >/dev/null 2>&1; then
    pre-commit run --all-files || { echo "❌ Pre-commit checks failed!"; exit 1; }
fi

echo "==> Checking orientation docs are actually filled in..."
for doc in AGENTS.md DESIGN.md; do
    [ -f "$doc" ] || continue
    n=$(grep -c "TODO(agent)" "$doc" || true)
    if [ "$n" -gt 0 ]; then
        echo "[X] $doc still has $n unfilled TODO(agent) marker(s)."
        echo "    An orientation document full of placeholders is worse than none:"
        echo "    agents read it, learn nothing, and trust it anyway."
        echo "    Fill the sections from the repository before opening a PR:"
        grep -n "TODO(agent)" "$doc" | head -10
        exit 1
    fi
done

if [ -f .agents/hooks/run_adversarial_audit.py ]; then
    python3 .agents/hooks/run_adversarial_audit.py || { echo "❌ Adversarial audit failed!"; exit 1; }
fi

echo "✅ All verification checks passed cleanly!"
