---
description: Mandatory pre-PR local verification, PR description structure, Copilot review request, and CI status check watch loop.
---
# Pull Request Lifecycle & Quality Gate Policy

1. **Mandatory Local Pre-PR Verification**:
   - Run local verification checks (`pre-commit run --all-files`, `./build_for_ultimaker.sh`, unit tests) before creating or updating any PR.
2. **Pull Request Creation & Description Standards**:
   - All PRs MUST be created in **DRAFT** state (`gh pr create --draft`).
   - Title MUST start with bracketed Jira ticket key: `[PROJECT-KEY] <Descriptive Title>`.
   - Description MUST include active Jira issue link, changes overview, support warning block if applicable, and empty human reviewer checklist:
     `- [ ] Initiating developer reviewed AI-generated code`
3. **Copilot AI Review & CI Watch Loop**:
   - Request Copilot AI review on PR (`gh pr comment <PR> --body "@github-copilot review"`).
   - Monitor CI status checks (`gh pr checks <PR> --watch`).
4. **Human Merge Policy**:
   - Merging is strictly restricted to human developers. AI agents MUST NOT merge PRs.
