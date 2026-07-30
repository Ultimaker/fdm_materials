#!/usr/bin/env python3
"""Pre-commit hook: Verify submodule tracking in git index."""

import configparser
import os
import subprocess
import sys


def check_submodules() -> bool:
    # 1. Check if main branch has .gitmodules when current branch lacks it
    if not os.path.exists(".gitmodules"):
        try:
            main_modules = subprocess.check_output(
                ["git", "show", "main:.gitmodules"], stderr=subprocess.DEVNULL, text=True
            )
            if main_modules.strip():
                print("SUBMODULE INTEGRITY ERROR: .gitmodules exists on 'main' but is missing on current branch!")
                print("Restore it with: git checkout main -- .gitmodules")
                return False
        except Exception:
            pass
        return True

    # 2. Parse .gitmodules
    config = configparser.ConfigParser()
    try:
        config.read(".gitmodules")
    except Exception as e:
        print(f"SUBMODULE INTEGRITY ERROR: Failed to parse .gitmodules: {e}")
        return False

    has_error = False
    for section in config.sections():
        if "path" in config[section]:
            submodule_path = config[section]["path"]
            try:
                ls_tree = subprocess.check_output(
                    ["git", "ls-tree", "HEAD", submodule_path], text=True
                ).strip()
                if not ls_tree or "160000" not in ls_tree:
                    print(f"SUBMODULE INTEGRITY ERROR: Submodule '{submodule_path}' is defined in .gitmodules but missing from git index!")
                    print(f"Restore it with: git checkout main -- {submodule_path}")
                    has_error = True
            except Exception:
                print(f"SUBMODULE INTEGRITY ERROR: Submodule '{submodule_path}' check failed in git index.")
                has_error = True

    return not has_error


if __name__ == "__main__":
    if not check_submodules():
        sys.exit(1)
    sys.exit(0)
