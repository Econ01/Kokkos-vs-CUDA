# Phase 3 native CUDA validation evidence

**Date:** 2026-11-18  
**Source commit:** `32be4b0829d6472b83cc2a9d2e3f457c88b4b7af`  
**Target:** `cuda_smoke`  
**Build preset:** `fedora-cuda`

## Scope

This smoke test validates native CUDA device detection, allocation,
a trivial kernel launch, synchronization, error checking, device-to-host
copying, numerical validation, and cleanup. It is not a performance
benchmark.

## Direct execution

Command:

```bash
python3 scripts/remote_fedora.py run --target cuda_smoke --preset fedora-cuda
```

Result: **passed**.

The program reported:

```
Number of CUDA devices: 1
CUDA device successfully set.
Device Name: NVIDIA GeForce RTX 4080 Laptop GPU
Total Global Memory: 11925 MB
Compute Capability: 8.9
Allocated device buffer.
Kernel launched.
CUDA device synchronized.
Device memory copied to host successfully.
Validated all 256 values successfully.
```

The process completed successfully with exit status 0.

## CTest execution

Command:

```bash
python3 scripts/remote_fedora.py test --preset fedora-cuda --verbose
```

Result: 100% tests passed, 0 tests failed out of 2

Individual tests:
- kokkos_smoke: passed.
- cuda_smoke: passed.
The Kokkos test also reported:
- Kokkos 5.2.2.
- Default execution device: CUDA.
- GPU architecture: ADA89.
- CUDA 13.5.
- 257 values validated with reduction result 65792.
- Successful initialization and finalization.
- 
## Outcome

The native CUDA smoke test passed directly and through CTest. Native
CUDA execution on the intended sm_89 device is therefore validated.
No JUBE benchmark or performance measurement was performed.