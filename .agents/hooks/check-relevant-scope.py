#!/usr/bin/env python3
import re
import subprocess
import sys

BLOCKED_VENDOR_PATHS = [
    re.compile(r"^software/sdk/"),
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
    staged_files = [f.strip() for f in res.stdout.splitlines() if f.strip()]
    if not staged_files:
        return

    blocked_files = []
    for f in staged_files:
        for pattern in BLOCKED_VENDOR_PATHS:
            if pattern.search(f):
                blocked_files.append(f)

    if blocked_files:
        print("=" * 80)
        print("ERROR: VENDOR SDK / THIRD-PARTY FILE MODIFICATION BLOCKED!")
        print("The following vendor/SDK files are staged for commit:")
        for f in blocked_files[:10]:
            print(f"  - {f}")
        if len(blocked_files) > 10:
            print(f"  ... and {len(blocked_files) - 10} more files.")
        print("Vendor SDKs and third-party code must remain untouched.")
        print("=" * 80)
        sys.exit(1)

    if len(staged_files) > MAX_FILES_THRESHOLD:
        print("=" * 80)
        print(
            f"ERROR: POTENTIAL SCOPE CREEP DETECTED! "
            f"({len(staged_files)} files staged, max is {MAX_FILES_THRESHOLD})"
        )
        print("Commit contains changes across too many files.")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    check_scope()
