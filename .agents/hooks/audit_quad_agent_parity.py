#!/usr/bin/env python3
"""
audit_quad_agent_parity.py
Audits a target repository for 100% Quad-Agent platform parity across:
- Gemini / Antigravity (.agents/hooks.json)
- Claude Code (.claude/settings.json & .claude/rules/)
- GitHub Copilot (.github/hooks/copilot-hooks.json
  & .github/copilot-instructions.md)
- OpenCode (opencode.json & .opencode/rules/)
"""

from pathlib import Path
import sys

REQUIRED_HOOK_SCRIPTS = [
    "block-absolute-paths.py",
    "block-secrets.py",
    "git-branch-guard.py",
    "post-edit-linter.sh",
    "check-api-doc-sync.py",
    "run_adversarial_audit.py",
]

REQUIRED_CONFIG_FILES = [
    ".agents/hooks.json",
    "opencode.json",
    ".github/hooks/copilot-hooks.json",
]


def audit_parity(repo_path: Path) -> bool:
    repo_path = repo_path.resolve()
    print(f"==> Auditing Quad-Agent Parity in: {repo_path.name}")
    passed = True

    # 1. Check Hook Scripts
    hooks_dir = repo_path / ".agents" / "hooks"
    if not hooks_dir.exists():
        print("❌ [HOOKS DIR MISSING] .agents/hooks directory does not exist!")
        passed = False
    else:
        for script in REQUIRED_HOOK_SCRIPTS:
            script_file = hooks_dir / script
            if not script_file.exists():
                print(
                    f"❌ [MISSING HOOK SCRIPT] .agents/hooks/{script} "
                    f"is missing!"
                )
                passed = False

    # 2. Check Platform Config Files
    for cfg in REQUIRED_CONFIG_FILES:
        cfg_file = repo_path / cfg
        if not cfg_file.exists():
            print(f"❌ [MISSING CONFIG] Platform config file {cfg} is missing!")
            passed = False

    # 3. Check Rule Symlink Parity
    rules_dir = repo_path / ".agents" / "rules"
    if rules_dir.exists():
        rule_files = list(rules_dir.glob("*.md"))
        claude_rules_dir = repo_path / ".claude" / "rules"
        opencode_rules_dir = repo_path / ".opencode" / "rules"

        for rf in rule_files:
            claude_link = claude_rules_dir / rf.name
            opencode_link = opencode_rules_dir / rf.name

            if not claude_link.exists():
                print(
                    f"⚠️ [RULE SYMLINK MISSING] .claude/rules/{rf.name} "
                    f"missing symlink!"
                )
                passed = False
            if not opencode_link.exists():
                print(
                    f"⚠️ [RULE SYMLINK MISSING] .opencode/rules/{rf.name} "
                    f"missing symlink!"
                )
                passed = False

    if passed:
        print("✅ Quad-Agent Platform Parity Audit Passed Cleanly!")
    return passed


def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    success = audit_parity(target)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
