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

INTERFACE_PATTERNS = [
    "interface/http/",
    "endpoints/",
    "routes/",
    "controllers/",
]
DOC_PATTERNS = ["docs/api_documentation.json", "openapi", "swagger"]


def check_api_doc_sync():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    staged_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    if not staged_files:
        return

    interface_changed = [
        f for f in staged_files if any(p in f for p in INTERFACE_PATTERNS)
    ]
    doc_changed = [
        f for f in staged_files if any(p in f.lower() for p in DOC_PATTERNS)
    ]

    if interface_changed and not doc_changed:
        print("=" * 80)
        print("WARNING: API ENDPOINT MODIFICATION DETECTED")
        print("The following endpoint/interface files were modified:")
        for f in interface_changed:
            print(f"  - {f}")
        print("Ensure API documentation / OpenAPI schemas are kept in sync.")
        print("=" * 80)


if __name__ == "__main__":
    check_api_doc_sync()
