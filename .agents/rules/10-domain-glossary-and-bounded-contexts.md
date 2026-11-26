# Rule 10: Domain Glossary & Four Bounded Contexts

**Applies to**: All code, comments, documentation, ADRs, and commit messages across `unimotion`.

## 1. The Four Bounded Contexts & Linked Obsidian Glossaries
1. **Ubiquitous Core & Cross-Context Seams** (`unimotion` meta-repository)
   - Vocabulary: [`GLOSSARY.md`](../../GLOSSARY.md), [`docs/05-Glossary/00-Ubiquitous-Core/context-ubiquitous-core.md`](../../docs/05-Glossary/00-Ubiquitous-Core/context-ubiquitous-core.md)
   - Owns cross-cutting architectural invariants (`Deep Module`, `Hermetic Seam`, `Whole-Chain Forensics`, `Meten is Weten`, `Technology Readiness Tier`, `Access Classification`).
2. **Bounded Context 1 — Preparation & Slicing** (`Cura-unimotion`, `CuraEngine-unimotion` on branch `CURA-13401-unimotion`)
   - Vocabulary: [`docs/05-Glossary/01-Preparation-and-Slicing/context-slicing.md`](../../docs/05-Glossary/01-Preparation-and-Slicing/context-slicing.md)
   - Owns CAD surface conformality, setting stack resolution, `TaggedGeometry` polygon booleans, Arachne medial-axis variable bead widths, and `CurveOptimalWindowedDp` (`G2`/`G3`/`G5` fitting).
3. **Bounded Context 2 — Lossless Intent Wire Contract** (`UFP` archive & G/M-code dialect between Slicer, SOM, and RT)
   - Vocabulary: [`docs/05-Glossary/02-Lossless-Intent-Wire/context-wire.md`](../../docs/05-Glossary/02-Lossless-Intent-Wire/context-wire.md)
   - Owns `StreamingDeflateUfpBuffer`, curved motion primitives (`G2`/`G3`/`G5`/`G6`), extrusion ramps (`Q`/`B` in $\text{mm}^2$ on `G1`/`G2`/`G3`; `W`/`B` in $\text{mm}$ on `G5`), dependency masks (`M12084`), and feature policies (`M12095`–`M12097`).
4. **Bounded Context 3 — SOM Host Orchestration** (`opinicus`, `okuda`, `misp-service`, `marvin-service`, `print-process-reporting`, `python3-uc-firmware-upgrade`, `stardust-printer_console`, `misc-product-specific`, `jedi-build`, `jedi-cookbook` on branch `EMB-476-ultimoco-cpp23`)
   - Vocabulary: [`docs/05-Glossary/03-SOM-Host-Orchestration/context-som.md`](../../docs/05-Glossary/03-SOM-Host-Orchestration/context-som.md)
   - Owns UFP job streaming, pre-print DAG scheduling, non-volatile calibration JSON persistence, touch UI, Material Station routing, and 2 kHz Valkey telemetry publishing.
5. **Bounded Context 4 — Real-Time Physical Control & Verification** (`ultimoco`, `bench-telemetry`, `UltiTools` on branch `EMB-476-ultimoco-cpp23`)
   - Vocabulary: [`docs/05-Glossary/04-Real-Time-Physical-Control/context-rt.md`](../../docs/05-Glossary/04-Real-Time-Physical-Control/context-rt.md) & [`docs/05-Glossary/05-Quality-and-Verification/context-quality-verification.md`](../../docs/05-Glossary/05-Quality-and-Verification/context-quality-verification.md)
   - Owns zero-heap (`_HeapSize = 0`) ISO C++23 real-time trajectory synthesis (integrated Cheetah 6-axis quintic Hermite planner), sample-rate coordinate/bed compensation (`ZFlow`), input shaping (`ID1`/`ID5`), convective extrusion (`ID4`/`ID16`), thermal enthalpy estimation (`ID8`/`ID9`), 4-state UD Kalman IMU fusion (`ID11`), and the 75 MHz `twin_cli` Digital Twin.

## 2. Mandatory Term Disambiguation (from [`GLOSSARY.md`](../../GLOSSARY.md))
- Use **Toolpath Fitter** for `CuraEngine-unimotion`'s `G2`/`G3`/`G5` curve fitting stage; use **Trajectory Planner** exclusively for `ultimoco`'s real-time 6-axis quintic Hermite S-curve synthesis.
- Use **Toolpath Primitive** for a wire move (`G0`/`G1`/`G2`/`G3`/`G5`); use **Trajectory Segment** for a 2 kHz time-parameterized quintic phase inside `ultimoco`.
- Use **Bead Cross-Section (`q`)** ($\text{mm}^2$, encoded via `Q`/`B` on `G1`/`G2`/`G3`) vs **Bead Width (`w`)** ($\text{mm}$, encoded via `W`/`B` on `G5`).
- Use **Calibration Persistence** for `opinicus` JSON storage on the SOM vs **Real-Time Coordinate Compensation** for `ultimoco` sample-rate transforms.
- Whenever introducing a new domain concept, opcode, or physical state variable, create its atomic `docs/05-Glossary/<context>/Term - <Name>.md` note and link it in `GLOSSARY.md`.
