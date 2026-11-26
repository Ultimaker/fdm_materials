#!/usr/bin/env python3
"""Session-start and pre-subagent Kanban context injector for UltiMaker Unified Motion.

Automatically surfaces:
1. Active `herdr-kanban` board state (In Progress, Ready, Blocked, Triage)
2. Active sibling claims and file overlaps from `.siblings/`
3. Unacknowledged agent-to-agent relay messages (`herdr-kanban inbox`)
4. Mandatory reminder to pass active ticket ID + claim scope when spawning subagents.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def sync_bundled_herdr_kanban() -> None:
    """Ensure the user's local herdr-kanban installation & Herdr-App GPUI mod match tools/herdr-kanban."""
    bundled = REPO_ROOT / "tools" / "herdr-kanban"
    if not (bundled / "src" / "herdr_kanban" / "__init__.py").is_file():
        return
    target = Path.home() / ".local" / "share" / "herdr-kanban"
    src_init = (bundled / "src" / "herdr_kanban" / "__init__.py").read_bytes()
    src_mod = (bundled / "mods" / "herdr-kanban" / "main.js").read_bytes()
    dst_init = target / "src" / "herdr_kanban" / "__init__.py"
    dst_mod = target / "mods" / "herdr-kanban" / "main.js"
    app_mod = Path.home() / ".config" / "herdr-app" / "mods" / "herdr-kanban" / "main.js"

    needs_sync = (
        not dst_init.is_file()
        or dst_init.read_bytes() != src_init
        or not dst_mod.is_file()
        or dst_mod.read_bytes() != src_mod
    )
    if needs_sync:
        target.mkdir(parents=True, exist_ok=True)
        for item in (
            "bin",
            "mods",
            "schema",
            "scripts",
            "skills",
            "src",
            "tests",
            "herdr-plugin.toml",
            "keys.json",
            "pyproject.toml",
            "README.md",
            "RECIPE.md",
        ):
            s = bundled / item
            d = target / item
            if s.is_dir():
                if d.exists():
                    shutil.rmtree(d)
                shutil.copytree(s, d, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
            elif s.is_file():
                shutil.copy2(s, d)
        bin_file = target / "bin" / "herdr-kanban"
        if bin_file.is_file() and os.name != "nt":
            bin_file.chmod(0o755)
        local_bin = Path.home() / ".local" / "bin"
        local_bin.mkdir(parents=True, exist_ok=True)
        link_bin = local_bin / "herdr-kanban"
        if not link_bin.exists() and bin_file.is_file():
            try:
                link_bin.symlink_to(bin_file)
            except OSError:
                shutil.copy2(bin_file, link_bin)

    if not app_mod.is_file() or app_mod.read_bytes() != src_mod:
        app_mod.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(bundled / "mods" / "herdr-kanban" / "main.js", app_mod)
        mod_toml = bundled / "mods" / "herdr-kanban" / "mod.toml"
        if mod_toml.is_file():
            shutil.copy2(mod_toml, app_mod.parent / "mod.toml")

    git_cfg = target / ".git" / "config"
    if git_cfg.is_file():
        cfg_txt = git_cfg.read_text(encoding="utf-8", errors="ignore")
        if "jellespijker/herdr-kanban" in cfg_txt:
            git_cfg.write_text(
                cfg_txt.replace("jellespijker/herdr-kanban", "Ultimaker/herdr-kanban"),
                encoding="utf-8",
            )


def find_herdr_kanban() -> str | None:
    sync_bundled_herdr_kanban()
    found = shutil.which("herdr-kanban")
    if found:
        return found
    candidate = Path.home() / ".local" / "bin" / "herdr-kanban"
    return str(candidate) if candidate.exists() else None


def read_local_siblings() -> list[dict]:
    siblings_dir = REPO_ROOT / ".siblings"
    claims = []
    if not siblings_dir.exists():
        return claims
    for path in sorted(siblings_dir.rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            claims.append({"file": str(path.relative_to(REPO_ROOT)), "data": data})
        except Exception:
            continue
    return claims


DEFAULT_CACHE_TTL_SEC = 60


def _hook_cache_path() -> Path:
    cache_root = Path(
        os.environ.get("HERDR_KANBAN_CACHE_DIR", str(Path.home() / ".cache" / "herdr-kanban"))
    )
    return cache_root / "session-board-summary.txt"


def _read_cached_board(cache_path: Path, *, ttl_sec: int, now_ts: float) -> str | None:
    try:
        if not cache_path.is_file():
            return None
        age = now_ts - cache_path.stat().st_mtime
        if ttl_sec > 0 and age < ttl_sec:
            text = cache_path.read_text(encoding="utf-8").strip()
            return text or None
    except OSError:
        return None
    return None


def _write_cached_board(cache_path: Path, text: str) -> None:
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(text, encoding="utf-8")
    except OSError:
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--subagent", action="store_true", default=False)
    args, _ = parser.parse_known_args(argv)

    ttl_sec = int(os.environ.get("HERDR_KANBAN_HOOK_CACHE_TTL_SEC", str(DEFAULT_CACHE_TTL_SEC)))
    cache_path = _hook_cache_path()
    now_ts = time.time()

    print("=== UltiMaker Unified Motion — herdr-kanban Session Context ===")
    if args.subagent:
        cached = _read_cached_board(cache_path, ttl_sec=max(ttl_sec * 10, 600), now_ts=now_ts)
        if cached:
            print(cached)
        else:
            print("  (Subagent mode: skipping live GitHub API calls; using local .siblings/ state)")
    else:
        cached = _read_cached_board(cache_path, ttl_sec=ttl_sec, now_ts=now_ts)
        if cached:
            print(cached)
        else:
            kanban_bin = find_herdr_kanban()
            if kanban_bin:
                board_proc = subprocess.run(
                    [kanban_bin, "board", "--cwd", str(REPO_ROOT)],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=15,
                )
                if board_proc.returncode == 0 and board_proc.stdout.strip():
                    summary = board_proc.stdout.strip()
                    print(summary)
                    _write_cached_board(cache_path, summary)
                else:
                    print("  (Offline or GitHub API unreachable; checking local .siblings/ cache)")
            else:
                print("  herdr-kanban binary not found on PATH.")

    siblings = read_local_siblings()
    if siblings:
        print("\n--- Local Active Sibling Claims (.siblings/) ---")
        for item in siblings:
            d = item["data"]
            issue = d.get("issue_number") or d.get("issue") or item["file"]
            repo = d.get("repo_alias") or d.get("repo") or "unimotion"
            owner = d.get("owner") or "agent"
            files = d.get("touched_files") or []
            print(f"  * {repo}#{issue} (@{owner}) -> files: {', '.join(files) if files else '(none listed)'}")

    print(
        "\n[MANDATORY LINKED-KNOWLEDGE & SUBAGENT RULES]:\n"
        "1. Before designing or editing code for a ticket, resolve its Linked-Knowledge Brief:\n"
        "     ./unimotion knowledge unimotion#<id>\n"
        "   (surfaces Role MOCs, L1-L3 Architecture notes, Domain Glossary terms, ADRs, Lean 4 proofs,\n"
        "    UltiCortex skills, and required Obsidian/Lean4 deliverables by domain:*, type:*, trl:*, access:*).\n"
        "2. Before completing a ticket (`herdr-kanban done`), verify deliverables & zero-sorry/wikilink gates:\n"
        "     ./unimotion knowledge --check unimotion#<id>\n"
        "3. Whenever you spawn a subagent (invoke_subagent / Task), pass the active herdr-kanban ticket ID,\n"
        "   Jira key, worktree path, sibling file claims, and the `./unimotion knowledge` brief!"
    )
    print("====================================================================")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
