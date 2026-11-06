# Environment and version policy

## Roles

- **macOS:** host-only development, Kokkos Serial correctness tests, and JUBE smoke tests. Its timings are never authoritative GPU measurements.
- **Fedora 45:** authoritative CUDA and Kokkos CUDA builds, Nsight Compute profiling, and JUBE performance runs.
- **Target GPU:** RTX 4080 Laptop GPU with 12 GB VRAM and compute capability 8.9 (`sm_89`).

## Latest, then freeze

During initial setup, select the latest mutually compatible releases. After all pre-STREAM smoke tests pass:

1. Record exact OS, kernel, driver, compiler, CUDA, Kokkos, JUBE, Python, and analysis-package versions.
2. Record source archive URLs and SHA-256 checksums.
3. Stop routine OS, kernel, driver, CUDA, Kokkos, JUBE, and Python dependency updates.
4. Treat every required update as an environment change: document it, rerun all smoke tests, and decide whether prior performance results must be repeated.

The word `latest` must not appear in a frozen manifest in place of an exact version.

## Environment manifest

Every authoritative result group must reference an environment manifest. Store manifests as UTF-8 JSON with the following shape. The example documents fields, not validated values.

```json
{
  "schema_version": 1,
  "captured_at_utc": "YYYY-MM-DDTHH:MM:SSZ",
  "platform": {
    "role": "fedora-cuda",
    "os": "Fedora Linux 45",
    "kernel": "exact kernel release",
    "glibc": "exact glibc version"
  },
  "source": {
    "commit": "full Git commit hash",
    "dirty": false
  },
  "hardware": {
    "gpu": "RTX 4080 Laptop GPU",
    "vram": "value reported by nvidia-smi",
    "compute_capability": "8.9"
  },
  "nvidia": {
    "driver": "exact driver version",
    "cuda_toolkit": "exact toolkit version",
    "nvcc": "exact NVCC version",
    "installation_method": "official repository, compatibility repository, or runfile",
    "repository_distribution": "fedora45, fedora44, or not applicable"
  },
  "toolchain": {
    "host_compiler": "compiler name and exact version",
    "cmake": "exact CMake version",
    "generator": "Ninja",
    "ninja": "exact Ninja version",
    "nvcc_ccbin": "selected host compiler or empty"
  },
  "kokkos": {
    "version": "exact release",
    "archive_url": "official release archive URL",
    "sha256": "archive checksum",
    "backends": ["Serial", "CUDA"],
    "cuda_architecture": "89"
  },
  "python": {
    "version": "exact Python version",
    "jube": "exact JUBE version",
    "lock_file": "relative path to the recorded dependency lock file"
  },
  "build": {
    "preset": "fedora-cuda",
    "build_type": "Release",
    "cxx_standard": 20,
    "fast_math": false
  },
  "compatibility": {
    "nvidia_qualified_os": false,
    "notes": ["Describe every unsupported compatibility choice"]
  },
  "benchmark_conditions": {
    "ac_power": true,
    "other_gpu_workloads": false,
    "power_mode": "recorded value",
    "notes": "Relevant clocks, temperature, or background-activity observations"
  }
}
```

### Manifest rules

- Use UTC ISO 8601 timestamps.
- Use relative repository paths for lock files and related evidence.
- Manifests exclude usernames, home-directory paths, IP addresses, SSH aliases, access tokens, and private keys.
- Authoritative measurements require `source.dirty` to be `false`; dirty-tree runs are development-only.
- Record the manifest's SHA-256 checksum alongside the associated result summary.
- Manifests are immutable after a run; source or environment changes produce a new manifest.

## Documentation to complete during setup

- [ ] macOS exact tool versions and smoke-test evidence.
- [ ] Fedora OS, kernel, driver, CUDA, compiler, and compatibility evidence.
- [ ] Kokkos version, checksum, backend configuration, and architecture evidence.
- [ ] JUBE source archive, checksum, Python lock file, and validation evidence.
- [ ] Frozen pre-STREAM manifests for macOS and Fedora.
