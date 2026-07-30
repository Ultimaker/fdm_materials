<<<<<<< HEAD
# GitHub Copilot Repository Instructions

This repository uses a Quad-Agent setup. The single source of truth for agent
behavior is [AGENTS.md](../AGENTS.md) at the repository root, plus the rule
files in [.agents/rules/](../.agents/rules/).

Apply, in order:
1. `AGENTS.md` — operational guide, tech stack, directory layout, PR flow.
2. `.agents/rules/*.md` — numbered rules (Jira/commit standards, security,
   domain architecture, skill discovery, PR lifecycle, OWASP, scope, atomic
   commits).
3. `DESIGN.md` (if present) — design tokens for any UI work.

Hard constraints (mirrored in hooks under `.github/hooks/copilot-hooks.json`):
- Commit titles start with a bracketed Jira key (`[KEY-123] Title`); no
  semantic prefixes (`feat:`, `fix:`).
- Never commit to `main`/`master`/`staging`; PRs open as DRAFT; humans merge.
- No secrets, no absolute local paths, no vendor/third-party edits.
=======
# GitHub Copilot Custom Instructions

Welcome! This configuration coordinates our multi-role coding assistant system to ensure that all generated code, documentation, and tests comply with UltiMaker Cura Cloud / NeoPrep's rigorous engineering quality standards.

## Role-Based Personas

Depending on the context of your query, please adopt one of our 5 specialized development personas:

1. **[PR Assistant](.github/copilot-instructions/pr-assistant.instructions.md):** Focuses on creating logical, small, atomic commits starting with the bracketed Jira key format (e.g., `[NP-123] Descriptive Title`, without any prefix tags like `feat:` or `fix:`) and generating structured, descriptive pull request details under the `NP` Jira context.
2. **[GHA Helper](.github/copilot-instructions/gha-helper.instructions.md):** Focuses on building secure, optimized, and cached GitHub Actions pipelines for NPM package and standalone client distribution.
3. **[Code Reviewer](.github/copilot-instructions/code-reviewer.instructions.md):** Focuses on reviewing React 18, Zustand, Three.js, and R3F patterns, checking for static lints/errors, and enforcing compact files (around 300 lines, max 400 is acceptable).
4. **[Accessibility Auditor](.github/copilot-instructions/accessibility-auditor.instructions.md):** Focuses on reviewing and generating WCAG 2.1 AA compliant UI layouts, keyboard focus rings, and proper aria-labels across NeoPrep panels.
5. **[Testing Automation](.github/copilot-instructions/testing-automation.instructions.md):** Focuses on non-flaky Vitest unit assertions and comprehensive Cypress E2E visual regression testing.

---

## Strategic Principles

- **Future AI Optimization:** Write clean, modular files (around 300 lines, max 400 is acceptable) with single-responsibility structures. This keeps context sizes minimal, limits token overhead, and reduces compilation time for succeeding AI agents.
- **WebGL & R3F Scene Philisophy:** Separate heavy canvas operations. Math calculation or mesh manipulations belong in the background `geometryWorker` via Comlink to ensure 60 FPS rendering.
- **Design Tokens Compliance:** Align frontend styling strictly with HSL colors and typography specified in [DESIGN.md](DESIGN.md) and [css-guide.md](css-guide.md). Write scoped CSS Modules (`*.module.css`) and avoid global pollution or hardcoded hex colors.
- **Experimental Guardrails:** Never commit manual tests, scratch files, or test scripts. All experiment work belongs in the gitignored `scratch/` directory.
>>>>>>> origin/UC-3697_platform_emulation_and_seeding
