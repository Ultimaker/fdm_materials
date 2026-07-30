---
description: Python conventions mined from this repository (typing, async, frameworks, formatting, logging).
---
# Python Conventions (3 files sampled)

> These rules are DISCOVERED from this repository's own sources by the agentic
> bootstrap — they are not organization-wide defaults. Re-run the bootstrap with
> `--update` after intentional convention changes.

0. **Load the `python-pro` skill** before implementing: it carries the type-safety, async, and packaging practices these conventions assume.
1. **Type Hints Mandatory**: 53% of sampled functions are annotated. ALL new/modified functions MUST have full parameter and return type annotations.
2. **I/O Discipline**: follow the existing synchronous patterns; do not introduce async frameworks without an explicit architecture decision.
3. **Logging over print**: `logging` is the established convention. Errors log to `sys.stderr` context and scripts exit non-zero (`sys.exit(1)`) on failure. Never log secrets/PII.
4. **String Formatting**: the dominant style here is **f-strings** ({'f-strings': 11, '.format()': 0, '%-formatting': 1}). Use it consistently; do not mix formatting styles within a module.
