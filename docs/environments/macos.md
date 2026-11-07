# macOS development environment

**Validated:** 2026-11-07  
**Role:** Host-only development and correctness smoke tests. No CUDA execution or authoritative GPU timing is performed on this system.

## Build tools

| Tool | Validated version |
| --- | --- |
| Git | 2.54.0 (Apple Git-157) |
| CMake | 4.4.5 |
| Ninja | 1.13.2 |
| C++ compiler | Apple Clang 21.0.0 (clang-2100.3.34.2) |
| C++ standard | C++20 |

## Python and JUBE

| Component | Validated version |
| --- | --- |
| Python | 3.15.2 |
| JUBE | 2.7.1 |
| PyYAML | 6.0.3 |
| `ruamel.yaml` | 0.19.1 |
| NumPy | 2.5.4 |
| pandas | 3.1.1 |
| matplotlib | 3.11.2 |
| Python dependency lock | `requirements/macos-lock.txt` — validated against the environment |

The lock file contains 17 entries and exactly matches `pip freeze` from the clean project environment. Dependency, import, hello-world, result-generation, and YAML checks are recorded in [../validation/phase-1-jube.md](../validation/phase-1-jube.md).

## Kokkos

| Field | Validated value |
| --- | --- |
| Version | 5.2.2 |
| Integration | CMake `FetchContent` |
| Archive URL | https://github.com/kokkos/kokkos/releases/download/5.2.2/kokkos-5.2.2.tar.gz |
| SHA-256 | `d6557aaef39302282a15f9c770433d1fcdf4e961dfd6d9ed726b9d0d0f546b9f` |
| Backend on macOS | Serial |
| Build type | Release |

The archive hash matches the official `kokkos-5.2.2-SHA-256.txt` file. Configuration and build evidence is recorded in [../validation/phase-1-kokkos.md](../validation/phase-1-kokkos.md).
