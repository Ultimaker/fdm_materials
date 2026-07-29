---
description: Mandatory pre-PR local verification, PR description structure, Copilot review request, and CI status check watch loop.
---
# Pull Request Lifecycle & Quality Gate Policy

1. **Mandatory Local Pre-PR Verification**:
   - Run local verification checks (`pre-commit run --all-files`, `./build_for_ultimaker.sh`, unit tests) before creating or updating any PR.
2. **Mandatory Adversarial Pre-PR Self-Audit**:
   - Before proposing or pushing any PR, the AI agent MUST execute a self-adversarial security and compliance audit on `git diff`:
     - **Security & Paths**: Verify zero hardcoded absolute user paths (`<home>/<username>/`, `<Users>/<username>/`) and zero committed secrets.
     - **Error Handling**: Verify Python scripts catch exceptions cleanly, log to `sys.stderr`, and exit with non-zero exit codes (`sys.exit(1)`).
     - **Design Parity**: Verify QML visual changes strictly reference `Theme.qml` singletons (`Theme.colors`, `Theme.margins`, `Theme.sizes`, `Theme.fonts`) without hardcoded raw hex color strings or magic integers.
     - **Pre-commit Cleanliness**: Ensure `pre-commit run --all-files` passes 100% cleanly without bypasses or skipped hooks.
3. **Pull Request Creation & Description Standards**:
   - All PRs MUST be created in **DRAFT** state (`gh pr create --draft`).
   - Title MUST start with bracketed Jira ticket key: `[PROJECT-KEY] <Descriptive Title>`.
   - Description MUST include active Jira issue link, changes overview, support warning block if applicable, and empty human reviewer checklist:
     `- [ ] Initiating developer reviewed AI-generated code`
4. **Copilot AI Review & CI Watch Loop**:
   - Request Copilot AI review on PR (`gh pr comment <PR> --body "@github-copilot review"`).
   - Monitor CI status checks (`gh pr checks <PR> --watch`).
5. **Human Merge Policy**:
   - Merging is strictly restricted to human developers. AI agents MUST NOT merge PRs.
