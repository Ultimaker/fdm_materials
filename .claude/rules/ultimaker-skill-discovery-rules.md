---
description: Mandate for dynamic discovery and usage of domain-specific UltiMaker engineering skills from UltiCortex.
---
# Dynamic UltiMaker AI Skill Discovery & Usage

AI agents working in this repository MUST dynamically discover and install specialized domain skills from `Ultimaker/UltiCortex` when performing relevant tasks:

```bash
# Search available skills
gh skill search ultimaker --owner Ultimaker

# Install specific skill
gh skill install Ultimaker/UltiCortex <skill-name>
```

## Mandated Skill Triggers
1. **`ultimaker-printer-ssh`**:
   - **Trigger**: When deploying packages, checking DBus properties, testing build outputs, or troubleshooting local services on physical or emulated 3D printers over SSH.
2. **`ultimaker-digital-factory`**:
   - **Trigger**: When working on cloud state synchronization, WSS WebSocket connections, IoT connectivity, telemetry, or Digital Factory API features.
3. **`ultimaker-log-analyzer`**:
   - **Trigger**: When analyzing log dumps (`/var/log/messages`, systemd journal, `opinicus.log`, `okuda.log`, `stardust.log`).
4. **`ultimaker-firmware-developer`**:
   - **Trigger**: When modifying core DBus interfaces, state machine frameworks, or CMake/Conan build tooling.
 5. **`ultimaker-support-articles`**:
   - **Trigger**: When introducing user-facing feature changes or behavioral shifts that impact public documentation or support workflows.
