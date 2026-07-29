#!/usr/bin/env python3
import sys
import json
import re
import subprocess

PROTECTED_BRANCHES = ["main", "master", "staging", "production"]

def get_current_branch():
    try:
        res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True, check=True)
        return res.stdout.strip()
    except Exception:
        return ""

def main():
    branch = get_current_branch()
    payload = {}
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
        except Exception:
            pass

    payload_str = json.dumps(payload)
    is_git_commit_or_push = bool(re.search(r'git\s+.*(?:commit|push)', payload_str, re.IGNORECASE))

    if branch in PROTECTED_BRANCHES and is_git_commit_or_push:
        print(json.dumps({"decision": "deny", "reason": f"Direct commits or pushes to protected branch '{branch}' are strictly prohibited by repo safety rules."}))
        sys.exit(2)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
