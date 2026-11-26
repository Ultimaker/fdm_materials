#!/usr/bin/env python3
"""UltiMaker Unified Motion — Linked-Knowledge & Ticket Deliverable Gate Checker.

Validates that work on a Kanban ticket (`unimotion#<id>`) satisfies the required
Obsidian Vault deliverables, `[[wikilink]]` graph integrity, Lean 4 `zero sorry`
invariants, and `access:public` IP boundaries before `herdr-kanban done`.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from suggest_ulticortex_skills import (
    DOCS_DIR,
    REPO_ROOT,
    WIKILINK_RE,
    load_vault_index,
    resolve_knowledge_brief,
)

SORRY_RE = re.compile(r"\bsorry\b")
ACCESS_RE = re.compile(r'^access:\s*["\']?(public|internal|proprietary)["\']?\s*$', re.M)
TRL_RE = re.compile(r'^trl:\s*["\']?(concept|experimental|production)["\']?\s*$', re.M)


def check_vault_frontmatter_taxonomy(fix: bool = False) -> list[str]:
    """Ensure every Markdown note in `docs/` declares valid `access:` and `trl:` metadata.

    Strictly read-only by default (ADR-0015 / ISO 27001 A.5.3); only mutates files when `fix=True`.
    """
    errors: list[str] = []
    if not DOCS_DIR.exists():
        return errors
    for md_path in sorted(DOCS_DIR.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
        rel_md = md_path.relative_to(REPO_ROOT).as_posix()
        rel_docs = md_path.relative_to(DOCS_DIR).as_posix()
        has_acc = bool(ACCESS_RE.search(text))
        has_trl = bool(TRL_RE.search(text))
        if fix and (not has_acc or not has_trl) and text.startswith("---\n"):
            end_idx = text.find("\n---\n", 4)
            if end_idx != -1:
                fm = text[4:end_idx]
                body = text[end_idx + 5 :]
                if not has_acc and not re.search(r"^access\s*:", fm, re.M):
                    acc = (
                        "proprietary"
                        if (
                            rel_docs.startswith("03-IP-Portfolio/")
                            or rel_docs.startswith("04-Lean4-Proofs/")
                            or "IP and Patent Portfolio" in rel_docs
                            or "Lean 4 Formal Verification" in rel_docs
                        )
                        else (
                            "public"
                            if any(rel_docs.startswith(p) for p in ("05-Glossary/00-", "05-Glossary/01-", "05-Glossary/02-"))
                            else "internal"
                        )
                    )
                    fm += f'\naccess: "{acc}"'
                    has_acc = True
                if not has_trl and not re.search(r"^trl\s*:", fm, re.M):
                    trl = (
                        "experimental"
                        if any(h in rel_docs.lower() for h in ("gpu", "4th-engine", "free-air", "freeair", "tensegrity", "id22", "id25", "disktree"))
                        else "production"
                    )
                    fm += f'\ntrl: "{trl}"'
                    has_trl = True
                text = f"---\n{fm}\n---\n{body}"
                md_path.write_text(text, encoding="utf-8")
        if not has_acc:
            errors.append(f"{rel_md}: missing or invalid `access: public|internal|proprietary` frontmatter")
        if not has_trl:
            errors.append(f"{rel_md}: missing or invalid `trl: concept|experimental|production` frontmatter")
    return errors


def strip_lean_comments(text: str) -> str:
    text = re.sub(r"/-.*?-/", "", text, flags=re.DOTALL)
    text = re.sub(r"--[^\n]*", "", text)
    return text


def check_zero_sorrys() -> list[str]:
    errors: list[str] = []
    proofs_dir = REPO_ROOT / "proofs" / "Proofs"
    if not proofs_dir.exists():
        return errors
    for lean_file in sorted(proofs_dir.rglob("*.lean")):
        raw = lean_file.read_text(encoding="utf-8", errors="replace")
        cleaned = strip_lean_comments(raw)
        if SORRY_RE.search(cleaned):
            rel = lean_file.relative_to(REPO_ROOT).as_posix()
            errors.append(f"Lean 4 proof `{rel}` contains forbidden `sorry` token.")
    return errors


def check_vault_wikilinks() -> list[str]:
    """Verify modified or newly added markdown files in `docs/` have no broken `[[wikilinks]]`."""
    errors: list[str] = []
    vault = load_vault_index()
    known_stems = set(vault.keys())
    known_rel_no_ext = {n.rel_path.removeprefix("docs/").removesuffix(".md") for n in vault.values()}

    proc = subprocess.run(
        ["git", "status", "--porcelain", "docs/"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    changed_docs: list[Path] = []
    for line in proc.stdout.splitlines():
        if len(line) < 4:
            continue
        rel_str = line[3:].strip().strip('"')
        if " -> " in rel_str:
            rel_str = rel_str.split(" -> ", 1)[1].strip('"')
        cand = REPO_ROOT / rel_str
        if cand.is_file() and cand.suffix == ".md":
            changed_docs.append(cand)

    for md_path in changed_docs:
        raw_text = md_path.read_text(encoding="utf-8", errors="replace")
        text = re.sub(r"```.*?```", "", raw_text, flags=re.DOTALL)
        text = re.sub(r"`[^`\n]+`", "", text)
        rel_md = md_path.relative_to(REPO_ROOT).as_posix()
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip().rstrip("\\").strip()
            if not target:
                continue
            if any(
                target.endswith(ext)
                for ext in (".svg", ".png", ".jpg", ".jpeg", ".pdf", ".html", ".canvas", ".tar.gz", ".zip", ".ufp", ".gcode")
            ):
                asset_path = DOCS_DIR / target
                if not asset_path.exists():
                    errors.append(f"{rel_md}: broken asset wikilink `[[{target}]]`")
                continue
            stem = Path(target).name
            if stem not in known_stems and target not in known_rel_no_ext:
                errors.append(f"{rel_md}: unresolved Obsidian wikilink `[[{target}]]`")
    return errors


def check_ticket_specific_deliverables(ticket_ref: str, fix: bool = False) -> tuple[dict, list[str], list[str]]:
    brief = resolve_knowledge_brief(ticket_ref, ticket_ref=ticket_ref)
    facets = brief["facets"]
    type_label = facets["type"]
    access_label = facets["access"]
    errors: list[str] = []
    passed: list[str] = []

    sorry_errs = check_zero_sorrys()
    if sorry_errs:
        errors.extend(sorry_errs)
    else:
        passed.append("All `proofs/Proofs/**/*.lean` files have `0 sorry`s")

    link_errs = check_vault_wikilinks()
    if link_errs:
        errors.extend(link_errs)
    else:
        passed.append("Obsidian Vault `[[wikilink]]` integrity verified on modified `docs/` notes")

    fm_errs = check_vault_frontmatter_taxonomy(fix=fix)
    if fm_errs:
        errors.extend(fm_errs[:10])
    else:
        passed.append("All Obsidian Vault notes declare valid `access:` and `trl:` frontmatter")

    if access_label == "access:public":
        leak_hook = REPO_ROOT / ".agents" / "hooks" / "check_public_repo_ip_leak.py"
        if leak_hook.exists():
            proc = subprocess.run([sys.executable, str(leak_hook)], cwd=str(REPO_ROOT), capture_output=True, text=True, check=False)
            if proc.returncode != 0:
                errors.append(f"Public IP leak check failed: {(proc.stdout + proc.stderr).strip()}")
            else:
                passed.append("Public repo IP hygiene (`check_public_repo_ip_leak.py`) passed")

    if type_label == "type:forensics":
        forensics_dir = DOCS_DIR / "06-Investigation-and-Quality-Reports" / "L1-01-Print-Artifact-Forensics"
        reports = list(forensics_dir.glob("Report - *.md")) if forensics_dir.exists() else []
        proof_dir = REPO_ROOT / "proofs" / "Proofs" / "Forensics"
        forensic_leans = list(proof_dir.glob("*.lean")) if proof_dir.exists() else []
        if not reports:
            errors.append(
                "type:forensics requires a forensic report in "
                "`docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics/Report - <Case> Forensics.md`"
            )
        else:
            passed.append(f"Found {len(reports)} forensic report(s) in `L1-01-Print-Artifact-Forensics/`")
        if not forensic_leans:
            errors.append("type:forensics requires a machine-checked Lean 4 proof in `proofs/Proofs/Forensics/<Case>Proofs.lean`")
        else:
            passed.append(f"Found {len(forensic_leans)} forensic Lean 4 proof suite(s) in `proofs/Proofs/Forensics/`")

    if type_label == "type:proof":
        proof_notes_dir = DOCS_DIR / "04-Lean4-Proofs"
        notes = list(proof_notes_dir.rglob("Lean4 - *.md")) if proof_notes_dir.exists() else []
        if not notes:
            errors.append("type:proof requires a companion `Lean4 - <Name>Proofs.md` note in `docs/04-Lean4-Proofs/`")
        else:
            passed.append(f"Found {len(notes)} Lean 4 proof vault note(s) in `docs/04-Lean4-Proofs/`")

    return brief, passed, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate linked-knowledge & Obsidian/Lean4 deliverables for a ticket.")
    parser.add_argument("ticket", nargs="?", default="unimotion", help="Kanban ticket ref (e.g. unimotion#10) or query")
    parser.add_argument("--fix", action="store_true", help="Explicitly backfill missing access:/trl: frontmatter on docs/ notes")
    args = parser.parse_args()

    brief, passed, errors = check_ticket_specific_deliverables(args.ticket, fix=args.fix)
    t = brief.get("ticket")
    header = f"unimotion#{t['number']}" if t else args.ticket
    print(f"=== Deliverable & Linked-Knowledge Gate Check ({header}) ===")
    print(f"Facets: {', '.join(brief['facets']['domains'])} | {brief['facets']['type']} | {brief['facets']['trl']} | {brief['facets']['access']}")
    for p in passed:
        print(f"  [PASS] {p}")
    for e in errors:
        print(f"  [FAIL] {e}")
    print("\nRequired Definition-of-Done Checklist for this Ticket:")
    for item in brief["verification_choices"]["required_deliverables"]:
        print(f"  - [ ] {item}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
