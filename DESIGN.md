# Architecture & System Topography (DESIGN.md)

## 1. System Overview: fdm_materials

This document details the architectural topography, C4 container boundaries, network interfaces, and operational guidelines for `fdm_materials`.

---

## 2. C4 Container Architecture

```
[ Material Profiles (XML) ] ──> [ check_material_profiles.py ] ──> [ Packaged FDM Materials (CMake/Conan) ]
```

---

## 3. Network Topography & Port Allocations

- **HTTP Gateway Interface**: Configured via environment parameters.
- **Internal Services**: Bound strictly to local bridge network interfaces.

---

## 4. Design Patterns & Conventions

- **SOLID Principles**: Single responsibility modules, interface isolation.
- **YAGNI & KISS**: Keep file footprint concise (prefer <300 lines per file).
