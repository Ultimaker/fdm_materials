---
<<<<<<< HEAD
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
4. **Empirical Proof Mandate**: Verification is ONLY valid when concrete empirical proof (a DOM text snapshot, test execution log, or screenshot uploaded via `gh image` attached to the walkthrough and PR body) is delivered. Agents must NEVER claim a UI feature or fix is verified without delivering empirical proof.
5. **Updating Existing PRs on Follow-up Commits**:
   - When pushing follow-up commits to an active branch with an existing Pull Request, agents **MUST** inspect the existing PR (`gh pr view` or `gh pr list --head <branch>`).
   - If the new commits add new scope, alter architecture (**How**), or require updated testing/screenshots (**V&V**), run `gh pr edit <PR_NUMBER> --body-file <updated_template>` to update the PR description so it always reflects the current state of the branch.
6. **CI Watch Loop**: After creating or updating a PR, actively monitor status checks (`gh pr checks <PR> --watch`) and fix any linter or test failures immediately before handing off to human review.
7. **Upstream Base Branch Alignment**:
   - Before staging changes, opening PRs, or pushing follow-up commits, agents **MUST** ensure the local feature branch is completely up-to-date with its base branch (`origin/staging`, `origin/main`, or `origin/master`).
   - Run `git fetch origin` and `git rebase origin/<base_branch>` (or use `/sync-base` command) to resolve any upstream changes or conflicts before proposing PR updates.
=======
description: Mandatory pre-PR local verification, PR description structure, Copilot review request, and CI status check watch loop.
---
# Pull Request Lifecycle & Quality Gate Policy

1. **Mandatory Local Pre-PR Verification**:
   - Before creating or updating any Pull Request, run local verification checks (`pre-commit run --all-files`, `./build_for_ultimaker.sh`, unit tests, linters).
   - Only create or update the PR if all local checks pass cleanly without errors.

2. **Pull Request Creation & Description Standards**:
   - All PRs MUST be created in **DRAFT** state (`gh pr create --draft`).
   - Title MUST start with the bracketed Jira ticket key: `[PROJECT-KEY] <Descriptive Title>`.
   - Description MUST include:
     - Active Jira issue link (`EMB-XXX`).
     - Overview of changes ("Why" and "How").
     - Support documentation warning block (`> [!WARNING]`) if support articles are impacted.
     - Empty human reviewer checklist at the bottom: `- [ ] Initiating developer reviewed AI-generated code`.

3. **Copilot AI Review & CI Watch Loop**:
   - Request Copilot AI review on PR (`gh pr comment <PR> --body "@github-copilot review"`).
   - Monitor CI status checks (`gh pr checks <PR> --watch`).
   - Address and resolve all Copilot review comments and threads before considering PR ready.

4. **Human Merge Policy**:
   - Merging is strictly restricted to human developers. AI agents MUST NOT merge PRs.
>>>>>>> origin/UC-3697_platform_emulation_and_seeding
