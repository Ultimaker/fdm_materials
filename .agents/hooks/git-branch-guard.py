#!/usr/bin/env python3
import subprocess
import sys

FORBIDDEN_BRANCHES = ["main", "master", "staging"]


def check_branch():
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    branch = result.stdout.strip()
    if branch in FORBIDDEN_BRANCHES:
        print(
            f"BRANCH GUARD ERROR: Cannot commit directly to "
            f"'{branch}' branch. Create a feature/bugfix branch."
        )
        sys.exit(1)


if __name__ == "__main__":
    check_branch()
