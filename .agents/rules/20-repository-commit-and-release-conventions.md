# Repository Specific Commit & Release Conventions

## 1. Explanatory Commit Bodies
Every non-trivial commit MUST include a commit body beneath the subject line explaining the rationale, context, or architectural impact of the change.

## 2. Commit Scope Limits
Commits MUST be tightly scoped. Ideally, commits touch <5 files. Any commit touching more than 35 files requires explicit justification in the commit body explaining why the change cannot be split into atomic commits.

## 3. Merge Topology Preservation
This repository uses PR merge commits. Do not force push or rebase published remote branches once pull requests are open.

## 4. Release Versioning Standards
Release tags follow bare semantic versions (e.g. `5.13.0`). When bumping versions, ensure `conanfile.py` and CPack/CMake version declarations move together in the same commit.
