#!/usr/bin/env python3
import sys
import json
import re
from pathlib import Path

ABSOLUTE_PATH_PATTERNS = [
    (r'/home/[a-zA-Z0-9_.-]{2,}/', "Prohibited Linux host home directory path"),
    (r'/Users/[a-zA-Z0-9_.-]{2,}/', "Prohibited macOS host user directory path"),
    (r'C:\\Users\\[a-zA-Z0-9_.-]{2,}\\', "Prohibited Windows host user directory path"),
]

def check_text(text, filename=""):
    # Strip markdown backticked example strings
    cleaned_text = re.sub(r'`[^`]*`', '', text)
    for pattern, reason in ABSOLUTE_PATH_PATTERNS:
        if re.search(pattern, cleaned_text):
            return True, f"Found hardcoded absolute path matching pattern: {pattern} ({reason})"
    return False, ""

def main():
    # 1. Check file arguments if invoked by pre-commit (sys.argv[1:])
    if len(sys.argv) > 1:
        failed = False
        for filepath_str in sys.argv[1:]:
            p = Path(filepath_str)
            if not p.is_file() or p.name == "block-absolute-paths.py":
                continue
            try:
                content = p.read_text(encoding="utf-8", errors="ignore")
                has_error, reason = check_text(content, filename=p.name)
                if has_error:
                    print(f"Error in {filepath_str}: {reason}", file=sys.stderr)
                    failed = True
            except Exception:
                pass
        if failed:
            sys.exit(1)
        sys.exit(0)

    # 2. Check JSON payload if invoked by tool hook via stdin
    payload = {}
    if not sys.stdin.isatty():
        try:
            payload = json.load(sys.stdin)
        except Exception:
            pass

    args_str = json.dumps(payload)
    has_error, reason = check_text(args_str)
    if has_error:
        print(json.dumps({"decision": "deny", "reason": reason}))
        sys.exit(2)

    print(json.dumps({"decision": "allow"}))
    sys.exit(0)

if __name__ == "__main__":
    main()
