#!/usr/bin/env python3
<<<<<<< HEAD
import os
import subprocess
import sys

# Hook may be invoked from .agents/ (Antigravity sets cwd to the hooks.json
# directory) — always operate from the repository root.
_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if _ROOT:
    os.chdir(_ROOT)

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


=======
import sys, subprocess

FORBIDDEN_BRANCHES = ["main", "master", "staging"]

def check_branch():
    result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
    branch = result.stdout.strip()
    if branch in FORBIDDEN_BRANCHES:
        print(f"BRANCH GUARD ERROR: Cannot commit directly to '{branch}' branch. Create a feature/bugfix branch.")
        sys.exit(1)

>>>>>>> origin/UC-3697_platform_emulation_and_seeding
if __name__ == "__main__":
    check_branch()
