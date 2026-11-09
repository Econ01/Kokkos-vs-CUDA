# Fedora remote development

`scripts/remote_fedora.py` provides a small set of fixed development operations over OpenSSH. It is intended for on-demand checks, Git synchronization, CMake builds/tests, and result retrieval. It does not provide arbitrary remote shell execution or run a background service.

## Prerequisites

- An SSH alias named `fedora` configured in the Mac's `~/.ssh/config`.
- Key-based SSH authentication already tested with `ssh fedora`.
- A Fedora checkout of this repository on `main`.
- The absolute path of that remote checkout, supplied with `--remote-repo` or `KVC_REMOTE_REPO`.
- Clean local and remote checkouts at the same Git commit for `sync`, `build`, and `test`.

Machine-specific addresses, usernames, private keys, and repository paths are not stored in this file or elsewhere in the tracked project.

## Configuration

The SSH alias defaults to `fedora`. A different alias can be supplied with `--host` or `KVC_SSH_HOST`.

Set the remote repository path for the current shell:

```bash
export KVC_REMOTE_REPO=/absolute/path/to/Kokkos-vs-CUDA
```

Alternatively, pass it explicitly before each operation:

```bash
python3 scripts/remote_fedora.py \
  --remote-repo /absolute/path/to/Kokkos-vs-CUDA \
  check
```

## Commands

### Check the environment

```bash
python3 scripts/remote_fedora.py check
```

`check` is read-only. It verifies SSH and the remote Git worktree, reports GPU/driver information, NVCC, CMake, Ninja, and JUBE versions, and compares local and remote revisions. Commit mismatches and dirty checkouts are reported as warnings so the state can be inspected before synchronization.

### Synchronize the remote checkout

Push the desired local commit to GitHub first, then run:

```bash
python3 scripts/remote_fedora.py sync
```

`sync` requires clean local and remote checkouts, requires the remote checkout to be on `main`, fetches `origin/main`, and merges with `--ff-only`. It then requires both commits to match. It does not push local commits, reset either checkout, delete files, or resolve diverged branches.

### Build and test

```bash
python3 scripts/remote_fedora.py build --preset fedora-cuda
python3 scripts/remote_fedora.py test --preset fedora-cuda
```

`build` and `test` require clean checkouts at the same commit. The remote scripts add `/usr/local/cuda/bin` to `PATH` and use `set -euo pipefail`, so failures stop the operation and produce a nonzero local exit status.

The default command timeout is 300 seconds. Longer builds can use, for example:

```bash
python3 scripts/remote_fedora.py --timeout 3600 build --preset fedora-cuda
```

### Fetch results

```bash
python3 scripts/remote_fedora.py fetch results/<run-id>
python3 scripts/remote_fedora.py fetch run/<run-id>
```

Result paths must be relative to the remote repository and begin with `results/` or `run/`. Parent-directory traversal and absolute result paths are rejected.

By default, each fetch creates a timestamped directory under `run/fetched/`. A custom empty destination can be supplied with `--destination`. Nonempty destinations are rejected to prevent accidental overwrites. Rsync uses archive and partial-transfer modes but never `--delete`.

### Dry-run an operation

Place `--dry-run` before the operation to print generated commands without executing them:

```bash
python3 scripts/remote_fedora.py --dry-run build --preset fedora-cuda
python3 scripts/remote_fedora.py --dry-run fetch results/example
```

## SSH behavior

Every SSH operation uses:

- `BatchMode=yes` to fail rather than wait for a password prompt.
- `StrictHostKeyChecking=yes` to preserve host verification.
- `ConnectTimeout=10` for faster network-failure detection.
- OpenSSH connection multiplexing for repeated operations.

The script uses Python's standard library and local argument lists without `shell=True`. Remote operations use fixed command templates and shell quoting. No password, key material, or arbitrary command string is accepted.

## Local tests

```bash
python3 -m unittest discover -s tests -p 'test_remote_fedora.py' -v
```

The tests cover SSH options, dry-run behavior, absolute-path requirements, result-path validation, fast-forward-only synchronization, dirty or mismatched checkouts, preset selection, fetch-destination protection, and command failures.
