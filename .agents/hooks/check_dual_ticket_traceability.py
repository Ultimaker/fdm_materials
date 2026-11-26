#!/usr/bin/env python3
"""Non-Negotiable Dual-Ticket Traceability Guard (Jira + GitHub Kanban).

Enforces Rule 02 across `unimotion` and all 15 child repositories in three modes:
1. Git `commit-msg` hook mode:
   `python3 check_dual_ticket_traceability.py <path-to-.git/COMMIT_EDITMSG>`
   Blocks commits unless:
   - The commit title (subject line) is clean (NO Jira keys or GitHub `#<id>` in the title).
   - The commit message body/description cites BOTH a relevant Jira key (`CURA-13401`, `EMB-476`,
     or an explicitly requested ticket) AND a GitHub Kanban issue reference (`unimotion#1`,
     `CuraEngine-unimotion#2`, `#5`, etc.).
2. Agent `PreToolUse` hook mode (reads JSON from stdin or `--command`):
   Inspects shell commands containing `git commit` or `herdr-kanban deposit` / `gh issue create`:
   - `git commit -m ...` must keep the title clean and cite both a Jira key and a GitHub Kanban `#<id>` in the body.
   - `herdr-kanban deposit` / `gh issue create` must keep `--title` clean and cite a relevant Jira key in `--body`.
3. CLI Audit mode (`--check-message "<msg>"`):
   Verifies a commit message string.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import sys
from pathlib import Path

JIRA_KEY_RE = re.compile(r"\b[A-Z][A-Z0-9]{1,9}-[1-9][0-9]*\b")
GH_ISSUE_RE = re.compile(r"(?:[A-Za-z0-9_.-]+)?#[1-9][0-9]*\b")


def validate_commit_message(msg: str) -> tuple[bool, str]:
    """Verify commit title is clean and commit body cites both a Jira key and a GitHub Kanban ID."""
    # Strip git comment lines starting with '# ' (while keeping '#123' tokens on non-comment lines)
    active_lines = [line for line in msg.splitlines() if not line.lstrip().startswith("# ")]
    cleaned = "\n".join(active_lines).strip()

    # Allow automatic git merge/revert headers
    if (
        cleaned.startswith("Merge branch ")
        or cleaned.startswith("Merge pull request ")
        or cleaned.startswith('Revert "')
    ):
        return True, "Merge/revert commit allowed."

    lines = cleaned.splitlines()
    subject = lines[0].strip() if lines else ""

    title_jira = JIRA_KEY_RE.search(subject)
    title_gh = GH_ISSUE_RE.search(subject)
    if title_jira or title_gh:
        found = [m.group(0) for m in (title_jira, title_gh) if m]
        return (
            False,
            "NON-NEGOTIABLE DUAL-TICKET TRACEABILITY VIOLATION (Rule 02):\n"
            f"  Ticket numbers ({', '.join(found)}) must NOT be in the commit title.\n"
            "  Keep the commit title clean and move Jira + GitHub ticket mentions to the commit body:\n"
            "    Build Structurizr C4 model and umbrella harness\n\n"
            "    Jira: EMB-476\n"
            "    Refs: unimotion#1",
        )

    body = "\n".join(lines[1:]).strip()
    has_jira = bool(JIRA_KEY_RE.search(body))
    has_gh = bool(GH_ISSUE_RE.search(body))

    if has_jira and has_gh:
        jira_match = JIRA_KEY_RE.search(body).group(0)  # type: ignore[union-attr]
        gh_match = GH_ISSUE_RE.search(body).group(0)  # type: ignore[union-attr]
        return True, f"Dual-ticket traceability verified (Jira: {jira_match}, GitHub Kanban: {gh_match})."

    missing = []
    if not has_jira:
        missing.append("relevant Jira ticket key in commit body (e.g. CURA-13401 for Cura, EMB-476 for firmware)")
    if not has_gh:
        missing.append("GitHub Kanban ticket ID in commit body (e.g. unimotion#1, CuraEngine-unimotion#2)")

    return (
        False,
        "NON-NEGOTIABLE DUAL-TICKET TRACEABILITY VIOLATION (Rule 02):\n"
        f"  Missing: {', '.join(missing)}\n"
        "  Every commit message MUST keep the title clean and cite BOTH a relevant Jira ticket\n"
        "  and the GitHub Kanban ticket in the commit message body/description.\n"
        "  Example (firmware):\n"
        "    Build Structurizr C4 model and umbrella harness\n\n"
        "    Jira: EMB-476\n"
        "    Refs: unimotion#1\n"
        "  Example (Cura/slicer):\n"
        "    Remove .lean files from public slicer repo\n\n"
        "    Jira: CURA-13401\n"
        "    Refs: CuraEngine-unimotion#2",
    )


def _extract_flag_values(command_str: str, flags: tuple[str, ...]) -> list[str]:
    """Extract values passed to CLI flags like -m/--message or --title using shlex."""
    try:
        tokens = shlex.split(command_str)
    except ValueError:
        return []
    values: list[str] = []
    i = 0
    while i < len(tokens):
        tok = tokens[i]
        matched = False
        for flag in flags:
            if tok == flag and i + 1 < len(tokens):
                values.append(tokens[i + 1])
                i += 2
                matched = True
                break
            if tok.startswith(f"{flag}="):
                values.append(tok.split("=", 1)[1])
                i += 1
                matched = True
                break
        if not matched:
            i += 1
    return values


def validate_shell_command(command_str: str) -> tuple[bool, str]:
    """Inspect a shell command in PreToolUse mode for `git commit` or `herdr-kanban deposit`."""
    if re.search(r"\bgit\s+commit\b", command_str) and ("-m " in command_str or "--message" in command_str):
        msg_parts = _extract_flag_values(command_str, ("-m", "--message"))
        if msg_parts:
            full_msg = "\n\n".join(msg_parts)
            ok, reason = validate_commit_message(full_msg)
            if not ok:
                return False, reason
        else:
            ok, reason = validate_commit_message(command_str)
            if not ok:
                return False, reason

    if re.search(r"\b(?:herdr-kanban\s+deposit|gh\s+issue\s+create)\b", command_str):
        titles = _extract_flag_values(command_str, ("--title", "-t"))
        for title in titles:
            title_jira = JIRA_KEY_RE.search(title)
            title_gh = GH_ISSUE_RE.search(title)
            if title_jira or title_gh:
                found = [m.group(0) for m in (title_jira, title_gh) if m]
                return (
                    False,
                    "NON-NEGOTIABLE DUAL-TICKET TRACEABILITY VIOLATION (Rule 02):\n"
                    f"  Ticket numbers ({', '.join(found)}) must NOT be in the Kanban issue `--title`.\n"
                    "  Keep `--title` clean and put the relevant Jira key (e.g. Jira: EMB-476 or Jira: CURA-13401)\n"
                    "  in `--body` instead.",
                )
        if not JIRA_KEY_RE.search(command_str):
            return (
                False,
                "NON-NEGOTIABLE DUAL-TICKET TRACEABILITY VIOLATION (Rule 02):\n"
                "  Every Kanban ticket (`herdr-kanban deposit` / `gh issue create`) MUST include\n"
                "  the relevant Jira ticket key (e.g. Jira: EMB-476 or Jira: CURA-13401) in its `--body`.",
            )

    if re.search(r"\bgit\b[^\n;&|]*\bpush\b[^\n;&|]*\b(?<!:)kanban/issue-\d+\b", command_str):
        return (
            False,
            "UNIMOTION PUSH GUARD VIOLATION:\n"
            "  Never push ephemeral `kanban/issue-*` worktree branches to `origin`.\n"
            "  Use `herdr-kanban done unimotion#<id>` to land onto the repository's Unimotion dev branch.",
        )

    return True, "Command complies with Rule 02 dual-ticket traceability."


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Jira + GitHub Kanban dual-ticket traceability (Rule 02)")
    parser.add_argument("commit_msg_file", nargs="?", help="Path to .git/COMMIT_EDITMSG (git commit-msg hook mode)")
    parser.add_argument("--check-message", help="Validate an explicit commit message string")
    parser.add_argument("--check-command", help="Validate a shell command string (PreToolUse mode)")
    parser.add_argument("--pre-tool-use", action="store_true", help="Read Claude/Gemini PreToolUse JSON payload on stdin")
    args = parser.parse_args()

    if args.check_message is not None:
        ok, report = validate_commit_message(args.check_message)
        stream = sys.stdout if ok else sys.stderr
        print(report, file=stream)
        return 0 if ok else 2

    if args.check_command is not None:
        ok, report = validate_shell_command(args.check_command)
        stream = sys.stdout if ok else sys.stderr
        print(report, file=stream)
        return 0 if ok else 2

    if args.pre_tool_use:
        raw = sys.stdin.read().strip()
        if not raw:
            return 0
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return 0
        tool_input = payload.get("tool_input") or payload.get("arguments") or {}
        cmd = (
            tool_input.get("command")
            or tool_input.get("CommandLine")
            or tool_input.get("cmd")
            or ""
        )
        if cmd:
            ok, report = validate_shell_command(cmd)
            if not ok:
                print(report, file=sys.stderr)
                return 2
        return 0

    if args.commit_msg_file:
        msg_path = Path(args.commit_msg_file)
        if not msg_path.exists():
            return 0
        msg = msg_path.read_text(encoding="utf-8", errors="replace")
        ok, report = validate_commit_message(msg)
        stream = sys.stdout if ok else sys.stderr
        print(report, file=stream)
        return 0 if ok else 1

    print("[DUAL-TICKET GUARD READY] Enforcing clean titles + Jira ([A-Z]+-[0-9]+) & GitHub Kanban (<repo>#<id>) in body.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
