# Material GUID Stability

**Category:** fdm_materials  **Confidence:** high

**Rule:**
> Material profile GUIDs must remain strictly stable. They are injected dynamically into WASM slicing runs inside the user's web browser, so changing a GUID will break slicing compatibility. Never modify an existing material's GUID.
