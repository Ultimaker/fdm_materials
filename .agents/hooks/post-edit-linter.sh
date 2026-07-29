#!/usr/bin/env bash
set -e

# Read stdin payload if available
PAYLOAD=""
if [ ! -t 0 ]; then
  PAYLOAD="$(cat)"
fi

# Extract target file paths from command line arguments or stdin JSON payload
TARGET_FILES=""

if [ "$#" -gt 0 ]; then
  TARGET_FILES="$*"
elif [ -n "$PAYLOAD" ]; then
  TARGET_FILES="$(echo "$PAYLOAD" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tool_call = data.get('toolCall', {})
    args = tool_call.get('args', {})
    path = args.get('TargetFile') or args.get('AbsolutePath') or ''
    if path:
        print(path)
except Exception:
    pass
" 2>/dev/null || true)"
fi

if command -v pre-commit &> /dev/null; then
  if [ -n "$TARGET_FILES" ]; then
    pre-commit run --files $TARGET_FILES || true
  else
    pre-commit run || true
  fi
fi

echo "{}"
exit 0
