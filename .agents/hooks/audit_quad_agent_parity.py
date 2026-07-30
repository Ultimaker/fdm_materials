#!/usr/bin/env python3
"""
audit_quad_agent_parity.py

Asserts that every hook a repository qualifies for is present in every platform
rendering that supports hooks.

The required set is derived from the generated configs themselves rather than
hardcoded. A hardcoded list is how the previous version came to require six
hooks while the bootstrap installed eleven — and the five it never checked were
the five added most recently.

Platform support, verified rather than assumed:
  * Antigravity  .agents/hooks.json
  * Claude Code  .claude/settings.json
  * Copilot      .github/hooks/copilot-hooks.json
  * OpenCode     has no command-hook mechanism, so it is checked for
                 configuration presence only; its enforcement floor is
                 pre-commit.
"""

import json
import sys
from pathlib import Path


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"[X] {path}: cannot be read ({exc})")
        return None


def script_name(command: str) -> str:
    """Reduce a platform-specific command line to the hook script's basename.

    Only managed hooks — commands that route through .agents/hooks/ — take part
    in the parity contract. A platform may additionally wire repository-local
    hooks living elsewhere (scripts/hooks/, an inline shell guard); those speak
    that platform's dialect by construction and demanding they exist on every
    other platform would force either a false failure or a broken port. The
    old last-token heuristic also choked on compound shell commands, reporting
    '}' as a missing hook.
    """
    if not command:
        return ""
    for token in command.split():
        # Explicitly routed through the managed hooks directory (Claude,
        # Copilot), or a bare script name resolved against it (Antigravity
        # runs hook commands from .agents/hooks/ itself).
        if ".agents/hooks/" in token:
            return token.rsplit("/", 1)[-1]
        if "/" not in token and token.endswith((".py", ".sh")):
            return token
    return ""


def antigravity_hooks(repo: Path):
    data = load_json(repo / ".agents" / "hooks.json")
    if data is None:
        return None
    names = set()
    for group in data.values():
        if not isinstance(group, dict):
            continue
        for entries in group.values():
            for entry in entries:
                for hook in entry.get("hooks", []):
                    names.add(script_name(hook.get("command", "")))
    return names - {""}


def claude_hooks(repo: Path):
    data = load_json(repo / ".claude" / "settings.json")
    if data is None:
        return None
    names = set()
    for blocks in (data.get("hooks") or {}).values():
        for block in blocks:
            for hook in block.get("hooks", []):
                names.add(script_name(hook.get("command", "")))
    return names - {""}


def copilot_hooks(repo: Path):
    data = load_json(repo / ".github" / "hooks" / "copilot-hooks.json")
    if data is None:
        return None
    names = set()
    for entries in (data.get("hooks") or {}).values():
        for hook in entries:
            names.add(script_name(hook.get("bash", "")))
    return names - {""}


def audit_parity(repo_path: Path) -> bool:
    repo = repo_path.resolve()
    print(f"==> Auditing agent-platform parity in: {repo.name}")
    passed = True

    platforms = {
        "Antigravity": antigravity_hooks(repo),
        "Claude Code": claude_hooks(repo),
        "Copilot": copilot_hooks(repo),
    }

    available = [hooks for hooks in platforms.values() if hooks]
    if not available:
        print("[X] No platform hook configuration found — run the bootstrap first.")
        return False

    # The union is what this repository qualifies for; every platform must carry
    # all of it. This catches a hook added to one config and forgotten in another.
    expected = set().union(*available)
    for name, hooks in platforms.items():
        if hooks is None:
            print(f"[X] {name}: configuration missing or unreadable")
            passed = False
            continue
        missing = expected - hooks
        if missing:
            print(f"[X] {name}: missing {sorted(missing)}")
            passed = False
        else:
            print(f"[ok] {name}: {len(hooks)} hook(s)")

    # Every referenced script must exist, or the config entry is a silent no-op.
    hooks_dir = repo / ".agents" / "hooks"
    for script in sorted(expected):
        if not (hooks_dir / script).exists():
            print(f"[X] {script} is referenced by a platform config "
                  "but is not installed")
            passed = False

    # ...and the reverse: a hook installed but called by nothing is dead code
    # that reads as enforcement. This is how check_upstream_alignment.py sat in
    # .agents/hooks/ enforcing nothing while a PR opened 21 commits behind its
    # base. Scan every place a hook can legitimately be invoked from.
    config_callers = ""
    for caller in (repo / ".pre-commit-config.yaml",
                   repo / "scripts" / "verify_and_create_pr.sh",
                   repo / ".claude" / "settings.json",
                   repo / ".agents" / "hooks.json",
                   repo / ".github" / "hooks" / "copilot-hooks.json",
                   repo / "opencode.json"):
        if caller.exists():
            config_callers += caller.read_text(errors="ignore")

    # A hook invoked by a sibling hook is wired too (post-edit-linter.sh calls
    # suggest-skills.py), so sibling sources count as callers — but a script
    # must not vouch for itself, hence the per-script exclusion below.
    hook_sources = {}
    if hooks_dir.is_dir():
        for path in sorted(hooks_dir.iterdir()):
            if path.is_file() and path.suffix in (".py", ".sh"):
                hook_sources[path.name] = path.read_text(errors="ignore")

    # The auditor is an entry point, run by hand and by the PR gate's
    # instructions rather than referenced from a config.
    ENTRY_POINTS = {"audit_quad_agent_parity.py"}

    for script in sorted(hook_sources):
        if script in ENTRY_POINTS:
            continue
        siblings = "".join(src for name, src in hook_sources.items()
                           if name != script)
        if script not in config_callers + siblings:
            print(f"[X] {script} is installed but referenced by no "
                  "config or script — it enforces nothing")
            passed = False

    if not (repo / "opencode.json").exists():
        print("[X] OpenCode: opencode.json missing")
        passed = False
    else:
        print("[ok] OpenCode: configured (no command-hook mechanism; "
              "its enforcement floor is pre-commit)")

    for required in (".pre-commit-config.yaml", ".aiignore", "AGENTS.md"):
        if not (repo / required).exists():
            print(f"[X] {required} is missing")
            passed = False

    print("==> Parity audit " + ("PASSED" if passed else "FAILED"))
    return passed


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    if not audit_parity(target):
        sys.exit(1)


if __name__ == "__main__":
    main()
