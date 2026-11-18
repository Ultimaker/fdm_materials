---
description: Atomic, bisect-safe commit rules.
---
# Atomic & Bisect-Safe Commits

1. **Atomic Commits**: Each commit must be a single self-contained, logical unit of work that compiles and passes tests independently.
2. **Bisect-Safe**: Never break the build or unit test suite in intermediate commits to preserve `git bisect` functionality.
3. **History Cleanup**: Squash WIP/fixup commits (`git rebase -i`) before a PR leaves DRAFT.
