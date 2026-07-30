---
paths:
  - "**/*.xml.fdm_material"
---
# Material Profile Guidelines (fdm_materials)

1. **Schema Compliance**:
   - All profile changes MUST pass `./run_check_material_profiles.sh`.
2. **GUID Stability**:
   - Material GUIDs must remain strictly stable across profile updates for WASM slicing resolution.
