#!/usr/bin/env python3
import sys, re, subprocess

SECRET_PATTERNS = [
    re.compile(r'-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----'),
    re.compile(r'AIzaSy[A-Za-z0-9_-]{33}'),
    re.compile(r'ghp_[A-Za-z0-9]{36}'),
    re.compile(r'glpat-[A-Za-z0-9_-]{20}')
]

def check_secrets():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    files = [f for f in result.stdout.splitlines() if f.strip()]
    
    failed = False
    for filepath in files:
        if "block-secrets.py" in filepath:
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(f, 1):
                    for pattern in SECRET_PATTERNS:
                        if pattern.search(line):
                            print(f"SECURITY ERROR: Secret detected in {filepath}:{idx}")
                            failed = True
        except Exception:
            pass
            
    if failed:
        sys.exit(1)

if __name__ == "__main__":
    check_secrets()
