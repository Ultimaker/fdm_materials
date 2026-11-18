---
description: Reuse before rebuild — search existing and published dependencies, and check licence compatibility, before writing new code.
---
# Dependency Management — Do Not Reinvent the Wheel

Hand-rolled implementations of solved problems are the most expensive code in a
repository: they carry no upstream security fixes, no community documentation,
and no tests but the ones you happen to write. Before implementing any
non-trivial capability, establish that it does not already exist.

This applies at **four** points, not just while typing.

## 1. During Design

Before choosing an approach, state in the design or plan **which existing
dependency provides this, or why none does**. "We will write our own X" is a
decision that needs a reason — an unmet requirement, a licence conflict, or an
unmaintained ecosystem — not a default.

## 2. Before Adding Anything — Check What Is Already Here

The cheapest dependency is one already in the manifest: no new supply chain, no
new licence, no new review.

- **Python** — already-declared dependencies live in `pyproject.toml / requirements.txt`. Search them first:
  ```bash
  pip list  # or: uv pip list
  ```

Also check the internal ecosystem: a sibling UltiMaker repository or a shared
library may already solve this, and reusing it keeps behaviour consistent across
products.

## 3. If Nothing Exists Internally — Search the Registry

- **Python**:
  ```bash
  pip index versions <package>
  # Inspect metadata and licence before adding:
  pip show <package>  # or: uv add --dry-run <package>
  ```

Judge a candidate on evidence, not popularity alone:

- **Maintenance**: recent releases, issues being answered, no unpatched CVEs.
- **Fit**: solves the actual problem without dragging in a framework.
- **Weight**: for frontend code, check the bundle cost; for embedded and WASM
  targets, check binary size and whether it allocates.
- **Transitive cost**: a package with a large dependency tree imports every one
  of that tree's licences and vulnerabilities too.

Prefer the option this repository or its siblings already use over an equivalent
alternative — consistency is worth more than a marginal feature advantage.

## 4. Licence Compatibility — Check Before Adding, Not After

This project is licensed **LGPL-3.0** (declared in `conanfile.py`).


Verify that each new dependency's licence is compatible with this project's
licence and its distribution model. Strong copyleft licences (GPL, AGPL) impose
obligations on distributed software; a package with no declared licence is "all
rights reserved" and cannot be used at all.

Record the licence of every dependency you add. If you cannot determine it, that
is itself a blocker.

## 5. When Opening the Pull Request

Any new dependency must be called out explicitly in the PR description with:

- **What it replaces** — the code you did not write.
- **Why this one** — maintenance status and the alternatives rejected.
- **Its licence**, and why that is compatible with the LGPL-3.0 licence.
- **Its transitive footprint** — how many packages it actually pulls in.

Pin the version, commit the updated lockfile in the same change, and never add a
dependency as a drive-by in a change about something else.
