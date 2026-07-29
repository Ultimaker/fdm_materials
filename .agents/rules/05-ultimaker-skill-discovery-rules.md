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
   - Trigger: Deploying packages, checking DBus properties, testing build outputs, or troubleshooting local services over SSH.
2. **`ultimaker-digital-factory`**:
   - Trigger: Cloud state sync, WSS WebSocket connections, IoT connectivity, telemetry, or Digital Factory APIs.
3. **`ultimaker-log-analyzer`**:
   - Trigger: Analyzing log dumps (`/var/log/messages`, systemd journal, `opinicus.log`, `okuda.log`, `stardust.log`).
4. **`ultimaker-firmware-developer`**:
   - Trigger: Modifying DBus interfaces, state machine frameworks, or CMake/Conan build tooling.
5. **`ultimaker-support-articles`**:
   - Trigger: User-facing feature changes impacting public support documentation.
