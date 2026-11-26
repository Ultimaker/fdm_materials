#!/usr/bin/env python3
"""Enforce Unimotion Dev-Branch Push Guardrails across all 25 repositories.

Prevents accidental pushes to `main` or `master` on shared child repositories
(e.g. `Curator`, `cura-private-data`, `neoprep`, `ultimoco`, `opinicus`, etc.)
and blocks pushing ephemeral `kanban/*` worktree branches to `origin`.

Modes:
1. Git `pre-push` hook mode (`check_allowed_push_branch.py <remote_name> <remote_url>`):
   Reads `<local_ref> <local_sha> <remote_ref> <remote_sha>` lines from stdin.
2. CLI / PreToolUse audit mode (`--repo <name> --ref <remote_ref>` or `--audit`).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

# Canonical Unimotion target branches per repository.
# `main` is ONLY permitted on the `unimotion` meta-repo and `UltiCortex`.
# Every shared product/firmware/slicer child repository MUST push ONLY to its
# dedicated Unimotion development branch — NEVER `main` or `master`.
ALLOWED_DEV_BRANCHES: dict[str, frozenset[str]] = {
    # Meta & skills repos
    "unimotion": frozenset({"main"}),
    "UltiCortex": frozenset({"main"}),
    # Bounded Context 1: Preparation & Slicing
    "Cura-unimotion": frozenset({"CURA-13401-unimotion"}),
    "CuraEngine-unimotion": frozenset({"CURA-13401-unimotion"}),
    "Uranium-unimotion": frozenset({"CURA-13401-unimotion"}),
    "CuraFormulaeEngine-unimotion": frozenset({"CURA-13401-unimotion"}),
    "CuraMCP": frozenset({"CURA-13401-unimotion"}),
    "fdm_materials": frozenset({"CURA-13401-unimotion"}),
    "fdm_materials_private": frozenset({"CURA-13401-unimotion"}),
    "cura-private-data": frozenset({"EMB-476-feature-policy", "CURA-13401-unimotion"}),
    "ultimaker-machine-resources": frozenset({"CURA-13401-unimotion"}),
    "Curator": frozenset({"NP-1365-optimize-curator-wasm-memory-and-performance", "CURA-13401-unimotion"}),
    "neoprep": frozenset({"UC-3400_solidcraft_step_integration", "CURA-13401-unimotion"}),
    "viz-layerz": frozenset({"NP-1365-optimize-gcode-parser-memory-and-tube-geometry", "CURA-13401-unimotion"}),
    "conan-config": frozenset({"feat/switch-to-gitea-conan-registry", "CURA-13401-unimotion"}),
    # Bounded Contexts 3 & 4: SOM Host Orchestration & Real-Time Physical Control
    "ultimoco": frozenset({"EMB-476-ultimoco-cpp23"}),
    "bench-telemetry": frozenset({"EMB-476-ultimoco-cpp23"}),
    "UltiTools": frozenset({"EMB-476-ultimoco-cpp23"}),
    "opinicus": frozenset({"EMB-476-ultimoco-cpp23"}),
    "okuda": frozenset({"EMB-476-ultimoco-cpp23"}),
    "misp-service": frozenset({"EMB-476-ultimoco-cpp23"}),
    "print-process-reporting": frozenset({"EMB-476-ultimoco-cpp23"}),
    "marvin-service": frozenset({"EMB-476-ultimoco-cpp23"}),
    "python3-uc-firmware-upgrade": frozenset({"EMB-476-ultimoco-cpp23"}),
    "stardust-printer_console": frozenset({"EMB-476-ultimoco-cpp23"}),
    "misc-product-specific": frozenset({"EMB-476-ultimoco-cpp23"}),
    "jedi-build": frozenset({"EMB-476-ultimoco-cpp23"}),
    "jedi-cookbook": frozenset({"EMB-476-ultimoco-cpp23"}),
}

ZERO_SHA = "0" * 40
REMOTE_SLUG_RE = re.compile(r"[:/]([^/:]+)/([^/:]+?)(?:\.git)?$")


def detect_repo_name(remote_url: str = "") -> str:
    if remote_url:
        m = REMOTE_SLUG_RE.search(remote_url.strip())
        if m:
            return m.group(2)
    try:
        url = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        m = REMOTE_SLUG_RE.search(url)
        if m:
            return m.group(2)
    except Exception:
        pass
    try:
        common = subprocess.check_output(
            ["git", "rev-parse", "--git-common-dir"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        if common:
            return Path(common).resolve().parent.name
    except Exception:
        pass
    try:
        top = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return Path(top).name
    except Exception:
        return ""


def validate_push_ref(repo_name: str, remote_ref: str, local_sha: str = "") -> tuple[bool, str]:
    # Allow remote branch/tag deletions (cleanup of stray branches)
    if local_sha == ZERO_SHA:
        return True, f"Deletion of {remote_ref} allowed."

    # Allow Unimotion release tags (`v5.15.0-alpha.*+unimotion`, `v12.0.0-alpha.*+unimotion`), `unimotion-staging`,
    # and NeoPrep npm alpha prerelease tags (`<major>.<minor>.<patch>-alpha.<N>` on `neoprep`).
    if remote_ref.startswith("refs/tags/"):
        tag = remote_ref.removeprefix("refs/tags/")
        if "+unimotion" in tag or tag == "unimotion-staging":
            return True, f"Unimotion tag {tag} allowed."
        if repo_name == "neoprep" and re.fullmatch(r"\d+\.\d+\.\d+-alpha\.\d+", tag):
            return True, f"NeoPrep alpha prerelease tag {tag} allowed."
        return (
            False,
            f"UNIMOTION PUSH GUARD VIOLATION ({repo_name}):\n"
            f"  Refusing to push non-unimotion tag `{tag}`.",
        )

    if not remote_ref.startswith("refs/heads/"):
        return True, f"Non-head ref {remote_ref} allowed."

    branch = remote_ref.removeprefix("refs/heads/")

    # Never push local `kanban/*` worktree branches to origin
    if branch.startswith("kanban/"):
        return (
            False,
            f"UNIMOTION PUSH GUARD VIOLATION ({repo_name}):\n"
            f"  Refusing to push local worktree branch `{branch}` to remote.\n"
            "  Use `herdr-kanban done unimotion#<id>` to land directly onto the target dev branch.",
        )

    # Allow Jedi automated QA recipe branch in jedi-cookbook
    if repo_name == "jedi-cookbook" and branch == "QA_recipes_branch":
        return True, "jedi-cookbook QA_recipes_branch allowed."

    allowed = ALLOWED_DEV_BRANCHES.get(repo_name)
    if allowed is not None:
        if branch not in allowed:
            allowed_list = ", ".join(sorted(allowed))
            return (
                False,
                f"UNIMOTION PUSH GUARD VIOLATION ({repo_name}):\n"
                f"  Refusing to push to branch `{branch}` in `{repo_name}`.\n"
                f"  Allowed Unimotion branch(es) for `{repo_name}`: {allowed_list}",
            )
        return True, f"Push to `{repo_name}` branch `{branch}` allowed."

    # Fallback for any unknown child repo: never allow main or master
    if branch in {"main", "master"}:
        return (
            False,
            f"UNIMOTION PUSH GUARD VIOLATION ({repo_name}):\n"
            f"  Refusing to push to protected default branch `{branch}`.",
        )
    return True, f"Push to `{repo_name}` branch `{branch}` allowed."


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate git push target branch against Unimotion dev-branch allowlist")
    parser.add_argument("remote_name", nargs="?", default="")
    parser.add_argument("remote_url", nargs="?", default="")
    parser.add_argument("--repo", default="", help="Explicit repository name for CLI testing")
    parser.add_argument("--ref", default="", help="Explicit remote ref (e.g. refs/heads/main) for CLI testing")
    args = parser.parse_args()

    if args.ref:
        repo = args.repo or detect_repo_name(args.remote_url)
        ok, msg = validate_push_ref(repo, args.ref)
        print(msg, file=sys.stdout if ok else sys.stderr)
        return 0 if ok else 2

    repo_name = detect_repo_name(args.remote_url)
    raw_stdin = sys.stdin.read()
    for line in raw_stdin.splitlines():
        parts = line.strip().split()
        if len(parts) != 4:
            continue
        _local_ref, local_sha, remote_ref, _remote_sha = parts
        ok, msg = validate_push_ref(repo_name, remote_ref, local_sha)
        if not ok:
            print(msg, file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
