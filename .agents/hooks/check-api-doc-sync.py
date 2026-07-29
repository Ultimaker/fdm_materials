#!/usr/bin/env python3
import sys, subprocess

INTERFACE_PATTERNS = ["griffin/interface/", "interface/http/", "endpoints/", "routes/"]
DOC_PATTERNS = ["docs/api_documentation.json", "openapi", "swagger"]

def check_api_doc_sync():
    result = subprocess.run(["git", "diff", "--cached", "--name-only"], capture_output=True, text=True)
    staged_files = [f.strip() for f in result.stdout.splitlines() if f.strip()]
    if not staged_files:
        return

    interface_changed = [f for f in staged_files if any(p in f for p in INTERFACE_PATTERNS)]
    doc_changed = [f for f in staged_files if any(p in f.lower() for p in DOC_PATTERNS)]

    if interface_changed and not doc_changed:
        print("=" * 80)
        print("ERROR: API DOCUMENTATION DESYNCHRONIZATION DETECTED!")
        print(f"The following interface/endpoint files were modified:")
        for f in interface_changed:
            print(f"  - {f}")
        print("However, endpoint documentation (docs/api_documentation.json or OpenAPI specs) was NOT updated!")
        print("Whenever REST/HTTP or DBus interfaces change, you MUST update the documentation.")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    check_api_doc_sync()
