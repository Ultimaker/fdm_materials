#!/usr/bin/env python3
import sys, re, subprocess

def check_staged_files():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    files = [f for f in result.stdout.splitlines() if f.strip()]

    home_pattern = re.compile(r'/home/[a-zA-Z0-9_-]+/')
    users_pattern = re.compile(r'/Users/[a-zA-Z0-9_-]+/')

    failed = False
    for filepath in files:
        if "block-absolute-paths.py" in filepath:
            continue
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                for idx, line in enumerate(f, 1):
                    if home_pattern.search(line) or users_pattern.search(line):
                        print(f"SECURITY ERROR: Absolute path detected in {filepath}:{idx}: {line.strip()}")
                        failed = True
        except Exception:
            pass

    if failed:
        sys.exit(1)

if __name__ == "__main__":
    check_staged_files()
