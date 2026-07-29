---
description: Universal agentic development guidelines, Jira work tracking, PR rules, and commit standards.
---

# Agentic Development Guidelines

1. **Jira Work Tracking**:
   - All feature/bugfix branches must be prefixed with the active Jira ticket key (e.g. `UC-3697_`).

2. **Git Commit Standards**:
   - Commit title format: `[UC-ID] <Descriptive Title>`.
   - Do NOT use semantic commit prefixes (`feat:`, `fix:`, `chore:`) in commit titles or PR titles.

3. **Pull Request Policy**:
   - Always open PRs in **DRAFT** state.
   - Keep PR diffs small (under 500 lines).

4. **Pre-Commit Checks**:
   - Always verify `pre-commit run --all-files` passes 100% green before staging and pushing commits.
