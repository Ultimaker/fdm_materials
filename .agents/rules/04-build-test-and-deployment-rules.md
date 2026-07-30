---
description: Build, test, and deployment verification commands detected for this repository.
---
# Build, Test & Deployment Verification

1. **Build Commands (detected)**:
   - `./build_for_ultimaker.sh`
   - `cmake --build build`
   - `conan build .`
   - Builds must complete cleanly (no new warnings) before PR creation.
2. **Test Commands (detected)**:
   - (no test runner detected — add one and re-run bootstrap --update)
3. **Artifact Isolation**:
   - Keep generated build outputs, intermediate binaries, and logs out of git.
