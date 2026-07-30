#!/usr/bin/env bash
<<<<<<< HEAD
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
=======
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
>>>>>>> origin/UC-3697_platform_emulation_and_seeding
