---
description: Skills from the UltiCortex catalogue that apply to this repository, and when to load them.
---
# UltiMaker Skill Discovery & Usage

This repository has been matched against the UltiCortex skill catalogue. Loading
the relevant skill is **not optional** for the work it covers: these skills carry
the standards, idioms, and tooling knowledge that the rules in this directory
assume you already have.

```bash
# Search the catalogue
gh skill search ultimaker --owner Ultimaker

# Install a specific skill
gh skill install Ultimaker/UltiCortex <skill-name>
```

Load the skill **before** designing or implementing, not after review comments
arrive. If a skill contradicts a rule in this directory, raise the conflict
rather than silently picking one.

## Skills Matched To This Repository

### `conan-2` — when touching `**/conanfile.py`, `**/conanfile.txt`, `**/conandata.yml`

Engineering guide for Conan 2 dependency management, cross-compilation, CMake integrations, and packaging workflows.

**Why it applies here:** Dependency graph, profiles, cross-compilation and packaging are Conan 2 concerns; the skill carries the v2 idioms and the CMakeToolchain/CMakeDeps integration this repository relies on.

```bash
gh skill install Ultimaker/UltiCortex conan-2
```

### `cmake` — when touching `**/CMakeLists.txt`, `**/*.cmake`, `**/CMakePresets.json`

Modern target-centric C/C++ engineering with CMake 3 & 4. Best practices, multi-platform presets, CTest QA, Conan 2 resolution, and CPack platform installations.

**Why it applies here:** Target-centric CMake, presets, and CTest wiring — avoid reinventing build logic or reaching for directory-scoped commands.

```bash
gh skill install Ultimaker/UltiCortex cmake
```

### `python-pro` — when touching `**/*.py`

Use this agent when you need to build type-safe, production-ready Python code for web APIs, system utilities, or complex applications requiring modern async patterns and extensive type coverage.

**Why it applies here:** Type-safe, production-ready Python: typing coverage, async patterns, and the conventions mined into the Python rule.

```bash
gh skill install Ultimaker/UltiCortex python-pro
```

### `software-architect` — always relevant

Expert Software Architect guide for best practices (SOLID, DRY) and Design Patterns, referencing Refactoring Guru.

**Why it applies here:** SOLID, DRY and the design-pattern catalogue — the reference to consult when a change needs decomposition rather than more lines in an existing module.

```bash
gh skill install Ultimaker/UltiCortex software-architect
```

### `ultimaker-material-knowledge` — when touching `**/*.xml.fdm_material`

Plastics engineering calculations for extrusion, viscosity models, thermal properties, and polymer processing.

**Why it applies here:** Material profile semantics and the polymer/processing physics behind the values being changed.

```bash
gh skill install Ultimaker/UltiCortex ultimaker-material-knowledge
```

## Other Catalogue Skills

17 further skill(s) exist that no automatic trigger matched.
They are listed in `.agents/bootstrap-observations.md` rather than here, because
by construction they are the ones static detection judged irrelevant — and this
file is loaded every session.

```bash
gh skill search ultimaker --owner Ultimaker
```
