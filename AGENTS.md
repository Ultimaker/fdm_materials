
## Agentic Development & Tooling Hooks

To ensure compatibility and performance with our AI Coding Agents:
- **Size Checks**: Ensure large generated models, binaries, or logs are NOT checked into standard git. Keep PR sizes small (ideally under 500 lines) for optimal Copilot/Agent reviews.
- **Claude & Cursor Hooks**: Standard `.claude` or `.cursorrules` guidelines are strictly aggregated into this `AGENTS.md` file. Do not create fragmented hidden dotfiles for AI rules.
- **Antigravity 2 Hooks**: When using Google Antigravity 2, agents must respect `.agyrules` and verify codebase boundaries using pre-commit checks prior to running full workspace deployments.

## Repository Specifics (fdm_materials)
- **Validation**: Run `./run_check_material_profiles.sh` to validate `.fdm_material` XML profiles.
- **Linting**: Run `./run_shellcheck.sh` to lint shell scripts.
- **Build**: Use `CMakeLists.txt` or `./build.sh` / `./build_for_ultimaker.sh` for packaging.
