---
paths:
  - "**/conanfile.py"
  - "**/conanfile.txt"
  - "**/conandata.yml"
---
# Use the `conan-2` skill for these files

You are editing files covered by the `conan-2` skill. Load it before making
changes:

```bash
gh skill install Ultimaker/UltiCortex conan-2
```

**What it covers:** Engineering guide for Conan 2 dependency management, cross-compilation, CMake integrations, and packaging workflows.

**Why it applies to this file type:** Dependency graph, profiles, cross-compilation and packaging are Conan 2 concerns; the skill carries the v2 idioms and the CMakeToolchain/CMakeDeps integration this repository relies on.

Follow that skill's guidance over your own defaults. If you are about to invent
a pattern it already prescribes, use the prescribed one instead.
