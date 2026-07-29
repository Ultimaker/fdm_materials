---
description: Guidelines for compiling Debian packages, managing recipes, and deploying to printers.
---
# Debian Packaging, Recipe Management & Printer Deployment

1. **Compiling Debian Packages**:
   - Service build script: `./build_for_ultimaker.sh`.
   - Packages compile into `.deb` artifacts inside local Docker container environments.
2. **Firmware Recipe Integration (`jedi-cookbook`)**:
   - Firmware update images (`.swu`) bundle debian packages specified in `.recipe` files under `S-Line/`, `Falcon/`, `Colorado/`, or `UM3/`.
   - Recipe line format: `deb <package_name> <version>`.
   - Recipe version bumps: Ensure the corresponding `.deb` package artifact is built and published upstream before updating recipe versions.
3. **Deploying Packages & Testing on Printers**:
   - Deploy compiled service packages directly to a networked test printer:
     ```bash
     ../jedi-build/deploy_to_printer.sh deploy <package_name> <printer-ip>
     ```
   - Interactive SSH terminal access to printer:
     ```bash
     ./dev/umssh.sh <printer-ip>
     ```
