---
description: Design system single source of truth (DESIGN.md), component reuse, scoped styling, Storybook, and accessibility standards for web and React UI development.
paths:
  - "src/**/*.tsx"
  - "src/**/*.jsx"
  - "src/**/*.ts"
  - "src/**/*.js"
  - "src/**/*.vue"
  - "src/**/*.scss"
  - "src/**/*.css"
  - "src/**/*.module.css"
  - "**/components/**/*.tsx"
  - "**/views/**/*.tsx"
  - "DESIGN.md"
---
# Frontend & Web UI Architecture Standards

0. **Load Skills before UI work**:
   - Load `web-accessibility-standard` for WCAG 2.1 AA checklist, keyboard navigation, and focus indicators.

1. **DESIGN.md as Single Source of Truth**:
   - **`DESIGN.md` is the absolute single source of truth** for all visual styles, HSL color palettes, spacing rhythm, typography, elevations, rounded corners, responsive grid breakpoints, and component state transitions.
   - **MUST NOT use hardcoded values**: Do NOT hardcode raw hex colors, static pixel margins/paddings, or hardcoded font sizes in components or rule files.
   - **ALWAYS read `DESIGN.md`** before implementing or updating any UI component. All styles must map directly to tokens defined in `DESIGN.md`.

2. **Component Reuse First**:
   - Always reuse existing UI components from `@ultimaker/stardust-web` or local shared atomic components before creating new ones.

3. **Scoped Styling & CSS Modules**:
   - Write scoped styling using CSS Modules (`*.module.css`) or SCSS Modules (`*.module.scss`).
   - Never use inline React `style` objects for static styling (except dynamic real-time canvas positioning or dragging).

4. **Storybook Coverage**:
   - Every UI component MUST have a corresponding `.stories.tsx` file covering all visual states (default, hover, active, focus, disabled, responsive, and dark mode).

5. **Accessibility (WCAG 2.1 AA)**:
   - Ensure all interactive controls have accessible names (`aria-label` or visible text), semantic markup, and visible focus indicators.
