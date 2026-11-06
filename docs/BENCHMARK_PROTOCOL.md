# Benchmarking and reporting protocol

**Status:** Working protocol. It must be finalized and validated through the dummy JUBE workflow in Phase 6 before STREAM begins.

## 1. Comparison levels

### Level 1: equivalent baseline

Keep the following equivalent between Kokkos and native CUDA:

- Algorithm and mathematical operations.
- FP64 values and arithmetic.
- Data layout and input datasets.
- Domain decomposition and iteration mapping.
- Compiler family, optimization level, and GPU architecture target.
- Numerical validation requirements.
- Timing boundaries and synchronization methodology.

Do not use fast-math or model-specific cleverness in only one baseline.

### Level 2: tuned implementations

Before tuning each kernel, freeze:

- Maximum variants per implementation: `N = ___`.
- Maximum profiling runs per implementation: `P = ___`.
- The primary selection metric and acceptance criteria.

Both implementations receive the same `N` and `P`. Record accepted and rejected variants. A variant includes a documented hypothesis, source change, correctness evidence, measurement evidence, and decision.

## 2. Builds and source state

- Use Release builds, C++20, and `sm_89` on the RTX 4080 Laptop GPU.
- Use the same host-compiler family and NVCC host-compiler selection for both implementations.
- Export and preserve relevant entries from `compile_commands.json` when flag questions arise.
- Do not enable fast-math in baselines. Any tuned experiment affecting arithmetic requires separate numerical review.
- Record the full Git commit. Authoritative measurements require a clean, committed source tree; dirty-tree measurements are development-only.
- Use the same Kokkos release and SHA-256 archive checksum on macOS and Fedora.

## 3. Timing boundaries

Exclude from timed kernel regions:

- Allocation and deallocation.
- Initialization and input generation.
- Host-device transfers.
- Numerical validation.
- Result-file output and other host-side reporting.

For short kernels:

1. Complete warm-up launches before measurement.
2. Synchronize before each measured batch.
3. Time a documented number of launches.
4. Synchronize after the batch.
5. Preserve the raw batch duration and launch count; derive per-launch time only during analysis.

Use CUDA events/error checks and explicit Kokkos fences as appropriate. Keep synchronization semantics equivalent.

## 4. Iterations and ordering

- Initial warm-up count: **10**, adjustable only with a documented calibration reason.
- Measured iterations: **at least 30** per configuration, with batching for short kernels.
- Calibrate batch duration before authoritative runs and freeze it for both implementations of a configuration.
- Interleave Kokkos and CUDA rather than measuring one implementation entirely before the other.
- Use ABBA ordering where practical to reduce systematic thermal or time drift.
- Do not profile during timing runs.

Any protocol adjustment after baseline measurement requires both implementations to be rerun under the adjusted protocol.

## 5. Validation

- Validate before accepting performance results.
- Use a host reference and operation-appropriate FP64 tolerances.
- Record tolerances in each kernel's experiment card.
- Treat a failed or missing validation result as a failed benchmark, not as a missing optional field.
- Include small and boundary-focused correctness cases in addition to performance-sized inputs.

Kernel-specific requirements are documented under [kernels/](kernels/).

## 6. Statistics and relative performance

Retain raw measured times and report:

- Median runtime.
- Interquartile range (IQR).
- Minimum and maximum as diagnostic information, not as the sole selection statistic.
- Derived bandwidth, MLUP/s, or GFLOP/s as appropriate.
- Runtime ratio and relative Kokkos performance:

\[
E_{\mathrm{Kokkos}} = \frac{t_{\mathrm{CUDA}}}{t_{\mathrm{Kokkos}}}
\]

Thus, values above 1 favor Kokkos, 1 indicates equal runtime, and values below 1 favor native CUDA.

## 7. Kernel metrics

- **STREAM Triad:** effective algorithmic traffic is `24 * N` bytes for FP64 `c[i] = a[i] + alpha * b[i]`. Report effective GB/s separately from profiler-measured traffic.
- **Stencil:** MLUP/s uses the number of interior lattice updates, excluding fixed boundaries.
- **CSR SpMV:** GFLOP/s uses `2 * nnz` operations. Preserve per-matrix results rather than reporting only aggregates.

Document all unit conversions in the analysis code.

## 8. Profiling

- Nsight Compute must collect memory-traffic metrics in the pre-STREAM environment gate.
- Profile separately from timing runs because profiling perturbs execution.
- Apply the same profiling budget to Kokkos and CUDA.
- Save selected reports or exports with the kernel, implementation, variant, input, source commit, and environment manifest identified.
- Do not compare algorithmic byte estimates directly with profiler counters without explaining their different meanings.

## 9. Benchmark-day conditions

Before authoritative runs:

- Connect the laptop to AC power.
- Stop unrelated GPU workloads and avoid interactive use.
- Prevent suspend or screen-lock interruption.
- Record power mode and relevant GPU state.
- Check temperature/clocks before and after runs when available.
- Do not change OS, kernel, driver, toolkit, compiler, dependencies, or source during a result group.

Record unavoidable deviations and mark affected results for review rather than silently accepting them.

## 10. Output and retention

The final output schema will be fixed in Phase 6 and tested through JUBE. Every record must identify at least:

- Schema version, kernel, implementation, comparison level, and variant.
- Problem size or dataset, precision, iteration and batch counts.
- Raw timing values and units.
- Validation status and tolerance.
- Derived metrics.
- Git commit and environment-manifest checksum.

Track compact raw measurements, summary CSV files, plots, environment manifests, and selected profiler exports in `results/`. Exclude binaries and disposable JUBE sandboxes. JUBE result tables supplement rather than replace the raw timing data.

Each accepted result group uses this layout:

```text
results/<kernel>/<run-id>/
  environment.json
  raw/             Compact raw timing data
  summary/         Summary CSV tables
  plots/           Reproducible plots
  profiles/        Selected Nsight Compute reports or exports
  README.md        Commands, source revision, deviations, and artifact checksums
```

The per-run README records commands, source revision, deviations, and artifact checksums. Every result group identifies its Git commit and environment-manifest checksum. Dirty-tree or failed-validation runs are development-only and are not published as authoritative results.

## 11. Completion criteria for every kernel

A kernel is complete only when:

- Baseline and tuned implementations pass correctness tests.
- Baseline and tuned raw results are preserved.
- Summary tables and plots are reproducible.
- Equal tuning budgets and all deviations are documented.
- README and the kernel experiment card link to instructions and evidence.
- A fresh build passes correctness tests and a reduced end-to-end JUBE run.
