---
name: no-hardcoded-speed-multipliers-or-profile-overrides
description: Prohibit hardcoded speed/flow/width multipliers or clamps in CuraEngine and prohibit ad-hoc printer profile overrides in ultimaker.def.json or NGP profiles that diverge from cura-private-data.
trigger: always_on
---
# Rule 25: No Hardcoded Slicer Speed Multipliers or Unauthorized Printer Profile Overrides

**Applies to**: `CuraEngine-unimotion`, `Cura-unimotion`, `cura-private-data`, and all agents/contributors working on slicing or printer definitions.

> **Why this rule exists**: Ad-hoc hardcoded speed clamps, motion-intent multipliers, and unauthorized `.def.json`/`.inst.cfg` profile overrides made NGP and UltiMaker prints substantially slower, less accurate, and visually uglier — directly sabotaging both print quality and productivity.

## 1. Never Hardcode Speed, Flow, or Width Multipliers/Clamps in `CuraEngine`
- **All feature speeds come exclusively from resolved Cura settings** (and their setting formulas in `.def.json` / `.inst.cfg`).
- The **only** permitted runtime speed reductions in `CuraEngine` are the explicit, user-configurable process features:
  1. Overhang speed multipliers (`wall_overhang_speed_factors` / `bridge_*`)
  2. Cooling / minimum layer time clamping (`cool_min_layer_time`, `cool_min_speed`)
  3. Explicit user-enabled gradual flow / max volumetric flow limiters
- **NEVER** add hardcoded speed ratios, floors, or caps in C++ (e.g., `2 * speed_wall_0` skin caps like `clampSkinSpeedToWallOuterBound`, or `0.65x`/`0.75x` roofing wall speed overrides like `smoothRoofingInnerWallConfig`).
- **NEVER** multiply emitted G-code feedrates (`F`) or preview widths by motion-intent, corner-policy, input-shaper, or pressure-advance policy factors (e.g., `kIntentFactors`, `kCornerFactors`, `kShaperFactors`, `kPaFactors`). Motion-intent policies (`M12095`) communicate **intent** to the motion controller (`Ultimoco`); they must **not** silently alter commanded feedrates in the slicer.

## 2. Never Invent Printer Profile Overrides or Diverge NGP from `cura-private-data`
- **Do NOT push opinionated setting changes into `ultimaker.def.json`** (e.g., overriding `inset_direction`, `cool_fan_speed_0`, `wall_overhang_angle`, `wall_overhang_speed_factors`, `skin_material_flow`, `bridge_wall_speed`, or `retraction_extrusion_window`) for all UltiMaker printers. Print-process engineers own printer profiles and setting formulas.
- **NGP definitions and quality profiles (`ultimaker_ngp_small`, `ultimaker_ngp_big`, `resources/quality/ultimaker_ngp_small/*`) MUST match canonical `cura-private-data` verbatim** (aside from visual platform mesh/texture metadata). Do not invent custom `speed_layer_0`, `top_thickness`, `speed_flooring`, `retraction_hop_enabled`, or `support_z_distance` overrides in `Cura-unimotion`.
- If a print-quality issue is observed on a specific printer, open a ticket for the Print Process / Materials team or fix the underlying physics/firmware/slicer bug — do **not** silently patch base `.def.json` or `.inst.cfg` files to mask it.
