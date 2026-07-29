---
description: Jira work tracking and commit message standards.
---
# Jira & Git Commit Standards

1. **Jira Work Tracking**:
   - All branches MUST reference an active Jira ticket starting with project key `UC` (e.g. `UC-123_description`).
2. **Commit Title Standard**:
   - Every commit title MUST start with bracketed Jira ticket key: `[UC-XXXX] <Descriptive Title>`.
   - Do NOT use semantic commit prefixes (`feat:`, `fix:`, `chore:`, `refactor:`) in commit or PR titles.
3. **Pull Request Policy**:
   - Always open PRs in **DRAFT** state.
   - Merging is strictly restricted to human developers.
