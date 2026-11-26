# Rule 04: Secrets Hygiene, Hook Integrity & Linear History

**Applies to**: All files and commits in `unimotion`.

1. **Zero Hardcoded Secrets**: Never commit API keys, GitHub tokens, private keys, or credentials. Enforced mechanically by `.agents/hooks/block-secrets.py` + `secret_scanner.py`.
2. **No Hook / Security Downgrades**: Never skip pre-commit/commit-msg hooks or disable security checks in `.pre-commit-config.yaml` / `.agents/hooks.json`. Enforced by `.agents/hooks/check_security_downgrades.py`.
3. **Safe Process Termination**: Never use broad `pkill -f` / `killall` commands that can terminate sibling agents. Enforced by `.agents/hooks/block_name_matched_kill.py`.
4. **Linear History & Naming**: Rebase onto `origin/main` rather than creating merge commits, and name new Python scripts in `scripts/` using `snake_case`.
5. **Git LFS for Binary, CAD/Slicer & Telemetry Assets (`.gitattributes`)**: Store raster images (`*.png`, `*.jpg`), reports/decks (`*.pdf`, `*.pptx`), 3D models & print packages (`*.3mf`, `*.stl`, `*.step`, `*.ufp`, `*.gcode`), SQLite DBs/logs (`*.db`, `*.jsonl`, `*.log`, `*.tar.gz`), and Redis/Valkey telemetry dumps (`docs/99-Assets/evidence/**/redis*/*.json`) via Git LFS (`filter=lfs`). Keep `.svg`, `.mmd`, `.puml`, `.dsl`, `.canvas`, and `.lean` as native Git text blobs. Never bypass the chained `.git/hooks/pre-push` hook (`check_allowed_push_branch.py` + `git lfs pre-push`).
