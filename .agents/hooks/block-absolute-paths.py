#!/usr/bin/env python3
import os
import re
import subprocess
import sys
# --- shared detection patterns (generated from one source) ----------------
# Kept in a single partial so the pre-flight guard, the pre-commit scanners and
# the adversarial audit cannot drift apart.

SECRET_PATTERNS = [
    # PKCS#1 / OpenSSH / PGP and the PKCS#8 forms that `openssl genpkey` and
    # `ssh-keygen -m PKCS8` emit by default — the latter were previously missed.
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----"),
    re.compile(r"-----BEGIN(?: ENCRYPTED)? PRIVATE KEY-----"),
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),          # Google API key
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),        # GitHub tokens
    re.compile(r"glpat-[A-Za-z0-9_-]{20}"),           # GitLab PAT
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),      # Slack
    re.compile(r"sk-[A-Za-z0-9]{32,}"),               # OpenAI-style
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),              # AWS access key id
]

HOME_PATH_PATTERN = re.compile(r"/home/[a-zA-Z0-9_-]+/")
USERS_PATH_PATTERN = re.compile(r"/Users/[a-zA-Z0-9_-]+/")
ABSOLUTE_PATH_PATTERNS = [HOME_PATH_PATTERN, USERS_PATH_PATTERN]


# Hook may be invoked from .agents/ (Antigravity sets cwd to the hooks.json
# directory) — always operate from the repository root.
_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if _ROOT:
    os.chdir(_ROOT)


def check_staged_files():
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True,
    )
    files = [f for f in result.stdout.splitlines() if f.strip()]

    failed = False
    for filepath in files:
        # Only the hook itself and the generated rule files are exempt.
        # Exempting every .md let absolute paths through in documentation,
        # which rule 02 explicitly forbids.
        if filepath.endswith("block-absolute-paths.py") or \
                filepath.startswith(".agents/rules/"):
            continue
        try:
            with open(
                filepath, "r", encoding="utf-8", errors="ignore"
            ) as f:
                for idx, line in enumerate(f, 1):
                    if any(p.search(line) for p in ABSOLUTE_PATH_PATTERNS):
                        print(
                            f"SECURITY ERROR: Absolute path detected in "
                            f"{filepath}:{idx}: {line.strip()}"
                        )
                        failed = True
        except Exception:
            pass

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    check_staged_files()
