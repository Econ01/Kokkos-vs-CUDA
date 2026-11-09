#!/usr/bin/env python3
"""Run a small, safety-focused set of Fedora development operations over SSH."""

import argparse
import json
import os
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "remote.local.json"
DEFAULT_TIMEOUT = 300
CONFIG_KEYS = {"host", "remote_repo", "timeout"}
DEFAULT_HOST = "fedora"
PRESETS = ("fedora-cuda", "fedora-serial")
SSH_OPTIONS = [
    "-o",
    "BatchMode=yes",
    "-o",
    "ConnectTimeout=10",
    "-o",
    "StrictHostKeyChecking=yes",
    "-o",
    "ControlMaster=auto",
    "-o",
    f"ControlPath={Path.home()}/.ssh/control-%C",
    "-o",
    "ControlPersist=10m",
]


class CommandError(RuntimeError):
    """A command failed, timed out, or failed a safety check."""


def validate_host(host):
    if not host or host.startswith("-") or any(c.isspace() for c in host):
        raise ValueError("SSH host must be a single alias or hostname without spaces")
    return host


def validate_remote_repo(path):
    if not path or any(c in path for c in ("\x00", "\n", "\r")):
        raise ValueError(
            "An absolute remote repository path is required "
            "(use --remote-repo, KVC_REMOTE_REPO, or remote.local.json)"
        )
    pure_path = PurePosixPath(path)
    if not pure_path.is_absolute() or str(pure_path) == "/" or ".." in pure_path.parts:
        raise ValueError("Remote repository must be an absolute path without '..'")
    return str(pure_path)


def validate_result_path(path):
    pure_path = PurePosixPath(path)
    if (
        pure_path.is_absolute()
        or not pure_path.parts
        or ".." in pure_path.parts
        or pure_path.parts[0] not in {"results", "run"}
    ):
        raise ValueError("Result paths must be relative and start with 'results/' or 'run/'")
    return str(pure_path)


def utc_timestamp():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def load_config(path):
    if not path.exists():
        return {}

    try:
        with path.open(encoding="utf-8") as handle:
            config = json.load(handle)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error

    if not isinstance(config, dict):
        raise ValueError(f"Configuration in {path} must be a JSON object")

    unknown_keys = set(config) - CONFIG_KEYS
    if unknown_keys:
        raise ValueError(f"Unknown configuration keys in {path}: {", ".join(sorted(unknown_keys))}")

    if "host" in config:
        if not isinstance(config["host"], str):
            raise ValueError(f"Configuration 'host' must be a string")
        validate_host(config["host"])
    if "remote_repo" in config:
        if not isinstance(config["remote_repo"], str):
            raise ValueError(f"Configuration 'remote_repo' must be a string")
        validate_remote_repo(config["remote_repo"])
    if "timeout" in config:
        timeout = config["timeout"]
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise ValueError("Configuration 'timeout' must be a number")
        if timeout <= 0:
            raise ValueError("Configuration 'timeout' must be positive")

    return config

class RemoteClient:
    def __init__(self, host, remote_repo, dry_run=False, timeout=300, runner=None):
        self.host = validate_host(host)
        self.remote_repo = validate_remote_repo(remote_repo)
        self.dry_run = dry_run
        self.timeout = timeout
        self.runner = runner or subprocess.run

    def execute(self, arguments, stdin=None):
        if self.dry_run:
            print(shlex.join(arguments))
            if stdin:
                print(stdin)
            return subprocess.CompletedProcess(arguments, 0, stdout="", stderr="")

        try:
            result = self.runner(
                arguments,
                check=True,
                text=True,
                capture_output=True,
                input=stdin,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired as error:
            raise CommandError(f"Command timed out: {shlex.join(arguments)}") from error
        except subprocess.CalledProcessError as error:
            if error.stdout:
                sys.stdout.write(error.stdout)
            if error.stderr:
                sys.stderr.write(error.stderr)
            raise CommandError(
                f"Command failed with exit status {error.returncode}: {shlex.join(arguments)}"
            ) from error

        if result.stdout:
            sys.stdout.write(result.stdout)
        if result.stderr:
            sys.stderr.write(result.stderr)
        return result

    def local(self, arguments):
        return self.execute(arguments)

    def remote(self, arguments):
        remote_command = shlex.join(arguments)
        return self.execute(["ssh", *SSH_OPTIONS, self.host, "--", remote_command])

    def remote_script(self, script):
        return self.execute(["ssh", *SSH_OPTIONS, self.host, "--", "bash", "-s"], stdin=script)

    def local_git(self, arguments):
        return self.local(["git", "-C", str(ROOT), *arguments]).stdout.strip()

    def remote_git(self, arguments):
        return self.remote(["git", "-C", self.remote_repo, *arguments]).stdout.strip()

    def local_status(self):
        return self.local_git(["status", "--porcelain"])

    def remote_status(self):
        return self.remote_git(["status", "--porcelain"])

    def local_commit(self):
        return self.local_git(["rev-parse", "HEAD"])

    def remote_commit(self):
        return self.remote_git(["rev-parse", "HEAD"])

    def require_clean_checkouts(self):
        local_status = self.local_status()
        remote_status = self.remote_status()
        if local_status:
            raise CommandError("Local checkout is dirty; commit or stash changes before continuing")
        if remote_status:
            raise CommandError("Remote checkout is dirty; commit or stash changes before continuing")

    def require_matching_commits(self):
        local_commit = self.local_commit()
        remote_commit = self.remote_commit()
        if local_commit != remote_commit:
            raise CommandError(
                f"Local and remote commits differ: local {local_commit}, remote {remote_commit}"
            )
        return local_commit

    def require_ready(self):
        self.require_clean_checkouts()
        return self.require_matching_commits()


def check(client):
    client.remote(["true"])
    client.remote_git(["rev-parse", "--is-inside-work-tree"])
    client.remote_script(
        "set -euo pipefail\n"
        f"cd {shlex.quote(client.remote_repo)}\n"
        "export PATH=/usr/local/cuda/bin:$PATH\n"
        "nvidia-smi --query-gpu=name,driver_version,memory.total --format=csv,noheader\n"
        "nvcc --version\n"
        "cmake --version\n"
        "ninja --version\n"
        "if [ -x .venv/bin/jube ]; then\n"
        "  .venv/bin/jube --version\n"
        "else\n"
        "  jube --version\n"
        "fi\n"
    )
    local_commit = client.local_commit()
    remote_commit = client.remote_commit()
    local_status = client.local_status() or "clean"
    remote_status = client.remote_status() or "clean"
    print(f"Local commit:  {local_commit} ({local_status})")
    print(f"Remote commit: {remote_commit} ({remote_status})")
    if local_commit != remote_commit:
        print("Warning: local and remote commits differ; run sync before building.")
    if local_status != "clean" or remote_status != "clean":
        print("Warning: build and test require clean, matching checkouts.")


def sync(client):
    client.require_clean_checkouts()
    branch = client.remote_git(["symbolic-ref", "--short", "HEAD"])
    if branch != "main":
        raise CommandError(f"Remote checkout must be on main, not {branch}")
    client.remote_git(["fetch", "origin", "main"])
    client.remote_git(["merge", "--ff-only", "origin/main"])
    commit = client.require_ready()
    print(f"Local and remote checkouts are synchronized at {commit}")


def build(client, preset):
    commit = client.require_ready()
    print(f"Building on Fedora at {commit}")
    client.remote_script(
        "set -euo pipefail\n"
        f"cd {shlex.quote(client.remote_repo)}\n"
        "export PATH=/usr/local/cuda/bin:$PATH\n"
        f"cmake --preset {shlex.quote(preset)}\n"
        f"cmake --build --preset {shlex.quote(preset)}\n"
    )


def test(client, preset):
    commit = client.require_ready()
    print(f"Testing on Fedora at {commit}")
    client.remote_script(
        "set -euo pipefail\n"
        f"cd {shlex.quote(client.remote_repo)}\n"
        "export PATH=/usr/local/cuda/bin:$PATH\n"
        f"ctest --preset {shlex.quote(preset)} --output-on-failure\n"
    )


def fetch(client, result_path, destination=None):
    relative_path = validate_result_path(result_path)
    remote_source = f"{client.remote_repo}/{relative_path}"
    destination = destination or ROOT / "run" / "fetched" / utc_timestamp()
    destination = Path(destination)

    if destination.exists() and not destination.is_dir():
        raise CommandError(f"Fetch destination is not a directory: {destination}")
    if destination.exists() and any(destination.iterdir()):
        raise CommandError(f"Fetch destination is not empty: {destination}")
    if not client.dry_run:
        destination.mkdir(parents=True, exist_ok=False)

    rsync_ssh = "ssh " + " ".join(SSH_OPTIONS)
    client.local(
        [
            "rsync",
            "-a",
            "--partial",
            "-e",
            rsync_ssh,
            f"{client.host}:{shlex.quote(remote_source)}",
            f"{destination}/",
        ]
    )
    print(f"Fetched results into {destination}")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--host",
        help="SSH alias (default: fedora or KVC_SSH_HOST)",
    )
    parser.add_argument(
        "--remote-repo",
        help="absolute remote repository path (or KVC_REMOTE_REPO)",
    )
    parser.add_argument("--dry-run", action="store_true", help="print commands without executing them")
    parser.add_argument("--timeout", type=float, help="command timeout in seconds")

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        help="local JSON configuration path (default: remote.local.json)",
    )

    subparsers = parser.add_subparsers(dest="operation", required=True)
    subparsers.add_parser("check", help="check SSH, tools, and repository state")
    subparsers.add_parser("sync", help="fast-forward the remote checkout and verify commits")
    for operation in ("build", "test"):
        subparser = subparsers.add_parser(operation, help=f"run remote CMake {operation}")
        subparser.add_argument("--preset", choices=PRESETS, required=True)

    fetch_parser = subparsers.add_parser("fetch", help="fetch results with rsync")
    fetch_parser.add_argument("path", help="remote path relative to results/ or run/")
    fetch_parser.add_argument("--destination", type=Path, help="empty local destination directory")
    return parser.parse_args()


def main():
    args = parse_args()
    try:
        config = load_config(args.config)

        host = (
            args.host
            or os.environ.get("KVC_SSH_HOST")
            or config.get("host", DEFAULT_HOST)
        )

        remote_repo = (
            args.remote_repo
            or os.environ.get("KVC_REMOTE_REPO")
            or config.get("remote_repo")
        )

        timeout = (
            args.timeout
            if args.timeout is not None
            else config.get("timeout", DEFAULT_TIMEOUT)
        )

        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        client = RemoteClient(host, remote_repo, args.dry_run, timeout)
        if args.operation == "check":
            check(client)
        elif args.operation == "sync":
            sync(client)
        elif args.operation == "build":
            build(client, args.preset)
        elif args.operation == "test":
            test(client, args.preset)
        elif args.operation == "fetch":
            fetch(client, args.path, args.destination)
        return 0
    except (CommandError, ValueError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
