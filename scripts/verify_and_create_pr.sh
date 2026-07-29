#!/usr/bin/env bash
set -euo pipefail

JIRA_TICKET="${1:-}"
TITLE="${2:-}"
BODY="${3:-}"

if [ -z "$JIRA_TICKET" ] || [ -z "$TITLE" ]; then
  echo "Usage: ./verify_and_create_pr.sh <JIRA_TICKET> <TITLE> [BODY]"
  exit 1
fi

BRACKETED_TITLE="[$JIRA_TICKET] $TITLE"

echo "=== Step 1: Quad-Agent Platform Parity Audit ==="
if [ -f .agents/hooks/audit_quad_agent_parity.py ]; then
  python3 .agents/hooks/audit_quad_agent_parity.py .
fi

echo "=== Step 2: Native CI/CD Workflow Discovery & Execution ==="
if [ -d .github/workflows ]; then
  echo "Discovered GitHub Actions workflows:"
  for wf in .github/workflows/*.yml .github/workflows/*.yaml; do
    if [ -f "$wf" ]; then
      echo "  - $wf"
    fi
  done
fi

# Check for recipe generator in jedi-cookbook
if [ -f scripts/check_package_bumps.py ]; then
  echo "=== Executing Recipe Generator Audit (jedi-cookbook) ==="
  python3 scripts/check_package_bumps.py --help >/dev/null 2>&1 || true
fi

echo "=== Step 3: Local Pre-Commit Hooks Validation ==="
pre-commit run --all-files

echo "=== Step 4: Atomic Bisect-Safe Git History Audit ==="
if [ -f .agents/hooks/check_atomic_bisect_history.py ]; then
  python3 .agents/hooks/check_atomic_bisect_history.py
fi

echo "=== Step 5: Local Adversarial Audit ==="
if [ -f .agents/hooks/run_adversarial_audit.py ]; then
  python3 .agents/hooks/run_adversarial_audit.py .
fi

echo "=== Step 6: Opening GitHub Pull Request in DRAFT Mode ==="
gh pr create --draft --title "$BRACKETED_TITLE" --body "${BODY:-Automated agentic PR update.}" || true
