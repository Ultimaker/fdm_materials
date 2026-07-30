---
description: Build, test, and deployment verification commands detected for this repository.
---
# Build, Test & Deployment Verification

1. **Build Commands (detected)**:
   - `./build_for_ultimaker.sh`
   - `cmake --build build`
   - `conan build .`
   - Builds must complete cleanly (no new warnings) before PR creation.
   - **Container Rebuilds & Compilation Mandate**: When changing frontend or backend code in Docker or compiled environments, executing container rebuilds or asset compilation (`docker compose build <service>` / `npm run build`) is strictly required before visual or functional verification.
   - **Package Registry Authentication**: Ensure `GITHUB_TOKEN` with `read:packages` scope is exported in your shell environment or loaded from gitignored `.env` / `.env.local` files when building services that consume private `@ultimaker` packages. Never commit plain-text credentials to git.
2. **Test Commands (detected)**:
   - (no test runner detected — add one and re-run bootstrap --update)
3. **Artifact Isolation**:
   - Keep generated build outputs, intermediate binaries, and logs out of git. Ensure `.env` and `.env.local` files remain strictly gitignored.
4. **Firmware Docker Container Testing Mandate**:
   - Firmware repositories (`opinicus`, `okuda`, `jedi-build`, `jedi-cookbook`, `stardust-embedded`, `ultimoco`, `fdm_materials`) target ARM embedded Linux devices. Unit and integration tests MUST be executed inside official Docker build containers (`./build_for_ultimaker.sh` or `docker run ...` with container mounts) and NEVER directly on host x86 development environments.
   - All tests must pass cleanly inside Docker before committing or opening pull requests.
