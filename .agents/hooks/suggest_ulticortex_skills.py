#!/usr/bin/env python3
"""UltiMaker Unified Motion — Linked-Knowledge Graph Resolver & UltiCortex Skill Router.

Traverses the Obsidian Knowledge Vault (`docs/`), `[[wikilinks]]`, `file://` source
anchors, Domain Glossaries (`GLOSSARY.md` + `docs/05-Glossary/`), ADRs (`docs/adr/`),
centralized Lean 4 proofs (`proofs/Proofs/`), IP disclosures (`docs/03-IP-Portfolio/`),
and Quality/Forensics reports (`docs/06-Investigation-and-Quality-Reports/`),
combined with `herdr-kanban` ticket taxonomy facets (`domain:*`, `type:*`, `trl:*`,
`access:*`, `Priority`, `target_repo`) to synthesize an actionable 3-Phase Agent
Engineering Brief:
  Phase 1 — Smart Design Choices (MOCs, L1-L3 Architecture, Glossary, ADRs, C4, IP Boundary)
  Phase 2 — Smart Implementation Choices (Source Anchors, Standards, TRL & Type Policies, Skills)
  Phase 3 — Smart Verification & Obsidian Deliverable Choices (Lean 4 Proofs, Vault Notes, Twin, CLI Gates)
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"

WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
FILE_LINK_RE = re.compile(r"\[([^\]]+)\]\((file:///[^)]+)\)")
TICKET_REF_RE = re.compile(r"^(?:([A-Za-z0-9_.-]+)?#)?([0-9]+)$")


@dataclass
class VaultNote:
    path: Path
    rel_path: str
    stem: str
    category: str  # moc, arch, standard, ip, proof, glossary, report, adr, other
    level: str = ""
    wikilinks: list[str] = field(default_factory=list)
    source_anchors: list[tuple[str, str]] = field(default_factory=list)


@dataclass
class DomainProfile:
    domain_label: str
    bounded_context: str
    role_moc: str
    l1_arch_prefixes: tuple[str, ...]
    glossary_context: str
    adrs: tuple[str, ...]
    c4_views: tuple[str, ...]
    skills: tuple[str, ...]
    verify_commands: tuple[str, ...]
    keywords: tuple[str, ...]


DOMAIN_PROFILES: dict[str, DomainProfile] = {
    "domain:slicing": DomainProfile(
        domain_label="domain:slicing",
        bounded_context="Bounded Context 1 — Preparation & Slicing (Cura-unimotion, CuraEngine-unimotion)",
        role_moc="docs/00-Map-Of-Content (MOC)/Role Map-Of-Content (MOC) - Slicer and Prep Engineer.md",
        l1_arch_prefixes=(
            "docs/01-Product-Process-Architecture/L1-01-CAD-and-Print-Preparation",
            "docs/01-Product-Process-Architecture/L1-02-CuraEngine-Cpp23-Slicing",
        ),
        glossary_context="docs/05-Glossary/01-Preparation-and-Slicing/context-slicing.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0003-centralized-ip-and-lean4-proofs-for-public-safe-slicer.md",
        ),
        c4_views=("SystemLandscape", "SlicingEngineComponents"),
        skills=(
            "ultimaker-unified-motion",
            "ultimaker-cura-slicer",
            "ultimaker-process-knowledge",
            "ultimaker-material-knowledge",
            "ultimaker-gcode-architecture",
            "cpp-pro",
            "software-architect",
        ),
        verify_commands=(
            "./unimotion build proofs",
            "./unimotion test slicer",
            "python3 .agents/hooks/check_public_repo_ip_leak.py",
        ),
        keywords=(
            "curaengine",
            "cura-unimotion",
            "slicer",
            "slicing",
            "clipper",
            "arachne",
            "curveoptimal",
            "taggedgeometry",
            "step",
            "cemesh",
            "ceweld",
            "overhang",
            "seam",
            "support",
            "combing",
        ),
    ),
    "domain:wire-contract": DomainProfile(
        domain_label="domain:wire-contract",
        bounded_context="Bounded Context 2 — Lossless Intent Wire Contract (UFP & G2/G3/G5/M12084/M12095-M12097)",
        role_moc="docs/00-Map-Of-Content (MOC)/Role Map-Of-Content (MOC) - Wire Contract and Seams.md",
        l1_arch_prefixes=("docs/01-Product-Process-Architecture/L1-03-Lossless-Intent-Wire",),
        glossary_context="docs/05-Glossary/02-Lossless-Intent-Wire/context-wire.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md",
        ),
        c4_views=("SystemLandscape", "LosslessIntentPipeline"),
        skills=(
            "ultimaker-unified-motion",
            "ultimaker-gcode-architecture",
            "asd-ste100",
            "software-architect",
        ),
        verify_commands=(
            "python3 .agents/hooks/check_wire_contract_sync.py",
            "./unimotion build proofs",
            "./unimotion twin",
        ),
        keywords=(
            "wire",
            "ufp",
            "gcode",
            "g2",
            "g3",
            "g5",
            "m12084",
            "m12095",
            "m12096",
            "m12097",
            "dialect",
            "seam",
        ),
    ),
    "domain:som": DomainProfile(
        domain_label="domain:som",
        bounded_context="Bounded Context 3 — SOM Host Orchestration (opinicus, okuda, misp-service, marvin-service, jedi)",
        role_moc="docs/00-Map-Of-Content (MOC)/Role Map-Of-Content (MOC) - SOM and Linux Firmware Engineer.md",
        l1_arch_prefixes=(
            "docs/01-Product-Process-Architecture/L1-04-Opinicus-SOM-Orchestration",
            "docs/01-Product-Process-Architecture/L1-06-Telemetry-Fleet-and-Forensics",
        ),
        glossary_context="docs/05-Glossary/03-SOM-Host-Orchestration/context-som.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md",
        ),
        c4_views=("SystemLandscape", "SomHostContainers"),
        skills=(
            "ultimaker-unified-motion",
            "ultimaker-firmware-development",
            "ultimaker-gcode-architecture",
            "ultimaker-printer-ssh",
            "python-pro",
        ),
        verify_commands=(
            "./unimotion test som",
            "python3 .agents/hooks/check_wire_contract_sync.py",
        ),
        keywords=(
            "opinicus",
            "okuda",
            "misp-service",
            "marvin-service",
            "print-process-reporting",
            "python3-uc-firmware-upgrade",
            "stardust-printer_console",
            "misc-product-specific",
            "jedi-build",
            "jedi-cookbook",
            "som",
            "valkey",
        ),
    ),
    "domain:rt-control": DomainProfile(
        domain_label="domain:rt-control",
        bounded_context="Bounded Context 4 — Real-Time Physical Control (ultimoco C++23 + integrated Cheetah)",
        role_moc="docs/00-Map-Of-Content (MOC)/Role Map-Of-Content (MOC) - Real-Time Control Engineer.md",
        l1_arch_prefixes=(
            "docs/01-Product-Process-Architecture/L1-05-Ultimoco-RT-and-Cheetah",
            "docs/01-Product-Process-Architecture/L1-06-Telemetry-Fleet-and-Forensics",
        ),
        glossary_context="docs/05-Glossary/04-Real-Time-Physical-Control/context-rt.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md",
        ),
        c4_views=("SystemLandscape", "UltimocoRtComponents"),
        skills=(
            "ultimaker-unified-motion",
            "cpp-pro",
            "software-architect",
            "jlink-debugging",
            "ultimaker-material-knowledge",
        ),
        verify_commands=(
            "./unimotion build proofs",
            "./unimotion test rt-twin",
            "./unimotion twin",
        ),
        keywords=(
            "ultimoco",
            "cheetah",
            "zflow",
            "kalman",
            "shaper",
            "umb5",
            "umb6",
            "quintic",
            "enthalpy",
            "convective",
            "imu",
            "stepper",
            "rt-control",
            "ppq-148",
        ),
    ),
    "domain:digital-twin": DomainProfile(
        domain_label="domain:digital-twin",
        bounded_context="Bounded Context 4 — 75 MHz Virtual-Clock PAL Digital Twin & DoE Harness (ultimoco twin_cli)",
        role_moc="docs/00-Map-Of-Content (MOC)/Philosophy 2 - Quality and Development Standards Map-Of-Content (MOC).md",
        l1_arch_prefixes=(
            "docs/02-Quality-and-Development-Standards/L1-05-Digital-Twin-JLink-and-DoE",
            "docs/01-Product-Process-Architecture/L1-05-Ultimoco-RT-and-Cheetah",
        ),
        glossary_context="docs/05-Glossary/05-Quality-and-Verification/context-quality-verification.md",
        adrs=("docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md",),
        c4_views=("UltimocoRtComponents",),
        skills=(
            "ultimaker-unified-motion",
            "cpp-pro",
            "tdd",
            "ultimaker-cura-slicer",
        ),
        verify_commands=(
            "./unimotion build rt-twin",
            "./unimotion test rt-twin",
            "./unimotion twin",
        ),
        keywords=("twin_cli", "digital-twin", "pal", "virtual-clock", "doe", "chrono", "ultitools", "bench-telemetry"),
    ),
    "domain:print-quality": DomainProfile(
        domain_label="domain:print-quality",
        bounded_context="Cross-Cutting — Whole-Chain Print Artifact Forensics & Process Quality",
        role_moc="docs/00-Map-Of-Content (MOC)/Investigation and Quality Reports Map-Of-Content (MOC).md",
        l1_arch_prefixes=(
            "docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics",
            "docs/06-Investigation-and-Quality-Reports/L1-02-Slicer-Performance-and-Quality-Verification",
            "docs/01-Product-Process-Architecture/L1-06-Telemetry-Fleet-and-Forensics",
        ),
        glossary_context="docs/05-Glossary/00-Ubiquitous-Core/context-ubiquitous-core.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md",
            "docs/adr/0004-centralized-unimotion-issue-and-triage-control-plane.md",
        ),
        c4_views=("SystemLandscape",),
        skills=(
            "ultimaker-print-artifact-forensics",
            "ultimaker-material-knowledge",
            "ultimaker-process-knowledge",
            "ultimaker-cura-slicer",
            "ultimaker-unified-motion",
            "ultimaker-gcode-architecture",
        ),
        verify_commands=(
            "./unimotion build proofs",
            "./unimotion twin",
        ),
        keywords=("forensics", "print-quality", "artifact", "owl", "autodesk", "ringing", "divot", "scar", "cusum", "stringing", "banding"),
    ),
    "domain:proofs-ip": DomainProfile(
        domain_label="domain:proofs-ip",
        bounded_context="Meta-Repository — Lean 4 Formal Verification (`proofs/`) & Patent Portfolio (`ID1`-`ID26`)",
        role_moc="docs/00-Map-Of-Content (MOC)/Lean 4 Formal Verification Map-Of-Content (MOC).md",
        l1_arch_prefixes=(
            "docs/02-Quality-and-Development-Standards/L1-03-Lean4-Formal-Verification",
            "docs/03-IP-Portfolio",
            "docs/04-Lean4-Proofs",
        ),
        glossary_context="docs/05-Glossary/05-Quality-and-Verification/context-quality-verification.md",
        adrs=("docs/adr/0003-centralized-ip-and-lean4-proofs-for-public-safe-slicer.md",),
        c4_views=("SystemLandscape",),
        skills=(
            "ultimaker-unified-motion",
            "patent-disclosure",
            "asd-ste100",
        ),
        verify_commands=(
            "./unimotion build proofs",
            "python3 .agents/hooks/check_public_repo_ip_leak.py",
        ),
        keywords=("proofs", ".lean", "lean4", "mathlib", "id1", "id2", "id4", "id6", "id7", "id8", "id16", "patent", "ip"),
    ),
    "domain:architecture-dx": DomainProfile(
        domain_label="domain:architecture-dx",
        bounded_context="Meta-Repository — Architecture, Structurizr C4, Obsidian Vault & Multi-Agent Kanban DX",
        role_moc="docs/00-Map-Of-Content (MOC)/00 - Home - Unified Motion System Map-Of-Content (MOC).md",
        l1_arch_prefixes=(
            "docs/02-Quality-and-Development-Standards/L1-01-Deep-Modules-and-DAG",
            "docs/02-Quality-and-Development-Standards/L1-04-UltiCortex-and-Agentic-Harness",
            "docs/02-Quality-and-Development-Standards/L1-06-Feature-Isolation-ISO27001-and-ISTQB-QA",
        ),
        glossary_context="docs/05-Glossary/00-Ubiquitous-Core/context-ubiquitous-core.md",
        adrs=(
            "docs/adr/0001-six-seam-lossless-intent-pipeline.md",
            "docs/adr/0004-centralized-unimotion-issue-and-triage-control-plane.md",
            "docs/adr/0015-isolated-feature-lifecycle-iso27001-and-istqb-iso29119-qa-standard.md",
        ),
        c4_views=("SystemLandscape", "ContainerOverview"),
        skills=(
            "herdr-kanban",
            "ultimaker-unified-motion",
            "software-architect",
            "domain-modeling",
            "herdr-diagrams",
        ),
        verify_commands=(
            "./unimotion build diagrams",
            "./unimotion twin",
        ),
        keywords=(
            "workspace.dsl",
            "c4",
            "diagram",
            "kanban",
            "obsidian",
            "adr",
            "glossary",
            "architecture-dx",
            "unimotion",
            "istqb",
            "iso-29119",
            "iso-27001",
            "qa-test-plan",
            "feature-manifest",
        ),
    ),
}

TRL_GUIDANCE: dict[str, tuple[str, str, str]] = {
    "trl:concept": (
        "Concept / First-Principles Exploration (`trl:concept`)",
        "Focus on mathematical formulation, Lean 4 proof sketching (`proofs/Proofs/`), or throwaway hypothesis validation (`prototype` / `research` skills) before committing production interfaces.",
        "Document analytical assumptions, trade-offs, and promotion criteria to `trl:experimental` in `docs/`.",
    ),
    "trl:experimental": (
        "Experimental Feature / PoC (`trl:experimental`)",
        "Isolate behind a clean Deep Module seam (`docs/02-Quality-and-Development-Standards/L1-01-Deep-Modules-and-DAG/L1 - Deep Modules & DAG.md`) and gate behind an explicit feature policy (`M12095`-`M12097` or runtime/compile-time flag) so baseline behavior remains bit-identical when disabled.",
        "Verify in the 75 MHz `twin_cli` Digital Twin and/or headless Cura DoE benchmark against baseline before hardware bench runs.",
    ),
    "trl:production": (
        "Production-Grade Deliverable (`trl:production`)",
        "Enforce strict ISO C++23 zero-heap (`_HeapSize = 0` in RT), `mp-units` dimensional safety, `noexcept` hot paths, and hermetic DAG layering (`docs/02-Quality-and-Development-Standards/L1-02-ISO-Cpp23-and-Zero-Heap/L1 - ISO C++23 & Zero Heap.md`).",
        "All 4 verification tiers must pass: Lean 4 (`zero sorrys`), Structurizr C4 validation, Digital Twin regression tests, and IP/wire hygiene hooks.",
    ),
}

ACCESS_GUIDANCE: dict[str, str] = {
    "access:public": (
        "PUBLIC REPO HYGIENE (`access:public` — ADR-0003): Code targets public/LGPLv3 surface (`Cura-unimotion`, "
        "`CuraEngine-unimotion`, or open-source plugins). NEVER commit `.lean` files, `ID1`-`ID26` patent markers, "
        "or proprietary Ultimoco RT internals into public repositories. Keep formal proofs in `unimotion/proofs/`. "
        "Verify with `python3 .agents/hooks/check_public_repo_ip_leak.py`."
    ),
    "access:internal": (
        "INTERNAL ENGINEERING (`access:internal`): Follow canonical ubiquitous language from `GLOSSARY.md` and "
        "`docs/05-Glossary/`, keep SOM vs RT boundaries aligned with ADR-0002, and update linked `docs/` notes when seams change."
    ),
    "access:proprietary": (
        "PROPRIETARY EXECUTION MOAT (`access:proprietary` — ADR-0003): Covers Core 7 / ID1-ID26 innovations and "
        "`ultimoco` RT control algorithms. Keep invention disclosures in `unimotion/docs/03-IP-Portfolio/` and "
        "machine-checked proofs in `unimotion/proofs/Proofs/`."
    ),
}

TYPE_SKILLS: dict[str, tuple[str, ...]] = {
    "type:forensics": (
        "ultimaker-print-artifact-forensics",
        "ultimaker-material-knowledge",
        "ultimaker-process-knowledge",
        "ultimaker-cura-slicer",
        "ultimaker-unified-motion",
        "ultimaker-gcode-architecture",
        "ultimaker-printer-logs",
    ),
    "type:feature": (
        "software-architect",
        "codebase-design",
        "domain-modeling",
        "tdd",
    ),
    "type:bug": (
        "diagnosing-bugs",
        "tdd",
    ),
    "type:proof": (
        "ultimaker-unified-motion",
        "patent-disclosure",
        "asd-ste100",
    ),
    "type:spike": (
        "research",
        "prototype",
        "domain-modeling",
    ),
    "type:doc": (
        "domain-modeling",
        "asd-ste100",
        "herdr-diagrams",
    ),
    "type:chore": (
        "herdr-kanban",
    ),
}

TYPE_GUIDANCE: dict[str, str] = {
    "type:feature": (
        "Feature Engineering (`type:feature`): Read linked `L1`->`L2`->`L3` architecture notes and `Term - *.md` "
        "glossary definitions first; design a narrow Deep Module interface; implement with tests and update C4/docs if seams evolve."
    ),
    "type:bug": (
        "Bug Diagnosis & Fix (`type:bug`): Load `diagnosing-bugs` + `tdd`; reproduce deterministically in `twin_cli` or "
        "unit test first (red-green-refactor); verify no invariant regression in linked Lean 4 proofs."
    ),
    "type:forensics": (
        "Whole-Chain Forensics (`type:forensics` — ADR-0004): Load `ultimaker-print-artifact-forensics`, "
        "`ultimaker-material-knowledge`, `ultimaker-process-knowledge`, and `ultimaker-cura-slicer`. Trace the defect "
        "end-to-end across all 6 seams (CAD -> Slicer UFP/G-code -> Opinicus SOM -> Ultimoco 2 kHz telemetry -> Lean 4 proof). "
        "Deliverables MUST include: (1) an Obsidian forensic report in `docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics/Report - <Case> Forensics.md`, "
        "(2) a machine-checked Lean 4 proof in `proofs/Proofs/Forensics/<Case>Proofs.lean` (`0 sorry`s) + companion note in `docs/04-Lean4-Proofs/L2-03-Print-Forensics-Proofs/`, "
        "and (3) deposited follow-up fix tickets (`herdr-kanban deposit --parent`)."
    ),
    "type:spike": (
        "Time-Boxed Technical Spike (`type:spike`): Load `research` / `prototype`; validate feasibility against primary "
        "sources and `twin_cli` benchmarks; capture findings in `docs/` and deposit concrete follow-up implementation tickets."
    ),
    "type:proof": (
        "Formal Verification (`type:proof`): Implement machine-checked theorems in `proofs/Proofs/{Slicer,RT,Forensics}/*.lean` "
        "with ZERO `sorry`s and ZERO non-standard axioms (`./unimotion build proofs`), and update the companion note in `docs/04-Lean4-Proofs/`."
    ),
    "type:doc": (
        "Architecture & Domain Documentation (`type:doc`): Maintain `L0`->`L1`->`L2`->`L3` Obsidian `[[wikilinks]]`, "
        "ASD-STE100 controlled technical summaries, and `GLOSSARY.md` consistency."
    ),
    "type:chore": (
        "Engineering Harness / Build Chore (`type:chore`): Verify cross-platform CLI compatibility (`./unimotion doctor`) "
        "and ensure all git/agent hooks pass."
    ),
}


def build_required_deliverables(
    type_label: str,
    matched_domains: list[str],
    trl_label: str,
    access_label: str,
    ticket_num: int | None = None,
) -> list[str]:
    """Return the required Obsidian Vault, Lean 4 proof, code, and Kanban deliverables for a ticket."""
    t_str = f"unimotion#{ticket_num}" if ticket_num else "unimotion#<id>"
    items: list[str] = []

    if type_label == "type:forensics" or "domain:print-quality" in matched_domains and type_label in ("type:forensics", "type:bug"):
        items.extend(
            [
                "Load skills: `ultimaker-print-artifact-forensics`, `ultimaker-material-knowledge`, `ultimaker-process-knowledge`, `ultimaker-cura-slicer`, `ultimaker-unified-motion`",
                "Inspect physical print photos, UFP/G-code (`cura.mjs`), setting stack, and 2 kHz `/dev/ultimoco-console` / Valkey telemetry across Seams 1-6",
                "Prove root-cause witness & countermeasure theorem in `proofs/Proofs/Forensics/<Case>Proofs.lean` (`0 sorry`s via `./unimotion build proofs`)",
                "Create companion proof note `docs/04-Lean4-Proofs/L2-03-Print-Forensics-Proofs/Lean4 - <Case>Proofs.md` and link in `docs/00-Map-Of-Content (MOC)/Lean 4 Formal Verification Map-Of-Content (MOC).md`",
                "Publish forensic report `docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics/Report - <Case> Forensics.md` with figures in `docs/99-Assets/forensics/` and link in `L1 - Print Artifact Forensics Reports.md`",
                f"Deposit follow-up fix tickets (`herdr-kanban deposit --repo <target-repo> --parent {t_str} --depends-on {ticket_num or '<id>'}`) for each affected bounded context",
            ]
        )
        return items

    if type_label == "type:proof":
        items.extend(
            [
                "Read linked `L1`/`L2` architecture notes and existing theorems in `proofs/Proofs/{Slicer,RT,Forensics}/`",
                "Implement machine-checked Lean 4 theorems in `proofs/Proofs/{Slicer,RT,Forensics}/<Name>Proofs.lean` with `0 sorry`s (`./unimotion build proofs`)",
                "Create/update Obsidian proof note `docs/04-Lean4-Proofs/.../Lean4 - <Name>Proofs.md` with theorem line jump table",
                "Link proof note from the verified `L1`/`L2` architecture note in `docs/01-Product-Process-Architecture/` and `Lean 4 Formal Verification Map-Of-Content (MOC).md`",
            ]
        )
        return items

    if type_label == "type:spike":
        items.extend(
            [
                "Read linked `L1`/`L2` architecture notes, `GLOSSARY.md`, and ADRs (`docs/adr/`)",
                "Build throwaway prototype or analytical/Lean 4 evaluation (`trl:concept` / `trl:experimental`)",
                "Record spike findings and benchmark evidence in `docs/06-Investigation-and-Quality-Reports/` or `docs/adr/`",
                f"Deposit concrete follow-up implementation tickets (`herdr-kanban deposit --parent {t_str}`) with appropriate `trl:*` and `--depends-on`",
            ]
        )
        return items

    if type_label == "type:feature":
        items.extend(
            [
                "Read linked Role MOC, `L1`->`L2`->`L3` architecture notes, ADRs, and `Term - *.md` glossary definitions before designing interfaces",
                f"Implement feature adhering to `{trl_label}` policy (Deep Module boundary, zero-heap `_HeapSize = 0` in RT, feature policy gate if `trl:experimental`)",
                "Add/update unit & Digital Twin integration tests (`./unimotion test <domain>` & `./unimotion twin`)",
                "Verify or extend corresponding Lean 4 theorems in `proofs/Proofs/` (`./unimotion build proofs`, `0 sorry`s) if geometric/kinematic/thermal invariants change",
                "Update linked `L2`/`L3` architecture note (`docs/01-Product-Process-Architecture/`), `GLOSSARY.md` + `docs/05-Glossary/` (for new terms), and `docs/03-IP-Portfolio/` (if `access:proprietary` IP disclosure applies)",
            ]
        )
        if access_label == "access:public":
            items.append("Run `python3 .agents/hooks/check_public_repo_ip_leak.py` to guarantee zero `.lean` or `ID1`-`ID26` leaks in public repos")
        return items

    if type_label == "type:bug":
        items.extend(
            [
                "Read linked `L1`/`L2` architecture notes and forensic reports (`docs/06-Investigation-and-Quality-Reports/`) for historical root-cause context",
                "Write deterministic failing test first (`tdd` / `diagnosing-bugs`) in `ctest`, `pytest`, or `twin_cli`",
                "Fix root cause without violating Seam 1-6 lossless contracts or ADR-0002 SOM/RT ownership",
                "Run domain test suite, Lean 4 proofs (`./unimotion build proofs`), and update linked `docs/` note if seam assumptions changed",
            ]
        )
        return items

    items.extend(
        [
            "Read linked MOC and `L1`/`L2` notes in `docs/`",
            "Maintain valid `[[wikilinks]]`, `file://` source anchors, and `GLOSSARY.md` ubiquitous terminology",
            "Run verification checks (`./unimotion twin` / `./unimotion build diagrams`)",
        ]
    )
    return items


def classify_note(rel_path: str) -> str:
    if rel_path.startswith("docs/00-Map-Of-Content"):
        return "moc"
    if rel_path.startswith("docs/01-Product-Process-Architecture"):
        return "arch"
    if rel_path.startswith("docs/02-Quality-and-Development-Standards"):
        return "standard"
    if rel_path.startswith("docs/03-IP-Portfolio"):
        return "ip"
    if rel_path.startswith("docs/04-Lean4-Proofs"):
        return "proof"
    if rel_path.startswith("docs/05-Glossary"):
        return "glossary"
    if rel_path.startswith("docs/06-Investigation-and-Quality-Reports"):
        return "report"
    if rel_path.startswith("docs/adr"):
        return "adr"
    return "other"


def load_vault_index() -> dict[str, VaultNote]:
    """Index all markdown notes in `docs/` by stem and extracted `[[wikilinks]]`."""
    index: dict[str, VaultNote] = {}
    if not DOCS_DIR.exists():
        return index
    for md_path in sorted(DOCS_DIR.rglob("*.md")):
        if ".obsidian" in md_path.parts:
            continue
        rel = md_path.relative_to(REPO_ROOT).as_posix()
        try:
            text = md_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        links = []
        for m in WIKILINK_RE.finditer(text):
            target = m.group(1).strip()
            if target and not target.endswith((".svg", ".png", ".jpg", ".canvas")):
                links.append(target)
        anchors = []
        for m in FILE_LINK_RE.finditer(text):
            label, uri = m.group(1).strip(), m.group(2).strip()
            anchors.append((label, uri))
        level = ""
        for part in ("L0", "L1", "L2", "L3"):
            if md_path.stem.startswith(f"{part} -"):
                level = part
                break
        index[md_path.stem] = VaultNote(
            path=md_path,
            rel_path=rel,
            stem=md_path.stem,
            category=classify_note(rel),
            level=level,
            wikilinks=links,
            source_anchors=anchors,
        )
    return index


def fetch_ticket_metadata(ticket_ref: str) -> dict[str, Any] | None:
    cache_file = Path.home() / ".cache" / "herdr-kanban" / "board-Ultimaker-7.json"
    m = TICKET_REF_RE.match(ticket_ref.strip())
    if m and cache_file.exists():
        target_num = int(m.group(2))
        try:
            cached = json.loads(cache_file.read_text(encoding="utf-8"))
            for t in cached.get("tickets") or []:
                if isinstance(t, dict) and int(t.get("number") or 0) == target_num:
                    return t
        except (OSError, ValueError):
            pass

    kanban_bin = shutil.which("herdr-kanban") or str(Path.home() / ".local" / "bin" / "herdr-kanban")
    if not Path(kanban_bin).exists():
        return None
    try:
        proc = subprocess.run(
            [kanban_bin, "show", ticket_ref, "--json", "--cwd", str(REPO_ROOT)],
            capture_output=True,
            text=True,
            check=False,
            timeout=15,
        )
    except subprocess.TimeoutExpired:
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    try:
        data = json.loads(proc.stdout)
        if isinstance(data, dict):
            inner = data.get("ticket")
            return inner if isinstance(inner, dict) else data
        return None
    except ValueError:
        return None


def resolve_knowledge_brief(
    query: str,
    *,
    ticket_ref: str = "",
) -> dict[str, Any]:
    vault = load_vault_index()
    ticket_data: dict[str, Any] | None = None

    effective_ticket_ref = ticket_ref.strip()
    if not effective_ticket_ref and TICKET_REF_RE.match(query.strip()):
        effective_ticket_ref = query.strip()

    if effective_ticket_ref:
        ticket_data = fetch_ticket_metadata(effective_ticket_ref)

    labels: list[str] = []
    priority = ""
    milestone = ""
    target_repo = ""
    depends_on: list[int] = []
    blocks: list[int] = []
    search_tokens: list[str] = [query.lower()]

    if ticket_data:
        labels = [str(lbl).lower() for lbl in (ticket_data.get("labels") or [])]
        priority = str(ticket_data.get("priority") or "")
        milestone = str(ticket_data.get("milestone") or "")
        target_repo = str(ticket_data.get("target_repo") or ticket_data.get("repo_alias") or "")
        depends_on = list(ticket_data.get("depends_on") or [])
        blocks = list(ticket_data.get("blocks") or [])
        search_tokens.append(str(ticket_data.get("title") or "").lower())
        search_tokens.append(str(ticket_data.get("body") or "").lower())
        if target_repo:
            search_tokens.append(target_repo.lower())
        search_tokens.extend(labels)

    combined_text = " ".join(search_tokens)

    # Extract facet labels from either ticket_data or query string
    for tok in re.split(r"[\s,]+", combined_text):
        if tok.startswith(("domain:", "type:", "trl:", "access:")) and tok not in labels:
            labels.append(tok)

    matched_domains = [lbl for lbl in labels if lbl in DOMAIN_PROFILES]
    if not matched_domains:
        for dom_key, prof in DOMAIN_PROFILES.items():
            if any(kw in combined_text for kw in prof.keywords):
                matched_domains.append(dom_key)
    if not matched_domains:
        matched_domains.append("domain:architecture-dx")

    trl_label = next((lbl for lbl in labels if lbl in TRL_GUIDANCE), "trl:production")
    access_label = next((lbl for lbl in labels if lbl in ACCESS_GUIDANCE), "access:internal")
    type_label = next((lbl for lbl in labels if lbl in TYPE_GUIDANCE), "")
    if not type_label:
        if "domain:print-quality" in matched_domains or any(
            w in combined_text for w in ("forensic", "artifact", "defect", "ringing", "divot", "scar", "banding")
        ):
            type_label = "type:forensics"
        else:
            type_label = "type:feature"

    # Gather seed notes from matched domain profiles + keyword matches in vault stems
    seed_stems: list[str] = []
    role_mocs: list[str] = []
    glossary_contexts: list[str] = []
    adrs: list[str] = []
    c4_views: list[str] = []
    skills: list[str] = ["herdr-kanban", "ultimaker-unified-motion"]
    verify_cmds: list[str] = []

    for ts in TYPE_SKILLS.get(type_label, ()):
        if ts not in skills:
            skills.append(ts)

    query_words = [
        w
        for w in re.findall(r"[a-z0-9_+-]{3,}", combined_text)
        if w not in {"the", "and", "for", "with", "from", "into", "unimotion", "cura", "emb", "ppq"}
    ]

    for dom_key in matched_domains:
        prof = DOMAIN_PROFILES[dom_key]
        if prof.role_moc not in role_mocs:
            role_mocs.append(prof.role_moc)
        if prof.glossary_context not in glossary_contexts:
            glossary_contexts.append(prof.glossary_context)
        for a in prof.adrs:
            if a not in adrs:
                adrs.append(a)
        for v in prof.c4_views:
            if v not in c4_views:
                c4_views.append(v)
        for s in prof.skills:
            if s not in skills:
                skills.append(s)
        for cmd in prof.verify_commands:
            if cmd not in verify_cmds:
                verify_cmds.append(cmd)
        for note in vault.values():
            if any(note.rel_path.startswith(pfx) for pfx in prof.l1_arch_prefixes):
                if note.level == "L1" and note.stem not in seed_stems:
                    seed_stems.append(note.stem)

    # Keyword-specific note boosts across the vault
    scored_notes: list[tuple[int, VaultNote]] = []
    for note in vault.values():
        stem_lc = note.stem.lower()
        rel_lc = note.rel_path.lower()
        score = sum(3 if w in stem_lc else (1 if w in rel_lc else 0) for w in query_words)
        if score > 0:
            scored_notes.append((score, note))
    scored_notes.sort(key=lambda item: (-item[0], item[1].rel_path))
    for _, note in scored_notes[:8]:
        if note.stem not in seed_stems:
            seed_stems.append(note.stem)

    # Traverse 1-2 hops of [[wikilinks]] from seed notes to collect linked L2/L3, Standards, IP, Proofs, Glossary Terms, Reports
    visited_stems: list[str] = list(seed_stems)
    frontier = list(seed_stems)
    for _hop in range(2):
        next_frontier: list[str] = []
        for stem in frontier:
            note = vault.get(stem)
            if not note:
                continue
            for target in note.wikilinks:
                target_stem = Path(target).name
                if target_stem in vault and target_stem not in visited_stems:
                    visited_stems.append(target_stem)
                    next_frontier.append(target_stem)
        frontier = next_frontier

    arch_notes: list[str] = []
    standard_notes: list[str] = [
        "docs/02-Quality-and-Development-Standards/L1-01-Deep-Modules-and-DAG/L1 - Deep Modules & DAG.md",
        "docs/02-Quality-and-Development-Standards/L1-02-ISO-Cpp23-and-Zero-Heap/L1 - ISO C++23 & Zero Heap.md",
    ]
    ip_notes: list[str] = []
    proof_notes: list[str] = []
    glossary_terms: list[str] = []
    report_notes: list[str] = []
    source_anchors: list[tuple[str, str]] = []

    for stem in visited_stems:
        note = vault.get(stem)
        if not note:
            continue
        for anchor in note.source_anchors:
            if anchor not in source_anchors and len(source_anchors) < 10:
                source_anchors.append(anchor)
        if note.category == "arch" and note.rel_path not in arch_notes and len(arch_notes) < 10:
            arch_notes.append(note.rel_path)
        elif note.category == "standard" and note.rel_path not in standard_notes and len(standard_notes) < 6:
            standard_notes.append(note.rel_path)
        elif note.category == "ip" and note.rel_path not in ip_notes and len(ip_notes) < 6:
            ip_notes.append(note.rel_path)
        elif note.category == "proof" and note.rel_path not in proof_notes and len(proof_notes) < 6:
            proof_notes.append(note.rel_path)
        elif note.category == "glossary" and note.rel_path not in glossary_terms and len(glossary_terms) < 10:
            glossary_terms.append(note.rel_path)
        elif note.category == "report" and note.rel_path not in report_notes and len(report_notes) < 5:
            report_notes.append(note.rel_path)

    if type_label == "type:forensics" or "domain:print-quality" in matched_domains:
        for note in vault.values():
            if note.rel_path.startswith("docs/04-Lean4-Proofs/L2-03-Print-Forensics-Proofs/") and note.rel_path not in proof_notes:
                proof_notes.append(note.rel_path)
            if note.rel_path.startswith("docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics/") and note.rel_path not in report_notes:
                report_notes.append(note.rel_path)

    # Map proof notes (`Lean4 - FooProofs.md`) to actual `.lean` files in `proofs/Proofs/`
    lean_files: list[str] = []
    for p_rel in proof_notes:
        stem = Path(p_rel).stem
        if stem.startswith("Lean4 - "):
            lean_name = f"{stem.removeprefix('Lean4 - ').strip()}.lean"
            for candidate in (REPO_ROOT / "proofs").rglob(lean_name):
                rel_lean = candidate.relative_to(REPO_ROOT).as_posix()
                if rel_lean not in lean_files:
                    lean_files.append(rel_lean)

    ticket_num = int(ticket_data["number"]) if ticket_data and ticket_data.get("number") else None
    deliverables = build_required_deliverables(
        type_label,
        matched_domains,
        trl_label,
        access_label,
        ticket_num=ticket_num,
    )

    trl_title, trl_impl, trl_verify = TRL_GUIDANCE[trl_label]
    return {
        "query": query,
        "ticket": (
            {
                "number": ticket_data.get("number"),
                "title": ticket_data.get("title"),
                "column": ticket_data.get("column"),
                "priority": priority,
                "milestone": milestone,
                "target_repo": target_repo,
                "labels": labels,
                "depends_on": depends_on,
                "blocks": blocks,
            }
            if ticket_data
            else None
        ),
        "facets": {
            "domains": matched_domains,
            "type": type_label,
            "trl": trl_label,
            "access": access_label,
        },
        "design_choices": {
            "role_mocs": role_mocs,
            "architecture_l1_l3_notes": arch_notes,
            "glossary_contexts": glossary_contexts,
            "linked_glossary_terms": glossary_terms,
            "adrs": adrs,
            "c4_views": c4_views,
            "ip_disclosures": ip_notes,
            "access_guardrail": ACCESS_GUIDANCE[access_label],
        },
        "implementation_choices": {
            "quality_standards": standard_notes,
            "source_anchors": [{"label": lbl, "uri": uri} for lbl, uri in source_anchors],
            "trl_policy": {"tier": trl_title, "implementation": trl_impl, "verification": trl_verify},
            "type_policy": TYPE_GUIDANCE[type_label],
            "recommended_skills": skills,
        },
        "verification_choices": {
            "required_deliverables": deliverables,
            "lean4_proof_notes": proof_notes,
            "lean4_source_files": lean_files,
            "benchmark_and_forensics_reports": report_notes,
            "verification_commands": verify_cmds,
        },
    }


def format_markdown_brief(brief: dict[str, Any]) -> str:
    lines: list[str] = []
    t = brief.get("ticket")
    facets = brief["facets"]
    if t:
        lines.append(f"# Linked-Knowledge Engineering Brief — `unimotion#{t['number']}`")
        lines.append(f"**Title**: {t['title']}")
        lines.append(
            f"**Target Repo**: `{t['target_repo'] or 'unimotion'}` | "
            f"**Priority**: `{t['priority'] or 'unset'}` | "
            f"**Milestone**: `{t['milestone'] or 'unset'}` | "
            f"**Facets**: `{', '.join(facets['domains'])}`, `{facets['type']}`, `{facets['trl']}`, `{facets['access']}`"
        )
        if t.get("depends_on") or t.get("blocks"):
            lines.append(
                f"**Dependency DAG**: depends_on=`{t.get('depends_on')}` | blocks=`{t.get('blocks')}`"
            )
    else:
        lines.append(f"# Linked-Knowledge Engineering Brief — `{brief['query']}`")
        lines.append(
            f"**Resolved Facets**: `{', '.join(facets['domains'])}` | "
            f"`{facets['type']}` | `{facets['trl']}` | `{facets['access']}`"
        )

    dc = brief["design_choices"]
    lines.append("\n## Phase 1 — Smart Design Choices (Read Linked Graph Before Coding)")
    lines.append(f"- **Access & IP Boundary**: {dc['access_guardrail']}")
    lines.append("- **Role Map-Of-Content (MOC)**:")
    for m in dc["role_mocs"]:
        lines.append(f"  - [`{Path(m).name}`](file://{(REPO_ROOT / m).as_posix()})")
    if dc["architecture_l1_l3_notes"]:
        lines.append("- **Linked `L1`->`L2`->`L3` Architecture Notes (`[[wikilinks]]`)**:")
        for n in dc["architecture_l1_l3_notes"]:
            lines.append(f"  - [`{Path(n).name}`](file://{(REPO_ROOT / n).as_posix()})")
    lines.append("- **Architecture Decision Records (MADR) & C4 Views (`docs/architecture/workspace.dsl`)**:")
    for a in dc["adrs"]:
        lines.append(f"  - [`{Path(a).name}`](file://{(REPO_ROOT / a).as_posix()})")
    lines.append(f"  - Structurizr C4 Views to keep in sync: `{', '.join(dc['c4_views'])}`")
    lines.append("- **Ubiquitous Language & Linked Domain Glossary (`GLOSSARY.md` + `docs/05-Glossary/`)**:")
    for g in dc["glossary_contexts"]:
        lines.append(f"  - Context Glossary: [`{Path(g).name}`](file://{(REPO_ROOT / g).as_posix()})")
    for term in dc["linked_glossary_terms"][:6]:
        lines.append(f"  - [`{Path(term).stem}`](file://{(REPO_ROOT / term).as_posix()})")
    if dc["ip_disclosures"]:
        lines.append("- **Connected Invention Disclosures (`docs/03-IP-Portfolio/`)**:")
        for ip in dc["ip_disclosures"]:
            lines.append(f"  - [`{Path(ip).name}`](file://{(REPO_ROOT / ip).as_posix()})")

    ic = brief["implementation_choices"]
    lines.append("\n## Phase 2 — Smart Implementation Choices (Deep Modules, TRL, Type & Skills)")
    lines.append(f"- **{ic['trl_policy']['tier']}**: {ic['trl_policy']['implementation']}")
    lines.append(f"- **Ticket Type Playbook**: {ic['type_policy']}")
    lines.append("- **Mandatory UltiCortex Skills (`SKILL.md`) to Load**:")
    lines.append(f"  - `{', '.join(ic['recommended_skills'])}`")
    lines.append("- **Quality & Development Standards**:")
    for std in ic["quality_standards"]:
        lines.append(f"  - [`{Path(std).name}`](file://{(REPO_ROOT / std).as_posix()})")
    if ic["source_anchors"]:
        lines.append("- **Repository Source Code Anchors (from linked vault notes)**:")
        for anc in ic["source_anchors"][:8]:
            lines.append(f"  - [{anc['label']}]({anc['uri']})")

    vc = brief["verification_choices"]
    lines.append("\n## Phase 3 — Smart Verification & Obsidian Deliverable Choices ('Meten is Weten')")
    lines.append("- **Mandatory Definition-of-Done Deliverables (Code + Obsidian Vault + Lean 4 + Kanban)**:")
    for idx, item in enumerate(vc["required_deliverables"], 1):
        lines.append(f"  {idx}. `[ ]` {item}")
    lines.append(f"- **TRL Verification Expectation**: {ic['trl_policy']['verification']}")
    if vc["lean4_source_files"] or vc["lean4_proof_notes"]:
        lines.append("- **Linked Machine-Checked Lean 4 Proofs (`zero sorrys`)**:")
        for lf in vc["lean4_source_files"]:
            lines.append(f"  - [`{Path(lf).name}`](file://{(REPO_ROOT / lf).as_posix()})")
        for pn in vc["lean4_proof_notes"]:
            lines.append(f"  - Note: [`{Path(pn).name}`](file://{(REPO_ROOT / pn).as_posix()})")
    if vc["benchmark_and_forensics_reports"]:
        lines.append("- **Reference Quality, DoE & Forensics Reports (`docs/06-Investigation-and-Quality-Reports/`)**:")
        for rep in vc["benchmark_and_forensics_reports"]:
            lines.append(f"  - [`{Path(rep).name}`](file://{(REPO_ROOT / rep).as_posix()})")
    lines.append("- **Mandatory Verification Commands Before `herdr-kanban done`**:")
    for cmd in vc["verification_commands"]:
        lines.append(f"  - `{cmd}`")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve linked Obsidian Vault knowledge, Glossary terms, ADRs, Proofs, Deliverables, and UltiCortex skills for a ticket or query."
    )
    parser.add_argument(
        "query",
        nargs="*",
        default=["unimotion"],
        help="Ticket ID (e.g. unimotion#8, #3), labels (domain:print-quality type:forensics), file path, or domain keywords",
    )
    parser.add_argument("--ticket", default="", help="Explicit Kanban ticket ID (e.g. unimotion#10)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--checklist", action="store_true", help="Emit `herdr-kanban progress --check` flags for the ticket's required deliverables")
    parser.add_argument("--output", default="", help="Optional markdown file path to write the brief to")
    args = parser.parse_args()

    query_str = " ".join(args.query).strip() or "unimotion"
    brief = resolve_knowledge_brief(query_str, ticket_ref=args.ticket)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(format_markdown_brief(brief), encoding="utf-8")

    if args.checklist:
        for item in brief["verification_choices"]["required_deliverables"]:
            print(f'--check "[ ] {item}"')
        return 0

    if args.json:
        print(json.dumps(brief, indent=2))
    else:
        print(format_markdown_brief(brief), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
