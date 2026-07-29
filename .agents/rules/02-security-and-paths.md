---
description: Security guidelines, secret protection, and path sanitation.
---
# Security & Path Protection Guidelines

1. **No Hardcoded Absolute Paths**:
   - Never commit absolute local filesystem paths (e.g. `<home>/<username>/` or `<Users>/<username>/`).
2. **No Secret Leaks**:
   - Never commit private keys, API tokens, or passphrases.
   - Use RAM-backed filesystem mounts (`/dev/shm`) for temporary secret processing.
3. **Branch Guard**:
   - Direct commits to `main`, `master`, or `staging` branches are strictly forbidden.
