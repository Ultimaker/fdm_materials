---
name: dual-ticket-jira-github-traceability
description: Require relevant Jira ticket key and GitHub Kanban issue reference in commit message body and Kanban issue description (not in titles).
trigger: always_on
---
# Rule 02: Non-Negotiable Dual-Ticket Traceability (Jira + GitHub Kanban)

**Applies to**: Every Git commit message, pull request, and `herdr-kanban deposit` / GitHub Issue across `unimotion` and all 15 child repositories.

## 1. Why Dual-Ticket Traceability Exists
- **Human Program & Release Tracking** runs in **Atlassian Jira** (currently `CURA-13401` for Cura/slicer work and `EMB-476` for firmware/SOM work; future work will use different Jira ticket numbers).
- **Agentic Task Execution & Worktree Coordination** runs in **GitHub Projects v2 Kanban** (`unimotion#1`, `unimotion#5`, `CuraEngine-unimotion#2`, etc.).
- Every artifact must bridge both systems so human engineers and autonomous agents have 100% bidirectional traceability, while keeping commit and issue **titles** clean and readable.

## 2. Non-Negotiable Commit Message Format
**Every Git commit message** in `unimotion` and in all 15 child repositories **MUST**:
1. Keep the **commit title (subject line) clean** — do **NOT** put Jira ticket keys or GitHub issue numbers in the title.
2. Mention **BOTH** in the **commit message body / description**:
   - A relevant **Jira Ticket Key** matching `[A-Z][A-Z0-9]+-[0-9]+` (e.g., `CURA-13401` or `EMB-476`).
   - A **GitHub Kanban Ticket ID** matching `(?:[A-Za-z0-9_.-]+)?#[0-9]+` (e.g., `unimotion#1`, `unimotion#5`, `CuraEngine-unimotion#2`, `opinicus#2878`, or `#5`).

### Valid Commit Message Examples
```text
Build Structurizr C4 model, cross-platform CLI, and umbrella harness

Jira: EMB-476
Refs: unimotion#1
```
```text
Sanitize .lean proofs from public slicer repository

Jira: CURA-13401
Refs: CuraEngine-unimotion#2
```

### Relevant Jira Ticket Selection (Current Defaults & Overrides)
Only cite Jira ticket numbers that are **relevant** to the change:
- **Cura / Slicer-related tickets & commits** (`Cura-unimotion`, `CuraEngine-unimotion`, `CuraFormulaeEngine-unimotion`, `Uranium-unimotion`, `CuraMCP`, `fdm_materials`, `fdm_materials_private`, `ultimaker-machine-resources`, `Curator`, `neoprep`): currently use **`CURA-13401`**.
- **Firmware / SOM-related tickets & commits** (`ultimoco`, `opinicus`, `okuda`, `misp-service`, `marvin-service`, `print-process-reporting`, `python3-uc-firmware-upgrade`, `UltiTools`, `bench-telemetry`, `stardust-printer_console`, `misc-product-specific`, `jedi-build`, `jedi-cookbook`, `cura-private-data`): currently use **`EMB-476`**.
- **Meta-repo cross-cutting work** (`unimotion` `main` branch): use whichever Jira key (`CURA-13401` or `EMB-476`) is relevant to the work (cite both only when the change genuinely spans both Cura and firmware).
- **One-offs & Future Tickets**: `PPQ-148` was a one-off and must not be added by default. Future epics/sprints will use different Jira ticket numbers.
- **Explicit Overrides**: If the user explicitly asks to use a different Jira ticket, label and cite that requested ticket accordingly instead of the default.

## 3. Non-Negotiable Kanban Issue / Deposit Format
Every ticket created on the Kanban board (`herdr-kanban deposit` or `gh issue create`) **MUST**:
1. Keep the **ticket `--title` clean** — do **NOT** put Jira keys or GitHub ticket numbers in the title.
2. Include the relevant **Jira Ticket Key** in its **`--body` (description)**:
```bash
herdr-kanban deposit \
  --repo opinicus \
  --title "Clean up legacy Marlin/S7 documentation" \
  --body "Jira: EMB-476. Discovered under unimotion#1..."
```

## 4. Automated Enforcement (`commit-msg` + Agent `PreToolUse` Hook)
Enforced automatically in `unimotion` and all 15 child repositories via:
- `.agents/hooks/check_dual_ticket_traceability.py`
- `.git/hooks/commit-msg` (installed across all 16 repositories via `./unimotion sync`)
