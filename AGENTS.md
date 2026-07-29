# Agent Operational & Onboarding Guide (AGENTS.md)

Welcome, AI Agent! This document defines the operational boundaries, design patterns, testing strategies, and collaborative conventions for the `fdm_materials` repository.

As a dynamic assistant, you must adhere strictly to these principles to maintain codebase sanity and ensure future developers can build upon your work efficiently.

---

## 1. SaaS Context, Sibling Services & AI Skill Discovery

### fdm_materials Context

**fdm_materials** is the centralized, standard database of polymer profiles and Fused Deposition Modeling (FDM) print preparation settings. It supplies the critical material and extruder properties (such as temperatures, speeds, fan rules, and retraction behaviors) matching the physical polymer properties of UltiMaker and third-party materials.

- **Profile Resolution**: These profiles are in XML format with `.xml.fdm_material` extensions, complying with the material profile schema. They are parsed and resolved by **Curator** and **CuraEngine (WASM)** to ensure safe, high-quality, and predictable 3D print preparation and slicing inside **NeoPrep (Cura Cloud)** and Cura Desktop.
- **Client-Side Slicing**: Direct material settings are injected dynamically into WASM slicing runs inside the user's web browser, meaning proper naming, GUIDs, and parameters must remain strictly stable.

### Sibling Services & Relative Paths

To collaborate on cross-repository features or platform emulation, locate and link with sibling services in this local workspace. Use the following relative paths and consult their corresponding `AGENTS.md` operational guides:

- **[neoprep](../../.gemini/antigravity/worktrees/neoprep/audit-stardust-atlas-submodules/)**: The interactive React 3D prep workspace. The painting pipeline is described in [painting_pipeline.md](../../.gemini/antigravity/worktrees/neoprep/audit-stardust-atlas-submodules/doc/Software%20Architecture/painting_pipeline.md).
- **[Curator](../../.gemini/antigravity/worktrees/Curator/)**: Slicing profile resolver.
- **[stardust-atlas](../../.gemini/antigravity/worktrees/stardust-atlas/audit-stardust-atlas-submodules/)**: Meta-repository and orchestration layer compiling the full Digital Factory stack.

### 🔍 Dynamic AI Skill Discovery & Installation

To obtain expert domain knowledge and specific runtime tools, agents **must** dynamically discover and install specialized engineering skills from `Ultimaker/UltiCortex` on branch `UC-3695_improve_code_base_for_agentic_development`:

```bash
# Discover and install specialized skills
gh skill install Ultimaker/UltiCortex ultimaker-neoprep-development --branch UC-3695_improve_code_base_for_agentic_development
gh skill install Ultimaker/UltiCortex ultimaker-material-knowledge --branch UC-3695_improve_code_base_for_agentic_development
gh skill install Ultimaker/UltiCortex ultimaker-support-articles --branch UC-3695_improve_code_base_for_agentic_development
```

---

## 2. Work Tracking, Git & Pull Request Habits

- **Jira Tracking**: All changes require an active Jira ticket starting with project key **`UC`** or **`NP`** (e.g., `UC-3697` or `NP-1325`). Branch names must be formatted as `[PROJECT_KEY]-[ID]_description`.
- **Git Commit Standards**:
  - **Bracketed Ticket Prefix**: Every Git commit title and GitHub Pull Request title **MUST** start with the active branch's Jira ticket key in bracketed format: `[PROJECT-KEY] <Description>`. For example: `[UC-3697] <Description>`.
  - **No Semantic Prefixes**: Do **NOT** use conventional/semantic commit prefix tags (such as `feat:`, `fix:`, `chore:`, etc.) in commit titles or Pull Request titles.
  - Commit message format:

    ```
    [UC-3697] Configure pre-commit and agentic enablement

    Setup pre-commit hooks and custom copilot instructions for fdm_materials development.

    Contributes to UC-3697
    ```

- **PR Guidelines**:
  - Always open PRs as **DRAFT** state. Merging is **strictly restricted to humans**.
  - Monitor CI status checks. Ensure build, linter, formatting, and unit tests pass cleanly.

---

## 3. Directory Organization & Architecture Index

### Core Directory Maps:

- `/*.xml.fdm_material`: Individual polymer profile XML definitions.
- `/scripts/`: Material profile validation and check scripts.
- `CMakeLists.txt` & `conanfile.py`: Package configuration files for Conan packaging.

---

## 4. Local Setup & Verification

### 🚀 Quick Start

1. Install dependencies and validate profiles:
   ```bash
   conan install . --build=missing
   ./run_check_material_profiles.sh
   ```

---

## 5. Quality Control, Tooling & Local Verification

To maintain top-tier reliability, fdm_materials enforces static checks. Succeeding agents and developers **must** run and verify these tools before proposing any Pull Request:

### 🧹 Profile Validation (run_check_material_profiles.sh)

Verify that all material profiles comply with standard schemas and have valid structures:

- **Verification**: `./run_check_material_profiles.sh`

### ⚓ Pre-commit Hook Integration

Pre-commit hooks automatically execute fast checks (check-yaml, check-json, talisman, local path blocking, and agent artifact checks) on staged files.

- **Manual Hook Audit**:
  ```bash
  pre-commit run --all-files
  ```
- **Opt-Out (Humans Only)**: Humans may prepend `SKIP_PRE_COMMIT=1` or run `git commit --no-verify`. AI agents **MUST** pass all pre-commit hooks cleanly.
