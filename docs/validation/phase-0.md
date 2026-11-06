# Phase 0 validation evidence

**Date:** 2026-11-05  
**Scope:** Repository scaffold only; no Kokkos integration, benchmark kernels, or performance measurements.

## Environment

| Tool | Validated version |
| --- | --- |
| OS | macOS 27.2, arm64 |
| Git | 2.54.0 (Apple Git-157) |
| CMake | 4.4.5 |
| Ninja | 1.13.2 |
| C++ compiler | Apple Clang 21.0.0 (clang-2100.3.34.2) |

Ninja 1.13.2 was installed through Homebrew because it was the only missing tool required by the shared presets. Homebrew also refreshed its repository metadata; no project dependency versions were frozen in this phase.

## Checks

### JSON syntax

```bash
python3 -m json.tool CMakePresets.json
```

Result: passed.

### Configure

```bash
cmake --preset macos-serial
```

Result: passed cleanly with C++20 and compile-command export enabled. Build files were generated under the ignored `build/macos-serial/` directory.

### Build

```bash
cmake --build --preset macos-serial
```

Result: passed; Ninja reported `no work to do`, as expected for the intentionally empty scaffold.

### Test driver

```bash
ctest --preset macos-serial
```

Result: CTest discovered the build and reported `No tests were found!!!`. This is expected: smoke targets are introduced in Phases 3-5, and benchmark-kernel tests remain blocked by the readiness gate.

## Outcome

Phase 0 is complete. The next phase is the full macOS host-tool, Kokkos Serial, and JUBE setup.
