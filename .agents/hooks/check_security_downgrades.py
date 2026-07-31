#!/usr/bin/env python3
"""
check_security_downgrades.py
----------------------------
Deterministic pre-commit & pre-PR hook script to detect and block security feature downgrades in staged diffs.
"""

import re
import subprocess
import sys

SECURITY_DOWNGRADE_PATTERNS = [
    (r"signInRequired\s*[:=]\s*false", "signInRequired disabled"),
    (r"needs_authentication\s*[:=]\s*false", "needs_authentication disabled"),
    (r"verify\s*[:=]\s*False", "SSL/TLS verification disabled"),
    (r"ssl_verify\s*[:=]\s*False", "ssl_verify disabled"),
    (r"check_permissions\s*[:=]\s*false", "check_permissions disabled"),
    (r"authorized\s*[:=]\s*false", "authorization disabled"),
]


def get_staged_diff() -> str:
    try:
        res = subprocess.run(
            ["git", "diff", "--cached", "-U0"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True
        )
        return res.stdout
    except Exception:
        return ""


def main():
    diff = get_staged_diff()
    if not diff:
        sys.exit(0)

    added_lines = [line for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++")]
    added_content = "\n".join(added_lines)

    violations = []
    for pattern, description in SECURITY_DOWNGRADE_PATTERNS:
        if re.search(pattern, added_content, re.IGNORECASE):
            violations.append(f"  ❌ Detected security downgrade: {description} ('{pattern}')")

    if violations:
        print("\n🔒 SECURITY GUARD VIOLATION DETECTED:")
        for v in violations:
            print(v)
        print("\nAI agents are strictly forbidden from disabling security or authentication features to bypass test/verification roadblocks.")
        print("Please revert the security feature downgrade and fix the underlying configuration/test issue properly.\n")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
