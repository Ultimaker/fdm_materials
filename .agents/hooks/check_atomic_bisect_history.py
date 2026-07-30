#!/usr/bin/env python3
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


def check_history():
    res = subprocess.run(
        ["git", "log", "origin/main..HEAD", "--oneline"],
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        return

    commits = [l.strip() for l in res.stdout.splitlines() if l.strip()]
    fixup_keywords = ["fixup!", "squash!", "WIP", "work in progress", "temp"]

    dirty = []
    for c in commits:
        if any(kw in c.lower() for kw in fixup_keywords):
            dirty.append(c)

    if dirty:
        print("HISTORY WARNING: Temporary/WIP commits detected before push:")
        for d in dirty:
            print(f"  - {d}")
        print("Consider squashing/cleaning history (`git rebase -i`) before review.")


if __name__ == "__main__":
    check_history()
