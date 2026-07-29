---
description: Guidelines for producing clean, small, meaningful atomic commits that maintain bisect-safety across git history.
---
# Atomic & Bisect-Safe Commit Standards

1. **Small & Meaningful Atomic Commits**:
   - Each commit MUST represent a single, self-contained, logical unit of change (e.g., a discrete feature component, bug fix, refactor, or test addition).
   - Do NOT combine unrelated changes into a single monolithic commit.
   - Do NOT leave 'WIP', 'fixup!', 'squash!', 'address review', or 'typo fix' commits on published PR branches.

2. **Bisect-Safety Guarantee**:
   - EVERY individual commit on a feature branch MUST compile, build cleanly, and pass unit tests (`pre-commit`, `pytest`, build scripts).
   - Never commit broken intermediate code that would break `git bisect` when searching for regressions in the future.

3. **History Cleanup Before Review**:
   - Before moving a PR out of DRAFT or requesting human review, clean up branch history using interactive rebase (`git rebase -i`):
     - Fixup/squash temporary or review-fix commits into the original relevant atomic commit.
     - Ensure every commit title follows `[PROJECT-KEY-123] <Descriptive Title>`.
