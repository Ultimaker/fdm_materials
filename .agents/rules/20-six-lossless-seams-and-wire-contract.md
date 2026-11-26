# Rule 20: Six Lossless Seams & Wire Contract Invariants

**Applies to**: `Cura-unimotion`, `CuraEngine-unimotion`, `opinicus`, `ultimoco`, and `proofs/`.

## 1. The Six Lossless Seams ([ADR-0001](../../docs/adr/0001-six-seam-lossless-intent-pipeline.md))
1. **Seam 1 (`CAD -> Mesh`)**: Preserve analytical `STEP` surface normals and curvature tags through `CadSurfaceFaceMatcher` and `CadTransformConformality`.
2. **Seam 2 (`Frontend -> Engine IPC`)**: Use `CEMESH01` / `CEWELD01` 36-byte binary framing + $3\times 4$ affine transform matrices and `StreamingDeflateUfpBuffer`.
3. **Seam 3 (`Clipper / Voronoi -> Toolpath`)**: Preserve `PointTag` (`CornerSharp`, `ArcCandidate`, `SmoothSpline`, `SeamAnchor`) across Clipper2 booleans and Arachne skeletal graphs; propagate inward wall curves only where $1 - d\kappa > 0$.
4. **Seam 4 (`Slicer -> Wire Format`)**: Emit exact Pratt `G2`/`G3` circular arcs and Gauss-Newton `G5` cubic Béziers with continuous `Q`/`B` ($\text{mm}^2$) or `W`/`B` ($\text{mm}$) ramps, `M12084` dependency bitmasks, and `M12095`–`M12097` feature policies.
5. **Seam 5 (`Host Opinicus -> RT Ultimoco`)** ([ADR-0002](../../docs/adr/0002-som-persistence-vs-rt-coordinate-compensation.md)): `opinicus` MUST stream `G2`/`G3`/`G5` moves and stored calibration tables to `ultimoco` without expanding curves into `G1` chords or pre-warping coordinates in Python.
6. **Seam 6 (`Planner -> Extruder & Frame`)**: `ultimoco` executes zero-drain shaper policy switching (`ID1`), convective-cancellation variable-width ramps (`ID4`/`ID16`), tip-to-head polytope projection (`ID6`), sample-rate `ZFlow` bed compensation (`ID7`), and 100 Hz radial enthalpy control (`ID8`/`ID9`).

## 2. Canonical Wire Opcode Grammar
| Opcode | Syntax | Contract Invariant |
|---|---|---|
| `G2` / `G3` | `G2\|G3 X Y [Z] I J E [F] [Q B \| W B]` | CW/CCW arc; wire `E` equals exact integral of cross-section ramp $\int_0^L q(s)\,ds$. |
| `G5` | `G5 X Y I J P Q E [F] [W B]` | Cubic Bézier (`P`=$X_2$ offset, `Q`=$Y_2$ offset). **Must use `W`/`B` ($\text{mm}$ width) and never `Q`/`B` for extrusion ramps** because `Q` is reserved for $Y_2$. |
| `G1 ... Q B` | `G1 X Y [Z] E [F] Q<end_mm2> B<start_mm2>` | Linear move with continuous cross-sectional area ramp $q(s) = B + (Q - B)\,(s/L)$. |
| `M12084` | `M12084 S<mask> \| P<object_id>` | Bitwise `ModelDependencyMask` allowing `ultimoco` to skip failed objects while preserving shared support trunks. |
| `M12095` | `M12095 SET=<preset> WIDTH=... CORNER=... PA=... SHAPER=...` | Zero-drain in-motion feature policy switch (`ID1`). |
| `M12096` | `M12096 V<mm/s> A<mm/s2> J<mm/s3>` | Per-feature tip kinematic ceiling projected through head actuator polytopes (`ID6`). |
| `M12097` | `M12097 SLOT=<n> TYPE=<ZV\|MZV\|EI> F=<Hz> ZETA=<d>` | Pre-loads tap-scored input shaper filter bank slots (`ID1`, `ID5`). |

Run `python3 .agents/hooks/check_wire_contract_sync.py` after any wire contract or glossary edit.
