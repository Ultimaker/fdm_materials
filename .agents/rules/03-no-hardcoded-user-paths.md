# Rule 03: No Hardcoded Local User Paths

**Applies to**: All files in `unimotion` (`docs/`, `proofs/`, `scripts/`, `.agents/`, `AGENTS.md`, tests, and configs).

## 1. Policy
Never commit hardcoded machine-local or user-home paths such as:
- `/home/<user>/...`
- `/Users/<user>/...`
- `C:\Users\<user>\...` or `file:///home/<user>/...`

## 2. What to Use Instead
- **Obsidian Vault / Markdown links**: Use `[[wikilinks]]` for vault notes, or **repository-relative paths** (e.g., `proofs/Proofs/RT/Ngp175MmFilamentLimitsProofs.lean`, `../../proofs/Proofs/...`).
- **Frontmatter (`source_file:`)**: Use repo-relative paths (`"proofs/Proofs/RT/..."`).
- **Python / Shell scripts**: Use `Path.home()`, `Path(__file__).resolve()`, `$HOME`, or `$(git rev-parse --show-toplevel)`.

## 3. Automated Enforcement
Enforced mechanically on every commit via:
- `.agents/hooks/block-absolute-paths.py` + `.agents/hooks/path_scanner.py`
- `.agents/hooks.json` (`PreCommit`)
- `.pre-commit-config.yaml` (`block-absolute-paths`)
- `.git/hooks/pre-commit` (installed by `./unimotion sync`)
