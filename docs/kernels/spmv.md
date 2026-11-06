# CSR SpMV experiment card

**Status:** Not started. Work begins only after the stencil completion gate.

## Research role

SpMV introduces irregular memory access and row-length imbalance. It prevents conclusions from being drawn only from regular memory-bound kernels.

## Dataset gate

Before implementation, record for every matrix:

- Source paper or repository and license.
- Download URL and cryptographic hash.
- Any conversion, reordering, or filtering steps.
- Dimensions, `nnz`, empty rows, stored zeros, and row-length statistics.
- Identical frozen matrix and vector data for both implementations.

## Experiment definition

| Field | Value |
| --- | --- |
| Operation | `y = A * x` |
| Representation | Compressed Sparse Row (CSR) |
| Values | FP64 |
| Indices | 32-bit |
| Warm-up | Initial protocol default: 10 |
| Measured iterations | At least 30, with calibrated batching |
| Validation tolerance | To be fixed before implementation |
| Level 2 variant budget `N` | `___` per implementation |
| Level 2 profiling budget `P` | `___` per implementation |

## Level 1 baseline

- One thread per matrix row.
- Serial inner loop over stored row entries.
- Equivalent CSR treatment in Kokkos and CUDA.
- Identical row ordering, within-row column ordering, empty-row handling, stored-zero treatment, and input data.
- Matrix conversion/preprocessing and validation outside timed regions.

## Validation plan

- Host reference using identical FP64 values and ordering.
- Empty rows, single-entry rows, highly imbalanced rows, and general matrices.
- Record FP64 tolerance and reject timings after any validation failure.

## Measurements

- Raw timing data, median runtime, and IQR for every matrix.
- GFLOP/s using `2 * nnz` operations.
- Runtime ratio and `E_Kokkos`.
- Selected Nsight Compute memory-traffic measurements in separate profiling runs.
- Per-matrix results retained rather than only aggregate averages.

## Level 2 candidates and variant log

Candidates include warp-per-row CUDA and an appropriate Kokkos counterpart, team-per-row or hierarchical execution, and documented row-balancing strategies.

| Variant | Model | Hypothesis and change | Correctness | Timing/profile evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| _Not started_ | | | | | |

## Results and reproduction

All result and reproduction links will be added during Phase 9.
