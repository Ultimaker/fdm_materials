---
name: herdr-kanban-multi-agent
description: Coordinate multi-agent and subagent tasks via herdr-kanban board, claims, and worktrees.
trigger: always_on
---
# Rule 01: `herdr-kanban` Multi-Agent & Subagent Coordination

**Applies to**: All main agents and all spawned subagents (`invoke_subagent`, `Task`, `herdr-kanban dispatch`, background workers) across `unimotion` and its 15 child repositories.

## 1. Mandatory Startup Check (Main Agents & Subagents)
At the beginning of every session or delegated task, run:
```bash
herdr-kanban board
herdr-kanban inbox --ack
./unimotion kanban context
```
This surfaces:
- All tickets in `In Progress`, `Ready`, `Blocked`, `Review`, and `Triage` on GitHub Project #7 (`Ultimaker/projects/7`).
- Active sibling claims in `.siblings/<repo>/<issue>.json` and their declared `--files` scope.
- Any incoming cross-agent relay messages (`herdr-kanban ask` / `inbox`).

## 2. Mandatory Subagent Context Propagation
Whenever an agent spawns a **subagent**, the parent agent **MUST** include in the subagent's prompt:
1. **Active Kanban Ticket ID(s)**: e.g., `unimotion#1`, `unimotion#5`, `CuraEngine-unimotion#2`, `unimotion#2`, `unimotion#3`, `unimotion#4`.
2. **Target Repository & Worktree Path**: exact path where the subagent is authorized to write.
3. **Sibling Claims & Off-Limits Files**: any files or directories currently claimed by sibling agents (check `./unimotion kanban overlaps`).
4. **Startup Instruction**: instruct the subagent to run `herdr-kanban board` or `./unimotion kanban context` if it needs to inspect cross-repo state or deposit follow-up issues.

## 3. Central `unimotion` Issue Control Plane, Taxonomy, Priorities & Dependency DAG (ADR-0004)
All GitHub Issues, labels, priorities, and milestones live **exclusively** in `Ultimaker/unimotion` (`issues_repo = "unimotion"` in `.herdr-kanban.toml`). Child repositories (`Cura-unimotion`, `CuraEngine-unimotion`, `ultimoco`, `opinicus`, etc.) are strictly code/worktree targets (`--repo <target-repo>`).

- **4 Mandatory Label Facets (`herdr-kanban sync-labels`)**:
  - `domain:*` (1+ required): `cura` (Cura Desktop app), `neoprep` (NeoPrep Desktop/Cloud & `cadkernel-occt`), `slicing` (shared slicing engine: `CuraEngine-unimotion`, `Curator`, `fdm_materials*`), `wire-contract`, `som`, `rt-control`, `digital-twin`, `print-quality`, `proofs-ip`, `architecture-dx`
  - `type:*` (exactly 1): `feature`, `bug`, `forensics` (Whole-Chain Forensics print-artifact RCA), `spike`, `proof`, `doc`, `chore`
  - `trl:*` (exactly 1): `concept`, `experimental`, `production`
  - `access:*` (exactly 1): `public`, `internal`, `proprietary`
- **Priority & Milestones**:
  - GitHub Project #7 native `Priority` field (`P0`, `P1`, `P2`, `P3`) — required before moving to `Ready`.
  - Milestones in `Ultimaker/unimotion`: `Onboard the teams`, `Hand-over PoC to V&V`.
- **Dependency DAG & Parallel Waves (`--depends-on` / `--blocks`)**:
  - Tickets declare upstream blockers via `--depends-on <id>`. `herdr-kanban board` and `list --ready-now` compute topological execution waves (`wave 0` = unblocked now) sorted by `Priority` (`P0` → `P3`).
  - `herdr-kanban claim` blocks if upstream dependencies are not `Done`. `herdr-kanban done` automatically transitions newly unblocked `Blocked` tickets to `Ready` once their Ready gate passes.

## 4. Claiming, Progress, Relay Messaging, and Deposits
- **Claim before editing**:
  ```bash
  herdr-kanban claim unimotion#<id> --json
  ```
- **Update live progress in-place (zero comment spam)**:
  ```bash
  herdr-kanban progress unimotion#<id> --note "Implementing ..." --check "[x] Step 1" --check "[ ] Step 2"
  ```
- **Deposit out-of-scope discoveries or follow-up tickets into `Ultimaker/unimotion`**:
  ```bash
  herdr-kanban deposit --repo <target-repo> \
    -l domain:<d> -l type:<t> -l trl:<tier> -l access:<acc> \
    -p P1 -m "Onboard the teams" --depends-on <upstream-id> \
    "Short descriptive summary" --body "Jira: <CURA-13401|EMB-476|explicit-key>. Context + reproduction" --parent unimotion#<id>
  ```
- **Triage labels, priority, milestone, and dependencies**:
  ```bash
  herdr-kanban triage unimotion#<id> --column ready -l domain:<d> -l type:<t> -l trl:<tier> -l access:<acc> -p P1 -m "Onboard the teams"
  ```
- **Ask another ticket's agent a question without leaving the terminal**:
  ```bash
  herdr-kanban ask unimotion#<target-id> --from unimotion#<your-id> "Question about seam/interface..."
  ```

## 5. Mandatory Ticket Landing & Board Progression (Never Leave Completed Work in `In Progress`)
A ticket is **NOT** finished when files are edited or when `herdr-kanban progress` has all `[x]` items checked. Before ending a task or subagent run:
1. **Commit all changes** with a clean title and the non-negotiable dual-ticket traceability footer in the commit message body (`Jira: <relevant-key>` and `Refs: <repo#id>`).
2. **Advance the ticket across the board**:
   - To land, run checks, push to the shared target branch, and move the card to **`Done`**:
     ```bash
     herdr-kanban done <repo#id> --summary "Summary of verified changes (Jira: <relevant-key>)"
     ```
   - Or if human review is requested before landing, move the card to **`Review`**:
     ```bash
     herdr-kanban triage <repo#id> --column review
     ```
   - Or if blocked on an external dependency, move the card to **`Blocked`**:
     ```bash
     herdr-kanban triage <repo#id> --column blocked
     ```
