# Phase 1 Kokkos validation evidence

**Date:** 2026-11-07  
**Scope:** Pinned Kokkos 5.2.2 `FetchContent` integration and macOS Serial smoke validation.

## Dependency verification

- Release archive: https://github.com/kokkos/kokkos/releases/download/5.2.2/kokkos-5.2.2.tar.gz
- Official checksum file: https://github.com/kokkos/kokkos/releases/download/5.2.2/kokkos-5.2.2-SHA-256.txt
- Verified archive SHA-256: `d6557aaef39302282a15f9c770433d1fcdf4e961dfd6d9ed726b9d0d0f546b9f`

The computed SHA-256 matched the official archive entry. The same URL and hash are pinned in `cmake/Kokkos.cmake`.

## Configure

```bash
cmake --preset macos-serial
```

Result: passed. CMake reported Kokkos 5.2.2, C++20, Apple Clang 21, and only the Serial execution backend.

## Build

```bash
cmake --build --preset macos-serial
```

Result: passed. Kokkos and the `kokkos_smoke` target compiled and linked successfully in Release mode.

## Direct smoke execution

```bash
./build/macos-serial/smoke/kokkos_smoke
```

The program reported:

- Kokkos 5.2.2.
- Serial as the default execution space.
- `KOKKOS_ENABLE_SERIAL: yes`.
- All 257 initialized values validated through a host mirror.
- Reduction result `65792`, matching the host-reference value.
- Successful initialization, parallel execution, reduction, and finalization.

## CTest

```bash
ctest --preset macos-serial
```

Result:

```text
100% tests passed, 0 tests failed out of 1
```

No CUDA backend was enabled, and no performance measurements were taken.
