---
description: Scoped changes and minimal diff enforcement guidelines to prevent scope creep, auto-formatting noise, and vendor SDK modifications.
---
# Scoped Changes & Minimal Diff Enforcement

1. **Relevant Changes Only**:
   - Every commit and Pull Request MUST contain ONLY changes that directly implement or support the active Jira ticket objective.
   - Do NOT include unrelated refactoring, cosmetic reformatting, or mass whitespace edits across files outside the immediate scope of work.

2. **Vendor SDK & Third-Party Code Protection**:
   - Never modify, format, or re-indent vendor SDKs, submodules, or third-party libraries (e.g. `software/sdk/`, `vendor/`, `third_party/`).
   - Pre-commit hooks automatically exclude vendor code. If vendor files appear in `git status`, discard them immediately:
     `git checkout -- <path>`

3. **LLM Agent Diff Relevance Validation**:
   - AI agents MUST inspect `git diff --name-only` against the base branch prior to committing or creating PRs.
   - Any file modified solely by auto-formatters, line-ending changes, or unrelated script side-effects MUST be reverted using `git checkout origin/<base_branch> -- <file>`.
   - Never commit or push out-of-scope files. Every modified file must directly serve the Jira ticket's acceptance criteria.
