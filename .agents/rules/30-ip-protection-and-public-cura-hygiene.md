# Rule 30: IP Protection & Public Cura Repository Hygiene

**Applies to**: `Cura-unimotion`, `CuraEngine-unimotion`, `ultimoco`, `proofs/`, and `docs/03-IP-Portfolio/`.

## 1. Centralized Residency ([ADR-0003](../../docs/adr/0003-centralized-ip-and-lean4-proofs-for-public-safe-slicer.md))
`Cura-unimotion` and `CuraEngine-unimotion` are slated to return to public open-source distribution (`LGPLv3`). Therefore:
- **All Lean 4 formal proof files (`*.lean`, `lakefile.lean`, `lean-toolchain`) MUST live exclusively in `unimotion/proofs/`**.
- **All invention disclosures (`ID1`–`ID26`), patent claim charts, and competitive moat analyses MUST live exclusively in `unimotion/docs/03-IP-Portfolio/`**.

## 2. Forbidden Content in `Cura-unimotion` and `CuraEngine-unimotion`
Never add any of the following to `Cura-unimotion` or `CuraEngine-unimotion` source files, headers, tests, comments, or commit messages:
1. Any `.lean` file or `docs/proofs/` directory.
2. Invention disclosure identifiers (`ID1` through `ID26`, `ID-01` through `ID-26`, `Invention Disclosure`, `Patent Disclosure`, `Patent Claim`).
3. Cross-references to private `unimotion/docs/03-IP-Portfolio/` or firmware trade-secret identifiers (`PPQ-148`, `EMB-476` internal moat notes).

## 3. Automated Enforcement
Always run the leak guard hook before committing or pushing changes in `Cura-unimotion` or `CuraEngine-unimotion`:
```bash
python3 .agents/hooks/check_public_repo_ip_leak.py
```
If `CuraEngine-unimotion` currently has legacy `.lean` files tracked under `CuraEngine-unimotion/docs/proofs/` (tracked by ticket `CuraEngine-unimotion#2`), `check_public_repo_ip_leak.py --strict` flags them until `CuraEngine-unimotion#2` removes them.
