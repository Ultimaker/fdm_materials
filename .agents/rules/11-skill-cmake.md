---
paths:
  - "**/CMakeLists.txt"
  - "**/*.cmake"
  - "**/CMakePresets.json"
---
# Use the `cmake` skill for these files

You are editing files covered by the `cmake` skill. Load it before making
changes:

```bash
gh skill install Ultimaker/UltiCortex cmake
```

**What it covers:** Modern target-centric C/C++ engineering with CMake 3 & 4. Best practices, multi-platform presets, CTest QA, Conan 2 resolution, and CPack platform installations.

**Why it applies to this file type:** Target-centric CMake, presets, and CTest wiring — avoid reinventing build logic or reaching for directory-scoped commands.

Follow that skill's guidance over your own defaults. If you are about to invent
a pattern it already prescribes, use the prescribed one instead.
