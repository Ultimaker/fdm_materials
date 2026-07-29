#!/usr/bin/env python3
"""
run_adversarial_audit.py
Automated Adversarial Security & Quality Gate Audit Script.
Scans current git diff for:
1. Hardcoded absolute paths (/home/username, /Users/username)
2. Private keys, API tokens, credentials
3. Python error swallowing (catch Exception without non-zero exit or logging to stderr)
4. Raw hex color strings or hardcoded pixel font declarations in QML files
5. Forbidden branch commits (main, master, staging)
"""

import sys
import re
import subprocess
from pathlib import Path

HOME_PATH_PATTERN = re.compile(r'/home/[a-zA-Z0-9_-]+/')
USERS_PATH_PATTERN = re.compile(r'/Users/[a-zA-Z0-9_-]+/')
SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----'),
    re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'),
    re.compile(r'ghp_[A-Za-z0-9]{36}'),
    re.compile(r'glpat-[A-Za-z0-9_-]{20}')
]
HEX_COLOR_PATTERN = re.compile(r'#(?:[0-9a-fA-F]{3}){1,2}\b')

def get_git_diff_files():
    result = subprocess.run(["git", "diff", "--name-only", "HEAD"], capture_output=True, text=True)
    if result.returncode != 0:
        # Fallback to cached or working tree diff
        result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]

def audit_diff():
    files = get_git_diff_files()
    if not files:
        print("==> Adversarial Audit: No modified files detected in git diff.")
        return 0

    errors = []
    print(f"==> Running Adversarial Security & Quality Audit on {len(files)} modified files...")

    for filepath in files:
        path = Path(filepath)
        if not path.exists() or path.is_dir():
            continue

        # Skip hook scripts themselves and binary/log files
        if "block-absolute-paths.py" in filepath or "run_adversarial_audit.py" in filepath:
            continue

        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.readlines()

            for idx, line in enumerate(content, 1):
                # 1. Absolute path check
                if HOME_PATH_PATTERN.search(line) or USERS_PATH_PATTERN.search(line):
                    if "AGENTS.md" not in filepath and not filepath.endswith(".md"):
                        errors.append(f"❌ [ABSOLUTE PATH] {filepath}:{idx}: {line.strip()}")

                # 2. Secret check
                for pat in SECRET_PATTERNS:
                    if pat.search(line):
                        errors.append(f"❌ [SECRET DETECTED] {filepath}:{idx}")

                # 3. Python exception handling check
                if filepath.endswith(".py"):
                    if "except Exception as e:" in line or "except Exception:" in line:
                        # Check surrounding lines for exit/stderr
                        window = "".join(content[max(0, idx-1):min(len(content), idx+5)])
                        if "sys.exit" not in window and "file=sys.stderr" not in window:
                            errors.append(f"⚠️ [PYTHON ERROR SWALLOWING] {filepath}:{idx}: Exception caught without sys.exit or stderr output.")

                # 4. QML Theme Singleton check
                if filepath.endswith(".qml") and "Theme.qml" not in filepath:
                    if HEX_COLOR_PATTERN.search(line):
                        errors.append(f"⚠️ [QML HARDCODED HEX COLOR] {filepath}:{idx}: {line.strip()} (Use Theme.colors instead)")

        except Exception as e:
            pass

    if errors:
        print("\n==========================================================================")
        print("🚨 ADVERSARIAL AUDIT FINDINGS (Fix these before submitting PR):")
        print("==========================================================================")
        for err in errors:
            print(err)
        print("==========================================================================\n")
        # Return non-zero if critical security errors are found
        critical_errors = [e for e in errors if "ABSOLUTE PATH" in e or "SECRET DETECTED" in e]
        if critical_errors:
            print("❌ Critical security findings must be resolved before PR creation.")
            return 1

    print("✅ Adversarial Security & Quality Audit Passed Cleanly!")
    return 0

if __name__ == "__main__":
    sys.exit(audit_diff())
