---
description: Universal agentic development guidelines, Jira work tracking, PR rules, commit standards, and empirical verification gates.
---

# Agentic Development Guidelines

1. **Jira Work Tracking**:
   - All feature/bugfix branches must be prefixed with the active Jira ticket key (e.g. `UC-3697_` or `NP-XXXX_`).

2. **Git Commit Standards**:
   - Commit title format: `[UC-ID] <Descriptive Title>` or `[NP-ID] <Descriptive Title>`.
   - Do NOT use semantic commit prefixes (`feat:`, `fix:`, `chore:`) in commit titles or PR titles.

3. **Pull Request Policy**:
   - Always open PRs in **DRAFT** state.
   - Keep PR diffs small (under 500 lines).

4. **Pre-Commit Checks**:
   - Always verify `pre-commit run --all-files` passes 100% green before staging and pushing commits.

5. **Empirical Browser & Visual Verification Gate**:
   - For UI, frontend, or end-to-end sandbox workflows, agents **MUST** execute live browser verification via `playwright-cli open <URL>` and capture screenshot evidence before declaring task completion.

6. **Container Build & Asset Loader Safety**:
   - Favor Debian-native apt packages (`python3-pymongo`) over unstable external apt repos in Dockerfiles.
   - Ensure pre-bundled frontend assets (`.zip` files, WebAssembly binaries) are configured in Vite asset loaders (`assetsInclude: ['**/*.ufp', '**/*.zip']`) and excluded from `optimizeDeps` when pre-compiled.
