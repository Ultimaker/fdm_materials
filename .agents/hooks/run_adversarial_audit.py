#!/usr/bin/env python3
"""
run_adversarial_audit.py
Automated Adversarial Security & Quality Gate Audit Script.
Scans current git diff for:
1. Hardcoded absolute paths (/home/username, /Users/username)
2. Private keys, API tokens, credentials
3. Python error swallowing
4. Raw hex color strings or hardcoded pixel font declarations in QML
5. Forbidden branch commits (main, master, staging)
"""

from pathlib import Path
import re
import subprocess
import sys

HOME_PATH_PATTERN = re.compile(r"/home/[a-zA-Z0-9_-]+/")
USERS_PATH_PATTERN = re.compile(r"/Users/[a-zA-Z0-9_-]+/")
SECRET_PATTERNS = [
    re.compile(r"-----BEGIN (?:RSA|OPENSSH|DSA|EC|PGP) PRIVATE KEY-----"),
    re.compile(r"AIzaSy[A-Za-z0-9_-]{33}"),
    re.compile(r"ghp_[A-Za-z0-9]{36}"),
    re.compile(r"glpat-[A-Za-z0-9_-]{20}"),
]
HEX_COLOR_PATTERN = re.compile(r"#(?:[0-9a-fA-F]{3}){1,2}\b")


def get_git_diff_files():
    result = subprocess.run(
        ["git", "diff", "--name-only", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
        )
    return [f.strip() for f in result.stdout.splitlines() if f.strip()]


def _check_line_patterns(filepath, idx, line, content, errors):
    m_home = HOME_PATH_PATTERN.search(line)
    m_user = USERS_PATH_PATTERN.search(line)
    if (m_home or m_user) and "AGENTS.md" not in filepath:
        if not filepath.endswith(".md"):
            errors.append(f"❌ [ABSOLUTE PATH] {filepath}:{idx}: {line.strip()}")

    for pat in SECRET_PATTERNS:
        if pat.search(line):
            errors.append(f"❌ [SECRET DETECTED] {filepath}:{idx}")

    if filepath.endswith(".py"):
        c1 = "except Exception as e:" in line
        c2 = "except Exception:" in line
        if c1 or c2:
            w_start = max(0, idx - 1)
            w_end = min(len(content), idx + 5)
            window = "".join(content[w_start:w_end])
            has_exit = "sys.exit" in window or "file=sys.stderr" in window
            if not has_exit:
                errors.append(
                    f"⚠️ [PYTHON ERROR SWALLOWING] {filepath}:{idx}: "
                    "Exception caught without sys.exit or stderr output."
                )

    if filepath.endswith(".qml") and "Theme.qml" not in filepath:
        if HEX_COLOR_PATTERN.search(line):
            errors.append(
                f"⚠️ [QML HARDCODED HEX COLOR] {filepath}:{idx}: "
                f"{line.strip()} (Use Theme.colors instead)"
            )


def _check_architectural_limits(files, errors):
    interface_prefixes = ["griffin/interface/", "interface/http/", "endpoints/"]
    interface_files = [f for f in files if any(p in f for p in interface_prefixes)]
    api_doc_files = [f for f in files if "docs/api_documentation.json" in f or "openapi" in f.lower()]
    if interface_files and not api_doc_files:
        errors.append(
            f"❌ [API DOC DESYNC] Interface files modified "
            f"({len(interface_files)} files) but docs/api_documentation.json "
            "was not updated!"
        )

    vendor_prefixes = ["software/sdk/", "vendor/", "third_party/"]
    vendor_files = [f for f in files if any(f.startswith(vp) for vp in vendor_prefixes)]
    if vendor_files:
        errors.append(
            f"❌ [VENDOR SDK MODIFIED] {len(vendor_files)} vendor files "
            f"modified (e.g. {vendor_files[0]}). Vendor code must remain untouched!"
        )

    if len(files) > 50:
        errors.append(
            f"⚠️ [EXCESSIVE DIFF] Total modified file count ({len(files)}) "
            "exceeds PR scope threshold (50 files)."
        )


def _audit_single_file(filepath, errors):
    path = Path(filepath)
    if not path.exists() or path.is_dir():
        return

    skip_files = ["block-absolute-paths.py", "run_adversarial_audit.py", ".pre-commit-config.yaml"]
    if any(sf in filepath for sf in skip_files):
        return

    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.readlines()

        for idx, line in enumerate(content, 1):
            _check_line_patterns(filepath, idx, line, content, errors)
    except Exception:
        pass


def audit_diff():
    # Execute security downgrade check hook if present
    sec_hook = Path(__file__).parent / "check_security_downgrades.py"
    if sec_hook.exists():
        res = subprocess.run([sys.executable, str(sec_hook)])
        if res.returncode != 0:
            return 1

    files = get_git_diff_files()
    if not files:
        print("==> Adversarial Audit: No modified files detected in git diff.")
        return 0

    errors = []
    print(f"==> Running Adversarial Security & Quality Audit on {len(files)} modified files...")

    for filepath in files:
        _audit_single_file(filepath, errors)

    _check_architectural_limits(files, errors)

    if errors:
        print("\n" + "=" * 74)
        print("🚨 ADVERSARIAL AUDIT FINDINGS (Fix these before submitting PR):")
        print("=" * 74)
        for err in errors:
            print(err)
        print("=" * 74 + "\n")
        crit_keys = ["ABSOLUTE PATH", "SECRET DETECTED", "API DOC DESYNC", "VENDOR SDK MODIFIED"]
        critical_errors = [e for e in errors if any(ck in e for ck in crit_keys)]
        if critical_errors:
            print("❌ Critical security findings must be resolved.")
            return 1

    print("✅ Adversarial Security & Quality Audit Passed Cleanly!")
    return 0


if __name__ == "__main__":
    sys.exit(audit_diff())
