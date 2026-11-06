# STREAM Triad experiment card

**Status:** Blocked by the pre-STREAM readiness gate in [../PIPELINE.md](../PIPELINE.md).

## Research role

STREAM is the regular, streaming, memory-bound starting point. It establishes whether Kokkos and native CUDA behave similarly when the access pattern is simple and regular.

## Experiment definition

| Field | Value |
| --- | --- |
| Operation | `c[i] = a[i] + alpha * b[i]` |
| Precision | FP64 values and arithmetic |
| Alpha | To be fixed before implementation |
| Input initialization | To be fixed before implementation |
| Array sizes | To be calibrated: larger than cache, with safe headroom in 12 GB VRAM |
| Warm-up | Initial protocol default: 10 |
| Measured iterations | At least 30, with calibrated batching |
| Validation tolerance | To be fixed before implementation |
| Level 2 variant budget `N` | `___` per implementation |
| Level 2 profiling budget `P` | `___` per implementation |

## Level 1 baseline

- One thread per element.
- GPU-resident arrays larger than cache.
- Equivalent memory layout and iteration mapping.
- Identical input values and arithmetic.
- No fast-math or model-specific launch cleverness.
- Allocation, initialization, transfers, and validation outside timed regions.

## Validation plan

- Host reference using identical inputs.
- Small, odd-sized, and performance-sized arrays.
- Record FP64 tolerance and check every output element.
- Reject all timings from a failed or missing validation.

## Measurements

- Raw batch and per-launch timing data.
- Median runtime and IQR.
- Runtime ratio and `E_Kokkos`.
- Effective bandwidth in GB/s using `24 * N` algorithmic bytes per Triad.
- Selected Nsight Compute memory-traffic measurements during separate profiling runs.

## Level 2 variant log

Freeze `N` and `P` before adding rows.

| Variant | Model | Hypothesis and change | Correctness | Timing/profile evidence | Decision |
| --- | --- | --- | --- | --- | --- |
| _Not started_ | | | | | |

## Results and reproduction

- Baseline instructions: not yet available.
- Tuned instructions: not yet available.
- Raw results: not yet available.
- Summary and plots: not yet available.
- Environment manifests: not yet available.
- Final STREAM conclusion: not yet available.
