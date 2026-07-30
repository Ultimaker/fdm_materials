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

# Base-branch drift is the single most common source of a PR that opens
# already conflicting. The hook is advisory by design — it cannot know whether
# this repository integrates by merge or by rebase — so surface it here, where
# a PR is about to be opened, rather than leaving it installed and uncalled.
if [ -f .agents/hooks/check_upstream_alignment.py ]; then
    python3 .agents/hooks/check_upstream_alignment.py || true
fi

if [ -f .agents/hooks/check_security_downgrades.py ]; then
    python3 .agents/hooks/check_security_downgrades.py || {
        echo "❌ Security downgrade detected!"; exit 1; }
fi

echo "==> Verifying credential and environment file isolation..."
if git status --porcelain | grep -qE '\.env|\.env\.local'; then
    echo "❌ ERROR: Un-ignored or staged .env/.env.local file detected in git status!"
    echo "    Credentials must NEVER be staged or committed to git."
    exit 1
fi

echo "✅ All verification checks passed cleanly!"

# Locate PR template
PR_TEMPLATE=""
for cand in .github/PULL_REQUEST_TEMPLATE.md .github/pull_request_template.md .github/workflows/PULL_REQUEST_TEMPLATE.md; do
    if [ -f "$cand" ]; then
        PR_TEMPLATE="$cand"
        break
    fi
done

if command -v gh >/dev/null 2>&1; then
    CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || true)
    if [ -n "$CURRENT_BRANCH" ]; then
        EXISTING_PR=$(gh pr list --head "$CURRENT_BRANCH" --json number --jq '.[0].number' 2>/dev/null || true)
        if [ -n "$EXISTING_PR" ] && [ "$EXISTING_PR" != "null" ]; then
            echo "==> Active PR #${EXISTING_PR} detected for branch '${CURRENT_BRANCH}'."
            echo "    Ensure PR description covers: Why, What, How, Verification & Validation (V&V), and PR Checklist."
            echo "    To update existing PR description: gh pr edit ${EXISTING_PR} --body-file <file>"
        else
            echo "==> No active PR found for branch '${CURRENT_BRANCH}'."
            if [ -n "$PR_TEMPLATE" ]; then
                echo "    Use template at '${PR_TEMPLATE}' when opening Draft PR:"
                echo "    gh pr create --draft --template '${PR_TEMPLATE}'"
            else
                echo "    Open Draft PR with: gh pr create --draft"
            fi
        fi
    fi
fi
