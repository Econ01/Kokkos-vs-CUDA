# Project development pipeline

This is the living checklist for the project. Work proceeds one kernel at a time, and no benchmark kernel starts before its predecessor's completion gate.

## How to use this checklist

- Validation evidence includes the date, command, result, and linked artifact.
- **Stop gates** block dependent work until their requirements pass.
- Current phase: **Phase 2, Fedora 45 base system and NVIDIA driver**.
- Next kernel: **STREAM**, but only after the pre-STREAM readiness gate.

## Phase 0 — Repository and documentation foundation

- [x] Create the initial CMake, documentation, benchmark, smoke, test, script, kernel, and result directories.
- [x] Add concise instructor-facing README and project-status table.
- [x] Add this living pipeline and per-kernel experiment cards.
- [x] Document environment roles, version freezing, and the Fedora 45 compatibility exception.
- [x] Define the JSON environment-manifest format and sensitive-data exclusions.
- [x] Draft the common timing, validation, tuning, profiling, and reporting protocol.
- [x] Add CMake configure/build/test presets for macOS Serial, Fedora Serial, and Fedora CUDA.
- [x] Exclude build trees, virtual environments, disposable JUBE runs, and editor files from Git.
- [x] Keep curated results separate from disposable run directories.
- [x] Validate the intentionally empty CMake scaffold on macOS ([evidence](validation/phase-0.md)).

## Phase 1 — macOS development environment

- [x] Install or update Git, CMake, Ninja, the Xcode compiler toolchain, and a current compatible Python.
- [x] Select one Python manager and a current compatible Python interpreter.
- [x] Create an isolated project Python environment.
- [x] Install JUBE, PyYAML, `ruamel.yaml`, NumPy, pandas, and matplotlib.
- [x] Record exact Python dependency versions after validation ([environment record](environments/macos.md)).
- [x] Verify Git, CMake, Ninja, Python, and JUBE versions ([environment record](environments/macos.md)).
- [x] Select the latest compatible Kokkos release and record its official archive URL and SHA-256 checksum ([environment record](environments/macos.md)).
- [x] Add the pinned Kokkos `FetchContent` integration and Serial smoke target.
- [x] Build the smoke target with `macos-serial` in Release mode.
- [x] Validate Kokkos initialization, a small parallel operation, a reduction, and finalization against a host reference.
- [x] Register and pass the smoke test through CTest ([validation evidence](validation/phase-1-kokkos.md)).
- [x] Run JUBE hello-world and a complete run/analyse/result cycle ([validation evidence](validation/phase-1-jube.md)).
- [x] Verify YAML parsing and schema validation ([validation evidence](validation/phase-1-jube.md)).
- [x] Save the macOS environment manifest and smoke-test evidence ([environment record](environments/macos.md)).
- [x] Confirm that no macOS timing enters GPU comparison tables.

## Phase 2 — Fedora 45 base system and NVIDIA driver

### Base tools

- [x] Perform the initial system update before freezing versions.
- [x] Install the required post-install development tools:

```bash
sudo dnf install \
  gcc gcc-c++ make cmake ninja-build git \
  python3 python3-pip python3-devel sqlite \
  curl wget tar unzip rsync \
  openssh-clients openssh-server \
  pciutils hwloc numactl kernel-tools \
  pkgconf-pkg-config mokutil
```

- [x] Install additional compatibility packages only when a documented need arises.
- [x] Record Fedora, kernel, GCC, glibc, CMake, Ninja, Git, Python, SQLite, and SSH versions.

### NVIDIA driver

- [x] Follow the current RPM Fusion NVIDIA instructions for Fedora 45.
- [x] Install the current driver stack, normally `akmod-nvidia`, `xorg-x11-drv-nvidia-cuda`, `akmods`, and `kernel-devel`.
- [x] Check Secure Boot with `mokutil --sb-state` and complete MOK enrollment if required.
- [x] Record the exact driver version and avoid unrecorded kernel/driver updates.

### Remote workflow

- [x] Enable and start the Linux SSH server.
- [x] Configure and test key-based authentication from macOS without storing credentials in the repository.
- [x] Verify GitHub access from Fedora.
- [x] Clone the repository and confirm both systems can select the same Git commit.
- [x] Confirm that `git rev-parse HEAD` and `git status` are captured before authoritative runs.

## Phase 3 — CUDA Toolkit and Nsight Compute

### Toolkit installation

- [x] Install the latest compatible `cuda-toolkit` package set and Nsight Compute; Nsight Systems is optional.launch scripts.
- [x] Verify `nvcc`, `ncu`, GCC, and G++ versions and locations.
- [x] If necessary, install a supported compatibility compiler and set `NVCC_CCBIN` consistently for both models.

### Native CUDA smoke test

- [ ] Add a trivial non-benchmark CUDA smoke program.
- [ ] Target only `sm_89`.
- [ ] Verify device detection, allocation, a trivial launch, synchronization, error checking, and cleanup.
- [ ] Build and run it directly before using JUBE.
- [ ] Optionally build an NVIDIA `deviceQuery`-style sample as an independent check.

### Nsight Compute gate

- [ ] Profile the trivial CUDA program with `ncu`.
- [ ] Confirm hardware-counter access.
- [ ] Collect representative DRAM read/write metrics.
- [ ] Save and reopen or export a small report.
- [ ] Resolve counter-permission failures using NVIDIA's documented method; root profiling is not required.
- [ ] Keep profiling separate from timing runs.

**STOP GATE:** Native CUDA execution and Nsight Compute metric collection must both work.

## Phase 4 — Kokkos Serial and CUDA validation

- [ ] Use the selected Kokkos archive and checksum from Phase 1; currently investigated candidate: 5.2.2.
- [ ] Use C++20 and separate `macos-serial`, `fedora-serial`, and `fedora-cuda` builds.
- [ ] Enable the Serial host backend explicitly.
- [ ] Enable `Kokkos_ENABLE_CUDA=ON`, `Kokkos_ARCH_ADA89=ON`, CUDA architecture 89, and Release mode for Fedora CUDA.
- [ ] Select and document the supported Kokkos CUDA compilation method; do not change it midway through comparisons.
- [ ] Add a trivial Kokkos smoke program and print `Kokkos::print_configuration()`.
- [ ] Verify the reported backends and architecture.
- [ ] Validate a small parallel operation against a host reference.
- [ ] Run initialization/finalization repeatedly to check stability.
- [ ] Confirm identical Kokkos source release and checksum on macOS and Fedora.

**STOP GATE:** Kokkos CUDA must build, run, validate, and report the intended architecture.

## Phase 5 — JUBE and shared benchmark-harness validation

### Installation

- [ ] Select the latest JUBE release; currently investigated candidate: 2.7.1.
- [ ] Install an official pinned source archive in an isolated Python environment.
- [ ] Install PyYAML and `ruamel.yaml`; verify SQLite if database output is used.
- [ ] Record the source URL, checksum, and Python lock file.
- [ ] Verify `jube --version` and command-line help.

### Functional tests

- [ ] Run hello-world.
- [ ] Run a parameter-space example.
- [ ] Run a dependent compile-then-execute example.
- [ ] Verify YAML schema validation.
- [ ] Produce readable and CSV results through analysis.
- [ ] Run a deliberate failure and verify that JUBE reports an error rather than valid-looking output.
- [ ] Repeat non-GPU smoke tests on macOS and authoritative tests on Fedora.

### End-to-end dummy benchmark

- [ ] Drive the existing CUDA and Kokkos smoke executables through one JUBE YAML configuration.
- [ ] Include configure/build, execution, parsing, analysis, and CSV generation.
- [ ] Emit stable machine-readable output with schema version, implementation, variant, size, validation, and source revision.
- [ ] Verify every parsed field, type, and unit.
- [ ] Verify that missing fields or nonzero exits fail the result gate.
- [ ] Verify that compact raw timing output can be retained without retaining build artifacts.

**STOP GATE:** The dummy end-to-end JUBE workflow must complete successfully before benchmark-kernel implementation.

## Phase 6 — Freeze protocol and authorize STREAM

- [ ] Finalize [BENCHMARK_PROTOCOL.md](BENCHMARK_PROTOCOL.md).
- [ ] Use Release builds, identical compiler families, C++20, and `sm_89`.
- [ ] Disable fast-math in baselines.
- [ ] Exclude allocation, initialization, transfers, validation, and reporting from timed regions.
- [ ] Use explicit CUDA synchronization/events and Kokkos fences.
- [ ] Calibrate batching and freeze warm-up/measured counts for each configuration.
- [ ] Interleave implementations, using ABBA ordering where practical.
- [ ] Preserve raw batch timings and document derived per-launch values.
- [ ] Require numerical validation before accepting timings.
- [ ] Fix and test the output CSV/JSON schema through JUBE.
- [ ] Fill `N = ___` variants and `P = ___` profiling runs before each kernel's Level 2 work.
- [ ] Establish AC-power, idle-GPU, no-suspend, environment-recording, and clean-source requirements.

### Pre-STREAM readiness gate

- [ ] Native CUDA smoke passes.
- [ ] Nsight Compute collects memory-traffic metrics.
- [ ] Kokkos CUDA smoke passes on Ada 89.
- [ ] Kokkos Serial smoke passes on macOS.
- [ ] JUBE completes the dummy end-to-end workflow.
- [ ] YAML validation and deliberate-failure tests pass.
- [ ] Versions and compatibility workarounds are recorded and frozen.
- [ ] Benchmark protocol and output schema are validated.
- [ ] Key-based SSH and Git synchronization work.
- [ ] No unresolved environment errors remain.

STREAM implementation begins when every readiness-gate item passes.

## Phase 7 — STREAM Triad

Use the [STREAM experiment card](kernels/stream.md).

### Baseline

- [ ] Freeze operation, FP64 precision, alpha, initialization, sizes, and validation tolerance.
- [ ] Implement equivalent one-thread-per-element baselines with identical inputs.
- [ ] Keep allocation, initialization, transfers, and validation outside timed regions.
- [ ] Validate small, odd-sized, and performance-sized inputs against a host reference.
- [ ] Check all CUDA errors and Kokkos finalization paths.

### Measurements and tuning

- [ ] Run the frozen baseline protocol and preserve every raw timing.
- [ ] Produce runtime, ratio, effective-bandwidth, and `E_Kokkos` tables and plots.
- [ ] Save source and environment metadata.

- [ ] Freeze baseline source/results and the equal variant/profiling budget before tuning.
- [ ] Give every variant an ID, hypothesis, change, correctness evidence, and decision.
- [ ] Revalidate every variant and keep profiling separate from timing.
- [ ] Record accepted and rejected variants and stop at the declared budget.
- [ ] Measure final tuned implementations under the same protocol.

### Completion gate

- [ ] Curate raw timings, summaries, plots, selected profiles, and environment manifests.
- [ ] Link instructions and evidence from README and the experiment card.
- [ ] Answer the research question for STREAM at both levels.
- [ ] Verify a fresh build and reduced end-to-end JUBE run.

Phase 8 begins after the STREAM completion gate.

## Phase 8 — Seven-point stencil

Use the [stencil experiment card](kernels/stencil.md) and repeat the complete baseline/measurement/tuning/analysis lifecycle.

- [ ] Use out-of-place FP64 computation, fixed boundaries, and interior-only updates.
- [ ] Start with `256^3` and `512^3`, adjusting only for documented hardware limits.
- [ ] Use identical contiguous x-dimension layout and flattened baseline mapping.
- [ ] Validate interiors and boundaries on small non-cubic grids.
- [ ] Calculate MLUP/s from actual interior updates.
- [ ] Document every MDRange, layout, team, hierarchical, or scratch-memory variant.
- [ ] Separate profiler traffic from algorithmic estimates.
- [ ] Complete the stencil documentation and completion gate.

## Phase 9 — CSR SpMV

Use the [SpMV experiment card](kernels/spmv.md) and repeat the complete lifecycle.

- [ ] Select and document matrix sources and record licenses, URLs, hashes, and conversions.
- [ ] Use FP64 values, 32-bit indices, and frozen matrix/vector inputs.
- [ ] Preserve row ordering, column ordering, empty rows, and stored zeros.
- [ ] Use one thread per row and a serial inner loop for the baseline.
- [ ] Keep preprocessing outside timed regions.
- [ ] Validate empty, single-entry, imbalanced, and general rows against a host reference.
- [ ] Calculate GFLOP/s using `2 * nnz` and retain per-matrix results.
- [ ] Document warp-per-row, team-per-row, hierarchical, and balancing variants under the equal budget.
- [ ] Complete the SpMV analysis and completion gate.

## Phase 10 — Instructor reproduction and closure

- [ ] Start from a fresh clone using only README and linked instructor-facing documentation.
- [ ] Reinstall Python dependencies from lock files.
- [ ] Rebuild pinned Kokkos and run all smoke/correctness tests.
- [ ] Run a reduced JUBE benchmark and regenerate a result table.
- [ ] Check curated raw data against summaries.
- [ ] Confirm there are no absolute paths or credentials and that all compatibility overrides are documented.
- [ ] Include the Fedora 45 support exception in the final limitations.
- [ ] Produce final baseline/tuned comparisons for all three kernels.
- [ ] State limitations: one GPU, one toolchain, selected datasets, and frozen environment.
- [ ] Answer where results do or do not support a consistent “Kokkos tax.”
