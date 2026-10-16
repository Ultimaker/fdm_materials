---
description: Scoped changes and minimal diff guidelines for code changes.
---
# Scoped Changes & Minimal Diffs

1. **Strict Scope Compliance**: Make changes strictly relevant to the active Jira ticket task. Avoid scope creep.
2. **Diff Relevance Validation**: Inspect `git diff --name-only` against the base branch before committing. Revert files touched only by formatters or side-effects: `git checkout origin/<base_branch> -- <file>`.
3. **No Unrelated Refactoring**: Do not modify whitespace, formatting, or code in files unrelated to the task. Never edit `vendor/`, `third_party/`, or submodule trees.
