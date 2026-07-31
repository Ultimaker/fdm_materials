---
description: OWASP security standards selected for this repository's detected stack profile.
---
# OWASP Security Guidelines (Profile-Matched)

These sections were selected because the bootstrap investigation detected the matching stack. Enforcement is layered: these rules guide implementation, pre-commit hooks block secrets/paths mechanically, and `scripts/verify_and_create_pr.sh` runs the adversarial audit before any PR.

## Secure Coding Essentials

1. **No hardcoded credentials**: never commit passwords, private keys, API tokens or HMAC secrets. Load them from the environment or a secret manager at runtime.
2. **Input validation**: validate and sanitise anything that crosses a trust boundary — user input, file contents, network payloads, subprocess arguments.
3. **Injection prevention**: parameterise database queries and never build shell commands by string concatenation from untrusted values.
4. **Privacy**: never write personal data, passwords or tokens to logs, telemetry or debug output.
5. **Dependency hygiene**: keep dependencies pinned and patched; check advisories before adding one.
6. **Error hygiene**: do not leak stack traces, internal paths or configuration in errors returned across a boundary.
