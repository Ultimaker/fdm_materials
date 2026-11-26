<!-- unimotion-dual-ticket-traceability -->
> **UMBRELLA RULES #1 & #2 (`unimotion` Multi-Agent Kanban & Dual-Ticket Traceability)**:
> 1. **Kanban & Subagent Awareness**: Run `herdr-kanban board` and `herdr-kanban inbox --ack` at session start. Whenever spawning a subagent, pass the active `herdr-kanban` ticket ID, relevant Jira key (`CURA-13401` for Cura, `EMB-476` for firmware, or explicitly requested key), worktree path, and active sibling file claims (`.agents/rules/01-herdr-kanban-multi-agent.md`).
> 2. **Non-Negotiable Dual-Ticket Commits & Issues**: Keep commit titles and Kanban `--title`s clean (no Jira or GitHub ticket numbers in titles). Every `herdr-kanban deposit` / GitHub Issue MUST include the relevant Jira key (`Jira: EMB-476` / `Jira: CURA-13401`) in its `--body`, and every Git commit message MUST cite **BOTH** the relevant Jira ticket key AND the GitHub Kanban ticket ID in the commit message body (e.g. `Jira: EMB-476` / `Refs: unimotion#2`). Enforced by `.agents/hooks/check_dual_ticket_traceability.py`.

# AGENTS.md — fdm_materials

<!-- BEGIN UNIMOTION DEPENDENCY TRAIN -->
## Dependency Train & Release Position (Auto-Synced from `unimotion/scripts/release_dag.py`)

- **Repository & Dev Branch:** `fdm_materials` (`CURA-13401-unimotion`)
- **Published Artifacts:** `fdm_materials/<ver>@ultimaker/testing` (`conan`)
- **Direct Upstream Repos:** *(Leaf repository — no internal Unimotion upstream)*
- **Downstream Consumer Repos:** `Cura-unimotion`, `Curator`, `neoprep`
- **Affected Release Trains (`herdr-kanban` & Changelogs):** `neoprep`, `slicer`
- **Docker Build Toolchain:** `fdm_materials/docker_env/Dockerfile`
- **Verify & Release Commands (from `unimotion` root):**
  - Inspect dirty/skip DAG status: `./unimotion release graph`
  - Release affected train(s): `./unimotion release all`
<!-- END UNIMOTION DEPENDENCY TRAIN -->
