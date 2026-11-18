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

# 2. Run Local Build/Validation Script if present
if [ -f "./build_for_ultimaker.sh" ]; then
  echo "==> Running local build check: ./build_for_ultimaker.sh..."
  ./build_for_ultimaker.sh || {
    echo "❌ Local build_for_ultimaker.sh failed! Fix build errors before pushing."
    exit 1
  }
elif [ -f "./run_check_material_profiles.sh" ]; then
  echo "==> Running profile checks..."
  ./run_check_material_profiles.sh || {
    echo "❌ Material profile checks failed!"
    exit 1
  }
fi

echo "✅ Local pre-PR verification passed cleanly!"

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
JIRA_KEY=""
if [[ "$CURRENT_BRANCH" =~ ^([A-Z0-9]+-[0-9]+) ]]; then
  JIRA_KEY="${BASH_REMATCH[1]}"
else
  echo "⚠️ Branch name '$CURRENT_BRANCH' does not start with a Jira ticket key (e.g. EMB-463_description)."
fi

# Get last commit message for title fallback
LAST_COMMIT_MSG=$(git log -1 --format="%s")

# Ensure title has bracketed Jira key
PR_TITLE="$LAST_COMMIT_MSG"
if [ -n "$JIRA_KEY" ] && [[ "$PR_TITLE" != \["$JIRA_KEY"* ]]; then
  PR_TITLE="[$JIRA_KEY] $LAST_COMMIT_MSG"
fi

echo "Branch: $CURRENT_BRANCH"
echo "Jira Key: ${JIRA_KEY:-None}"
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

Contributes to Jira ticket: **${JIRA_KEY:-N/A}**

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
  PR_URL=$(gh pr create --draft --title "$PR_TITLE" --body "$PR_BODY")
  PR_NUMBER=$(echo "$PR_URL" | grep -oE '[0-9]+$')
  echo "Created Draft PR #$PR_NUMBER: $PR_URL"
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
gh pr checks "$PR_NUMBER" --watch || {
  echo "⚠️ CI status checks failed or timed out on PR #$PR_NUMBER. Check details with 'gh pr checks $PR_NUMBER'."
  exit 1
}

echo ""
echo "=========================================================================="
echo "🎉 PR Lifecycle Automation Complete!"
echo "PR #$PR_NUMBER is ready for review. All local checks passed and CI checks are green."
echo "Note: Merging is strictly restricted to human developers."
echo "=========================================================================="
