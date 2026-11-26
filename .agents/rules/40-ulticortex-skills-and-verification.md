# Rule 40: Linked-Knowledge Engineering Loop, UltiCortex Skills & Deliverable Gates ("Meten is Weten")

**Applies to**: Every main agent and spawned subagent designing, implementing, investigating, or verifying work across `unimotion` and its 15 child repositories.

## 1. Mandatory 3-Phase Linked-Knowledge Engineering Loop
Before writing code or documentation on any Kanban ticket (`unimotion#<id>`), resolve its linked knowledge subgraph:
```bash
./unimotion knowledge unimotion#<id>
```
This traverses the Obsidian Knowledge Vault (`docs/`), `[[wikilinks]]`, `file://` source anchors, `GLOSSARY.md`, `docs/adr/`, `proofs/Proofs/`, and the ticket's 4 taxonomy facets (`domain:*`, `type:*`, `trl:*`, `access:*`) across three mandatory phases:

1. **Phase 1 — Smart Design Choices (Read Linked Graph First)**:
   - Read the resolved **Role MOC** (`docs/00-Map-Of-Content (MOC)/`) and **`L1`→`L2`→`L3` Architecture notes** (`docs/01-Product-Process-Architecture/`).
   - Check the resolved **MADR Architecture Decision Records** (`docs/adr/0001`–`0004`), **Structurizr C4 views** (`docs/architecture/workspace.dsl`), and **Domain Glossary terms** (`docs/05-Glossary/**/Term - *.md`) so class names, units, and wire parameters match canonical ubiquitous language.
   - Respect the ticket's **`access:*` IP boundary** (`access:public` forbids `.lean` and `ID1`–`ID26` markers in `Cura-unimotion` / `CuraEngine-unimotion`; `access:proprietary` routes invention disclosures to `docs/03-IP-Portfolio/`).

2. **Phase 2 — Smart Implementation Choices (Deep Modules, TRL Tier & UltiCortex Skills)**:
   - Load every **UltiCortex `SKILL.md`** recommended by `./unimotion knowledge`.
   - Follow **`docs/02-Quality-and-Development-Standards/`** (`L1 - Deep Modules & DAG`, `L1 - ISO C++23 & Zero Heap` `_HeapSize = 0`, `mp-units`, `noexcept`).
   - Tailor implementation depth to the ticket's **`trl:*` Technology Readiness Tier**:
     - `trl:concept`: Mathematical formulation, Lean 4 proof exploration, or throwaway prototype (`prototype`/`research` skills).
     - `trl:experimental`: Isolated behind a narrow Deep Module seam and gated behind an explicit feature policy (`M12095`–`M12097` or runtime/compile-time flag) so disabled behavior is bit-identical to baseline; benchmarked in `twin_cli` or headless slicer DoE.
     - `trl:production`: Full ISO C++23 zero-heap RT compliance, complete unit + Digital Twin regression coverage, and machine-checked Lean 4 proofs (`0 sorry`s).

3. **Phase 3 — Smart Verification & Obsidian Vault Deliverables (By Ticket `type:*`)**:
   Every ticket type has a concrete **Definition of Done** across code, Lean 4 proofs, Obsidian Vault notes, and Kanban follow-ups (verified via `./unimotion knowledge --check unimotion#<id>`):
   - **`type:forensics` (Whole-Chain Print Artifact / Quality Investigation)**:
     1. **Skills**: Load `ultimaker-print-artifact-forensics`, `ultimaker-material-knowledge`, `ultimaker-process-knowledge`, `ultimaker-cura-slicer`, `ultimaker-unified-motion`.
     2. **Obsidian Forensic Report**: Publish `docs/06-Investigation-and-Quality-Reports/L1-01-Print-Artifact-Forensics/Report - <Case> Forensics.md` with visual evidence in `docs/99-Assets/forensics/`, `[[wikilinks]]` to affected `L1`/`L2` architecture slices, and link it in `L1 - Print Artifact Forensics Reports.md` and `Investigation and Quality Reports Map-Of-Content (MOC).md`.
     3. **Machine-Checked Lean 4 Proof**: Formulate and prove the physical/geometric/kinematic root-cause witness and countermeasure theorem in `proofs/Proofs/Forensics/<Case>Proofs.lean` (`0 sorry`s via `./unimotion build proofs`) + companion note `docs/04-Lean4-Proofs/L2-03-Print-Forensics-Proofs/Lean4 - <Case>Proofs.md`.
     4. **Follow-Up Fix Tickets**: Deposit concrete remedial tickets (`herdr-kanban deposit --repo <target-repo> --parent unimotion#<id> --depends-on <id>`) in `Ultimaker/unimotion`.
   - **`type:feature`**:
     - Code + unit/Digital Twin tests (`./unimotion test <domain>` & `./unimotion twin`) + Lean 4 theorem update (`proofs/Proofs/{Slicer,RT}/*.lean`, `0 sorry`s) + updated `L2`/`L3` architecture note (`docs/01-Product-Process-Architecture/`), `Term - *.md` glossary note (if new terms added), and `ID<N> - *.md` disclosure (if `access:proprietary` IP applies).
   - **`type:bug`**:
     - Failing-then-passing regression test (`tdd` / `diagnosing-bugs` in `ctest`, `pytest`, or `twin_cli`) + Lean 4 invariant check (`./unimotion build proofs`) + update to linked `L2`/`L3` or forensic report note.
   - **`type:proof`**:
     - `proofs/Proofs/{Slicer,RT,Forensics}/<Name>Proofs.lean` (`0 sorry`s, `./unimotion build proofs`) + companion `docs/04-Lean4-Proofs/.../Lean4 - <Name>Proofs.md` linked in `Lean 4 Formal Verification Map-Of-Content (MOC).md`.
   - **`type:spike`**:
     - Prototype/DoE benchmark evidence recorded in `docs/06-Investigation-and-Quality-Reports/` or `docs/adr/` + deposited follow-up tickets (`herdr-kanban deposit --parent`).

## 2. Four-Tier Verification Gate Before `herdr-kanban done`
Run `./unimotion knowledge --check unimotion#<id>` plus the domain verification commands:
1. **Lean 4 Mathematical Proofs (`./unimotion build proofs`)**: `proofs/Proofs/{Slicer,RT,Forensics}/*.lean` must compile with **zero `sorry`s** and **zero non-standard axioms**.
2. **Structurizr C4 & Vault Graph Integrity (`./unimotion build diagrams` & `./unimotion knowledge --check`)**: `docs/architecture/workspace.dsl` and all `docs/**/*.md` `[[wikilinks]]` must validate cleanly.
3. **75 MHz Virtual-Clock Digital Twin (`./unimotion twin` & `./unimotion test rt-twin`)**: Replay sliced toolpaths through `ultimoco`'s host-compiled `twin_cli`.
4. **Hardware & Fleet Telemetry (`bench-telemetry`)**: Validate 2 kHz `/dev/ultimoco-console` / Valkey telemetry streams against R1/R2/R3 CUSUM drift thresholds.
