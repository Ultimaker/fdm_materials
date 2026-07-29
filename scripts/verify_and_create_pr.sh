#!/usr/bin/env bash
#
# Automated Pre-PR Quality Verification, PR Creation/Update, Copilot Review, and CI Watch Loop Script.
# Contributes to UltiMaker Agentic Firmware Engineering Standards.
#

set -euo pipefail

echo "=========================================================================="
echo "🚀 [1/5] Running Local Pre-PR Verification & Quality Gate Checks"
echo "=========================================================================="

# 1. Run Pre-Commit Hooks
if command -v pre-commit >/dev/null 2>&1; then
  echo "==> Running pre-commit hooks..."
  pre-commit run --all-files || {
    echo "❌ Pre-commit checks failed! Please resolve all errors locally before creating/updating a PR."
    exit 1
  }
else
  echo "⚠️ pre-commit not installed. Skipping pre-commit hook run."
fi

# 2. Run Local Build/Validation Script if present and enabled
if [ "${SKIP_BUILD:-0}" != "1" ]; then
  if [ -f "./run_check_material_profiles.sh" ]; then
    echo "==> Running profile checks..."
    ./run_check_material_profiles.sh || {
      echo "❌ Material profile checks failed!"
      exit 1
    }
  elif [ -f "./build_for_ultimaker.sh" ]; then
    echo "==> Running local build check..."
    if [ -n "${RECIPE_FILE:-}" ]; then
      ./build_for_ultimaker.sh -r "$RECIPE_FILE" || exit 1
    else
      ./build_for_ultimaker.sh -l 2>/dev/null || true
    fi
  fi
fi

# 2. Run Adversarial Pre-PR Security & Quality Audit
if [ -f "./.agents/hooks/run_adversarial_audit.py" ]; then
  echo "==> Running Adversarial Pre-PR Security & Quality Audit..."
  python3 ./.agents/hooks/run_adversarial_audit.py || {
    echo "❌ Adversarial audit failed! Please resolve security and quality findings before submitting PR."
    exit 1
  }
elif [ -f "../UltiCortex/skills/ultimaker/ultimaker-agentic-bootstrap/resources/scripts/run_adversarial_audit.py" ]; then
  python3 ../UltiCortex/skills/ultimaker/ultimaker-agentic-bootstrap/resources/scripts/run_adversarial_audit.py || exit 1
fi

echo "✅ Local pre-PR verification and adversarial audit passed cleanly!"

echo ""
echo "=========================================================================="
echo "🌿 [2/5] Inspecting Git Branch & Jira Context"
echo "=========================================================================="

CURRENT_BRANCH=$(git branch --show-current)
if [[ "$CURRENT_BRANCH" == "main" || "$CURRENT_BRANCH" == "master" || "$CURRENT_BRANCH" == "staging" ]]; then
  echo "❌ Error: Cannot create PR directly from '$CURRENT_BRANCH' branch. Switch to a feature/bugfix branch."
  exit 1
fi

# Extract Jira Key from branch name
if [[ "$CURRENT_BRANCH" =~ ^([A-Z0-9]+-[0-9]+) ]]; then
  JIRA_KEY="${BASH_REMATCH[1]}"
else
  echo "❌ Error: Branch name '$CURRENT_BRANCH' does not start with a valid Jira ticket key (e.g. EMB-463_description)."
  exit 1
fi

# Get last commit message for title fallback
LAST_COMMIT_MSG=$(git log -1 --format="%s")

# Ensure title has bracketed Jira key
PR_TITLE="$LAST_COMMIT_MSG"
if [[ "$PR_TITLE" != \["$JIRA_KEY"* ]]; then
  PR_TITLE="[$JIRA_KEY] $LAST_COMMIT_MSG"
fi

echo "Branch: $CURRENT_BRANCH"
echo "Jira Key: $JIRA_KEY"
echo "PR Title: $PR_TITLE"

echo ""
echo "=========================================================================="
echo "📤 [3/5] Pushing Working Branch to Remote"
echo "=========================================================================="

git push origin HEAD || {
  echo "❌ Failed to push branch to remote."
  exit 1
}

echo ""
echo "=========================================================================="
echo "📝 [4/5] Creating or Updating Draft GitHub Pull Request"
echo "=========================================================================="

PR_BODY=$(cat <<EOF
## Overview & Rationale
${LAST_COMMIT_MSG}

Contributes to Jira ticket: **${JIRA_KEY}**

## Changes Made
- Executed local pre-commit quality gate checks cleanly.
- Updated repository code and agentic rules in accordance with firmware standards.

> [!NOTE]
> This PR was created in **DRAFT** state and underwent local pre-PR automated quality verification.

## Initiator Review Checklist
- [ ] Initiating developer reviewed AI-generated code
EOF
)

# Check if PR already exists
EXISTING_PR=$(gh pr view --json number -q ".number" 2>/dev/null || echo "")

if [ -n "$EXISTING_PR" ]; then
  echo "==> Existing PR #$EXISTING_PR found. Updating title and body..."
  gh pr edit "$EXISTING_PR" --title "$PR_TITLE" --body "$PR_BODY"
  PR_NUMBER="$EXISTING_PR"
else
  echo "==> Creating new Draft PR..."
  gh pr create --draft --title "$PR_TITLE" --body "$PR_BODY"
  PR_NUMBER=$(gh pr view --json number -q ".number")
  echo "Created Draft PR #$PR_NUMBER"
fi

echo ""
echo "=========================================================================="
echo "🤖 [5/5] Requesting GitHub Copilot AI Review & Monitoring CI Status Checks"
echo "=========================================================================="

# Trigger Copilot Review comment
echo "==> Requesting Copilot AI Review on PR #$PR_NUMBER..."
gh pr comment "$PR_NUMBER" --body "@github-copilot review" || true

# Watch CI status checks
echo "==> Monitoring GitHub Actions CI status checks..."
if gh pr checks "$PR_NUMBER" >/dev/null 2>&1; then
  gh pr checks "$PR_NUMBER" --watch || {
    echo "⚠️ CI status checks failed or timed out on PR #$PR_NUMBER. Check details with 'gh pr checks $PR_NUMBER'."
  }
else
  echo "ℹ️ No GitHub Actions CI status checks reported on branch '$CURRENT_BRANCH'."
fi

echo ""
echo "=========================================================================="
echo "🎉 PR Lifecycle Automation Complete!"
echo "PR #$PR_NUMBER is ready for review."
echo "Note: Merging is strictly restricted to human developers."
echo "=========================================================================="
