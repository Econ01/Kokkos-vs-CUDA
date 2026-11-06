# Seven-point stencil experiment card

**Status:** Not started. Work begins only after the STREAM completion gate.

## Research role

The stencil introduces multidimensional iteration and data reuse. It tests whether conclusions from STREAM survive when mapping and reuse become important.

## Experiment definition

| Field | Value |
| --- | --- |
| Operation | Constant-coefficient 3D seven-point stencil |
| Computation | Out-of-place, FP64 |
| Boundaries | Fixed; interior points only |
| Initial grids | `256^3` and `512^3`, subject to documented hardware limits |
| Warm-up | Initial protocol default: 10 |
| Measured iterations | At least 30, with calibrated batching |
| Validation tolerance | To be fixed before implementation |
| Level 2 variant budget `N` | `___` per implementation |
| Level 2 profiling budget `P` | `___` per implementation |

## Level 1 baseline

- Identical contiguous x-dimension layout.
- Equivalent flattened iteration mapping.
- Same coefficients, input, boundaries, and arithmetic.
- No fast-math or model-specific mapping cleverness.
- Allocation, initialization, transfers, and validation outside timed regions.

## Validation plan

- Host reference with identical coefficients and input.
- Small non-cubic grids as well as performance-sized grids.
- Verify every interior result and unchanged fixed boundaries.
- Record FP64 tolerance and reject timings after any validation failure.

## Measurements

- Raw timing data, median runtime, and IQR.
- MLUP/s based on actual interior lattice updates.
- Runtime ratio and `E_Kokkos`.
- Selected Nsight Compute memory-traffic measurements in separate profiling runs.

## Level 2 candidates and variant log

Candidates include `Kokkos::MDRangePolicy` and corresponding CUDA mappings, layouts, team/hierarchical execution, and other protocol-compliant optimizations. Candidates do not count as completed variants until documented and measured.

| Variant | Model | Hypothesis and change | Correctness | Timing/profile evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| _Not started_ | | | | | |

## Results and reproduction

All result and reproduction links will be added during Phase 8.
