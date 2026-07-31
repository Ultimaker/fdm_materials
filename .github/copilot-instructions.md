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
