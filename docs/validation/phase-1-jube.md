# Phase 1 JUBE validation evidence

**Date:** 2026-11-07  
**Scope:** Python dependency verification, JUBE hello-world, complete result generation, and YAML validity checks.

## Environment and dependency lock

- Python: 3.15.2
- JUBE: 2.7.1
- PyYAML: 6.0.3
- `ruamel.yaml`: 0.19.1
- NumPy: 2.5.4
- pandas: 3.1.1
- matplotlib: 3.11.2
- Lock file: `requirements/macos-lock.txt`

The lock file contains 17 entries and exactly matches `pip freeze` from the clean project environment. It contains no local `file://` URLs or user-specific paths. `pip check` reports no broken requirements, and all required imports pass.

## JUBE source verification

- Source: https://apps.fz-juelich.de/jsc/jube/download.php?version=2.7.1
- Verified SHA-256: `fe8b505a8bf224d785df665af134a1e69063d34d1a7214700d8c7325fef9ecfc`

The versioned HTTPS archive has the same checksum as the initially installed JUBE package. Reinstalling that identical package from the versioned URL updated the lock-file provenance without changing dependency versions.

## Hello-world

From the official `examples/hello_world` directory:

```bash
jube run hello_world.yaml
```

Result: the `say_hello` workpackage completed with one done and zero errors.

The hello-world example has no result-table definition, so the official `result_creation` example was also used to validate the complete cycle.

## Run, analyse, and result

From the official `examples/result_creation` directory:

```bash
jube run result_creation.yaml
jube result bench_run -a
```

All three workpackages completed successfully. Analysis and result generation produced:

```text
| number | number_pat | Number | Zahl |
|--------|------------|--------|------|
|      1 |          1 |      1 |    1 |
|      2 |          2 |      2 |    2 |
|      4 |          4 |      4 |    4 |
```

## YAML validity and duplicate-key detection

Both valid YAML examples parsed and ran successfully. A separate temporary YAML file containing two `do` keys in the same step was then passed to JUBE in debug mode.

Result: JUBE exited with status 1 and reported `found duplicate key "do"`, confirming that `ruamel.yaml` performs its duplicate-key validity check. This test targets JUBE 2.7.1's documented `ruamel.yaml` behavior; it does not claim that every unknown YAML key is rejected.

No benchmark-kernel code or performance measurements were involved.
