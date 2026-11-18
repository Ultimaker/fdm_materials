---
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
