#!/usr/bin/env python3
"""
check_upstream_alignment.py
---------------------------
Deterministic pre-PR check verifying that the local branch is up-to-date with its base branch.
"""

import subprocess
import sys


def run_cmd(cmd, timeout=5) -> str:
    try:
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""


def main():
    # Detect current branch
    current_branch = run_cmd(["git", "branch", "--show-current"])
    if not current_branch or current_branch in ["main", "master", "staging"]:
        sys.exit(0)

    # Fetch origin silently with short timeout
    run_cmd(["git", "fetch", "origin"], timeout=8)

    # Detect base branch
    base_branch = None
    for cand in ["staging", "main", "master"]:
        if run_cmd(["git", "rev-parse", "--verify", f"origin/{cand}"]):
            base_branch = f"origin/{cand}"
            break

    if not base_branch:
        sys.exit(0)

    # Check how many commits current branch is behind base_branch
    behind_count = run_cmd(["git", "rev-list", "--count", f"HEAD..{base_branch}"])
    if behind_count and behind_count.isdigit() and int(behind_count) > 0:
        print(f"\n⚠️  BRANCH ALIGNMENT WARNING: Current branch '{current_branch}' is {behind_count} commit(s) behind '{base_branch}'.")
        print(f"    Please rebase or merge with '{base_branch}' before opening or updating PRs:")
        print(f"    git rebase {base_branch}  (or run /sync-base)\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
