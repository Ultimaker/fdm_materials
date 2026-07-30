---
description: Pull request lifecycle rules, draft PR policy, PR template enforcement, and review workflows.
---
# Pull Request Lifecycle Rules

1. **Pre-PR Verification & Gate**: Run `scripts/verify_and_create_pr.sh` (pre-commit + orientation check + adversarial audit) before creating or updating any PR.
2. **Draft PR Policy**: Always open PRs in **DRAFT** state (`gh pr create --draft`). Merging is strictly restricted to human developers; AI agents must never auto-merge.
3. **Mandatory PR Template & Comprehensive Description**:
   - Every PR description **MUST** strictly follow the repository's PR template (located at `.github/PULL_REQUEST_TEMPLATE.md` or `.github/workflows/PULL_REQUEST_TEMPLATE.md`) and answer the core review questions:
     - **Why**: The problem, user request, Jira ticket (`[UC-XXXX]`), and business context driving the change.
     - **What**: High-level overview of introduced changes.
     - **How**: Architecture decisions, implementation details, and modified modules.
     - **Verification & Validation (V&V)**: Empirical test results (unit tests, integration tests, E2E checks, and visual screenshots/recordings for UI changes).
     - **PR Checklist**: Human reviewer checklist (`- [ ] Initiating developer reviewed AI-generated code`).
   - Vague, brief, or 1-sentence PR descriptions are strictly prohibited.
4. **Updating Existing PRs on Follow-up Commits**:
   - When pushing follow-up commits to an active branch with an existing Pull Request, agents **MUST** inspect the existing PR (`gh pr view` or `gh pr list --head <branch>`).
   - If the new commits add new scope, alter architecture (**How**), or require updated testing/screenshots (**V&V**), run `gh pr edit <PR_NUMBER> --body-file <updated_template>` to update the PR description so it always reflects the current state of the branch.
5. **CI Watch Loop**: After creating or updating a PR, actively monitor status checks (`gh pr checks <PR> --watch`) and fix any linter or test failures immediately before handing off to human review.
