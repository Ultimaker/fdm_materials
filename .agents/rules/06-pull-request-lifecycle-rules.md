---
description: Pull request lifecycle rules, draft PR policy, and review workflows.
---
# Pull Request Lifecycle Rules

1. **Pre-PR Verification**: Run `scripts/verify_and_create_pr.sh` (pre-commit + adversarial audit) before creating or updating any PR.
2. **Draft PR Policy**: Always open PRs as DRAFT (`gh pr create --draft`).
3. **Title & Description**: Title starts with `[UC-XXXX]`. Description includes the Jira link, a changes overview, visual evidence for UI changes, and an empty human reviewer checklist:
   `- [ ] Initiating developer reviewed AI-generated code`
4. **CI Watch Loop**: After pushing, monitor checks (`gh pr checks <PR> --watch`) and fix failures before requesting review.
5. **Human Merge Only**: Merging is strictly restricted to human developers. Agents must never auto-merge.
