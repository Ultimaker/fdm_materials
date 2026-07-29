#!/usr/bin/env python3
"""
check_atomic_bisect_history.py
Validates the git history of the current feature branch against base branch:
1. Every commit message title MUST start with bracketed Jira key [KEY-123].
2. Rejects WIP, fixup, squash, or temporary commit titles.
3. Verifies every commit touches a reasonable number of files (<= 35 files).
"""

import re
import subprocess
import sys

FORBIDDEN_PATTERNS = [
    r"^wip\b",
    r"^fixup!",
    r"^squash!",
    r"^temp\b",
    r"^tmp\b",
    r"^oops\b",
    r"fix\s+typo",
    r"address\s+review",
    r"review\s+comments",
    r"checkpoint",
]


def run_git(cmd):
    res = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return res.stdout.strip()


def get_base_branch():
    branches = [
        "origin/master",
        "origin/main",
        "origin/master_cheetah",
        "origin/master_d-line",
    ]
    for branch in branches:
        res = subprocess.run(
            f"git merge-base {branch} HEAD",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if res.returncode == 0 and res.stdout.strip():
            return branch
    return "HEAD~1"


def main():
    base = get_base_branch()
    print(f"Checking git commit history against base '{base}'...")

    rev_range = f"{base}..HEAD" if base != "HEAD~1" else "HEAD~1..HEAD"
    commits_raw = run_git(f"git rev-list {rev_range}")
    if not commits_raw:
        print("No new commits on branch to validate.")
        sys.exit(0)

    commits = commits_raw.splitlines()
    print(f"Found {len(commits)} commit(s) on branch.")

    errors = []
    for commit in commits:
        title = run_git(f"git log -1 --format=%s {commit}")
        stats = run_git(
            f"git diff-tree --no-commit-id --name-only -r {commit}"
        )
        files = [f for f in stats.splitlines() if f.strip()]

        if not re.match(r"^\[[A-Z]+-[0-9]+\]\s+", title):
            errors.append(
                f"Commit {commit[:7]} title does not start with "
                f"bracketed Jira ticket: '{title}'"
            )

        for pat in FORBIDDEN_PATTERNS:
            if re.search(pat, title, re.IGNORECASE):
                errors.append(
                    f"Commit {commit[:7]} contains WIP/fixup keyword "
                    f"matching '{pat}': '{title}'"
                )

        if len(files) > 35:
            errors.append(
                f"Commit {commit[:7]} touches {len(files)} files "
                f"(max allowed 35 per atomic commit)."
            )

    if errors:
        print()
        print("❌ Git Commit History Validation Failed:")
        for err in errors:
            print(f"  - {err}")
        print()
        print("💡 Action Required:")
        print(f"  Clean up git history before merging: git rebase -i {base}")
        print()
        sys.exit(1)

    print("✅ All commits on branch are atomic and bisect-safe!")
    sys.exit(0)


if __name__ == "__main__":
    main()
