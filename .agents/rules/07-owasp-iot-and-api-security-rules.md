---
description: OWASP Top 10 IoT Security and OWASP API Security Top 10 guidelines for firmware daemons, Opinicus REST/DBus endpoints, and embedded components.
---
# OWASP IoT & API Security Guidelines

## 1. OWASP Top 10 IoT Vulnerability Mitigations
1. **Weak, Guessable, or Hardcoded Credentials**:
   - Zero hardcoded passwords, private keys, API tokens, or HMAC secrets in source code.
   - Decryption and signing keys must be loaded from GCP Secret Manager or RAM-backed `/dev/shm` tmpfs mounts.
2. **Insecure Network Services**:
   - Exposed network ports must require TLS/SSL encryption.
   - Local IPC/DBus endpoints must authenticate callers and enforce interface permissions.
3. **Insecure Ecosystem Interfaces**:
   - Validate and sanitize all incoming payloads across REST API routes, DBus methods, and MQTT topics.
   - Reject unverified or oversized JSON/GCode payloads.
4. **Lack of Secure Update Mechanism**:
   - Firmware SWU updates require detached GPG signatures. Never bypass signature verification logic in update scripts.
5. **Use of Insecure or Outdated Components**:
   - Keep Python packages, Conan C++ dependencies, and Debian build recipes pinned to secure releases.
6. **Insufficient Privacy Protection**:
   - Never write PII, passwords, or authentication tokens to system journal, `opinicus.log`, or debug outputs.
7. **Insecure Data Transfer & Storage**:
   - Store temporary sensitive decryption targets in RAM-backed filesystem (`/dev/shm`).
8. **Lack of Device Management**:
   - IoT connectivity to UltiMaker Digital Factory must use authenticated WSS websockets over TLS.
9. **Insecure Default Settings**:
   - Default configurations must be secure out-of-the-box (SSH disabled by default, random `umssh` passwords).
10. **Lack of Physical Hardening**:
    - Protect SOM/UART/USB serial debug ports against unauthenticated flashloader commands.

## 2. OWASP API Security Top 10 (Opinicus REST & DBus APIs)
1. **Broken Object Level Authorization (BOLA)**:
   - Validate caller privileges before reading or writing printer hardware states, queues, or configurations.
2. **Broken Authentication**:
   - Authenticate all external REST API endpoints and cloud WebSocket connections.
3. **Broken Object Property Level Authorization**:
   - Ensure clients cannot modify unauthorized object fields during JSON deserialization.
4. **Unrestricted Resource Consumption**:
   - Enforce payload size limits, rate limiting, and queue bounds on incoming GCode, REST requests, and WebSocket frames.
5. **Broken Function Level Authorization**:
   - Administrative functions (e.g. system reboot, EEPROM write, firmware update trigger) require elevated authorization.
6. **Server-Side Request Forgery (SSRF)**:
   - Validate and sanitize all external URLs provided for package downloads, camera streams, or telemetry sync; restrict to authorized UltiMaker Digital Factory domains.
7. **Security Misconfiguration**:
   - Suppress verbose stack traces or internal local filesystem paths in HTTP and DBus error responses.
8. **Improper Inventory Management**:
   - Keep REST API specification in `docs/api_documentation.json` in sync with active endpoints.
