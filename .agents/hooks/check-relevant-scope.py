#!/usr/bin/env python3
import os
import re
import subprocess
import sys

# Hook may be invoked from .agents/ (Antigravity sets cwd to the hooks.json
# directory) — always operate from the repository root.
_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if _ROOT:
    os.chdir(_ROOT)

BLOCKED_VENDOR_PATHS = [
    re.compile(r"^vendor/"),
    re.compile(r"^third_party/"),
    re.compile(r"^node_modules/"),
]

MAX_FILES_THRESHOLD = 50


def check_scope():
    res = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    staged = [f.strip() for f in res.stdout.splitlines() if f.strip()]

    blocked = []
    for f in staged:
        for vp in BLOCKED_VENDOR_PATHS:
            if vp.match(f):
                blocked.append(f)

    if blocked:
        print("SCOPE ERROR: Modifications to vendor/third-party paths blocked:")
        for b in blocked:
            print(f"  - {b}")
        sys.exit(1)

    if len(staged) > MAX_FILES_THRESHOLD:
        print(f"SCOPE WARNING: Large commit staged ({len(staged)} files). Ensure commit is focused.")


if __name__ == "__main__":
    check_scope()
