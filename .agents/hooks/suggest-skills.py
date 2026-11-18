#!/usr/bin/env python3
"""
suggest-skills.py

Advisory hook: maps the files touched in this change to the UltiCortex skills
that cover them, so the relevant expertise is loaded while the work is still
open rather than recalled during review.

Never fails a build — steering belongs in the rules; this is the reminder.
"""

import fnmatch
import os
import subprocess
import sys

# skill -> (globs, one-line reason)
SKILL_TRIGGERS = {'conan-2': (['**/conanfile.py', '**/conanfile.txt', '**/conandata.yml'], 'Dependency graph, profiles, cross-compilation and packaging are Conan 2 concerns'), 'cmake': (['**/CMakeLists.txt', '**/*.cmake', '**/CMakePresets.json'], 'Target-centric CMake, presets, and CTest wiring — avoid reinventing build logic or reaching for directory-scoped commands'), 'python-pro': (['**/*.py'], 'Type-safe, production-ready Python: typing coverage, async patterns, and the conventions mined into the Python rule'), 'ultimaker-material-knowledge': (['**/*.xml.fdm_material'], 'Material profile semantics and the polymer/processing physics behind the values being changed')}

_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
).stdout.strip()
if _ROOT:
    os.chdir(_ROOT)


def changed_files():
    for args in (["diff", "--cached", "--name-only"], ["diff", "--name-only", "HEAD"]):
        res = subprocess.run(["git", *args], capture_output=True, text=True)
        files = [f for f in res.stdout.splitlines() if f.strip()]
        if files:
            return files
    return []


def matches(path: str, glob: str) -> bool:
    """fnmatch has no notion of `**`, and its `*` already spans `/`. A pattern
    anchored with `**/` must therefore also be tried without that prefix, or it
    would never match a file sitting at the repository root."""
    if fnmatch.fnmatch(path, glob):
        return True
    if glob.startswith("**/") and fnmatch.fnmatch(path, glob[3:]):
        return True
    return False


def main():
    files = changed_files()
    if not files:
        return
    hits = {}
    for skill, (globs, reason) in SKILL_TRIGGERS.items():
        for path in files:
            if any(matches(path, g) for g in globs):
                hits.setdefault(skill, [reason, []])[1].append(path)
    if not hits:
        return
    print("Relevant UltiCortex skills for the files you are changing:")
    for skill, (reason, paths) in sorted(hits.items()):
        sample = ", ".join(paths[:3]) + (" ..." if len(paths) > 3 else "")
        print("  - {}: {}".format(skill, reason))
        print("      triggered by: {}".format(sample))
        print("      gh skill install Ultimaker/UltiCortex {}".format(skill))


if __name__ == "__main__":
    main()
