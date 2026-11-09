import subprocess
import unittest
import tempfile
from pathlib import Path

from scripts.remote_fedora import (
    load_config,
    CommandError,
    RemoteClient,
    build,
    fetch,
    sync,
    validate_remote_repo,
    validate_result_path,
)


REPO = "/home/test/project"


class FakeRunner:
    def __init__(self, local_status="", remote_status="", commit="abc123"):
        self.local_status = local_status
        self.remote_status = remote_status
        self.commit = commit
        self.calls = []

    def __call__(self, arguments, **kwargs):
        self.calls.append((arguments, kwargs))
        joined = " ".join(arguments)
        if "--porcelain" in joined:
            status = self.remote_status if arguments[0] == "ssh" else self.local_status
            stdout = status + ("\n" if status else "")
        elif "rev-parse HEAD" in joined:
            stdout = self.commit + "\n"
        elif "symbolic-ref" in joined:
            stdout = "main\n"
        elif "--is-inside-work-tree" in joined:
            stdout = "true\n"
        else:
            stdout = ""
        return subprocess.CompletedProcess(arguments, 0, stdout=stdout, stderr="")


class RemoteClientTests(unittest.TestCase):
    def client(self, runner=None, dry_run=False):
        return RemoteClient("fedora", REPO, dry_run=dry_run, runner=runner or FakeRunner())

    def test_remote_command_uses_ssh_safety_options(self):
        runner = FakeRunner()
        self.client(runner).remote(["git", "-C", REPO, "status"])
        arguments, kwargs = runner.calls[0]
        self.assertEqual(arguments[0], "ssh")
        self.assertIn("BatchMode=yes", arguments)
        self.assertIn("StrictHostKeyChecking=yes", arguments)
        self.assertIn("fedora", arguments)
        self.assertNotIn("shell", kwargs)
        self.assertTrue(kwargs["check"])

    def test_remote_repository_must_be_absolute(self):
        for invalid in ("relative/path", "../outside", "/", None):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    validate_remote_repo(invalid)

    def test_result_path_cannot_escape_result_roots(self):
        for invalid in ("../secrets", "/etc/passwd", "source/file.cpp", "results/../secrets"):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    validate_result_path(invalid)

    def test_dry_run_does_not_execute_runner(self):
        runner = FakeRunner()
        self.client(runner, dry_run=True).remote(["true"])
        self.assertEqual(runner.calls, [])

    def test_sync_uses_fast_forward_only(self):
        runner = FakeRunner()
        sync(self.client(runner))
        commands = [" ".join(arguments) for arguments, _ in runner.calls]
        self.assertTrue(any("fetch origin main" in command for command in commands))
        self.assertTrue(any("merge --ff-only origin/main" in command for command in commands))
        self.assertFalse(any("reset" in command or "clean" in command for command in commands))

    def test_sync_rejects_dirty_remote_checkout(self):
        runner = FakeRunner(remote_status=" M README.md")
        with self.assertRaises(CommandError):
            sync(self.client(runner))

    def test_build_rejects_dirty_local_checkout(self):
        runner = FakeRunner(local_status=" M README.md")
        with self.assertRaises(CommandError):
            build(self.client(runner), "fedora-cuda")

    def test_build_rejects_mismatched_commits(self):
        class DifferentRemoteCommits(FakeRunner):
            def __call__(self, arguments, **kwargs):
                result = super().__call__(arguments, **kwargs)
                if "rev-parse HEAD" in " ".join(arguments) and arguments[0] == "ssh":
                    result.stdout = "different\n"
                return result

        with self.assertRaises(CommandError):
            build(self.client(DifferentRemoteCommits()), "fedora-cuda")

    def test_build_uses_selected_preset(self):
        runner = FakeRunner()
        build(self.client(runner), "fedora-cuda")
        scripts = [kwargs["input"] for arguments, kwargs in runner.calls if kwargs.get("input")]
        self.assertTrue(any("cmake --preset fedora-cuda" in script for script in scripts))

    def test_timeout_is_reported_as_command_error(self):
        class TimeoutRunner(FakeRunner):
            def __call__(self, arguments, **kwargs):
                raise subprocess.TimeoutExpired(arguments, 1)

        with self.assertRaises(CommandError):
            self.client(TimeoutRunner()).remote(["true"])

    def test_nonzero_exit_is_reported_as_command_error(self):
        class FailureRunner(FakeRunner):
            def __call__(self, arguments, **kwargs):
                raise subprocess.CalledProcessError(7, arguments, output="", stderr="failed")

        with self.assertRaises(CommandError):
            self.client(FailureRunner()).remote(["true"])

    def test_fetch_rejects_nonempty_destination(self):
        destination = Path("run/test-existing-fetch-destination")
        destination.mkdir(parents=True, exist_ok=True)
        (destination / "existing.txt").write_text("keep", encoding="utf-8")
        try:
            with self.assertRaises(CommandError):
                fetch(self.client(), "results/example", destination)
        finally:
            (destination / "existing.txt").unlink()
            destination.rmdir()

class ConfigurationTests(unittest.TestCase):
    def test_load_valid_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote.local.json"
            path.write_text(
                '{"host": "fedora", "remote_repo": "/home/test/project", "timeout": 123}',
                encoding="utf-8",
            )
            config = load_config(path)
            self.assertEqual(config["host"], "fedora")
            self.assertEqual(config["remote_repo"], "/home/test/project")
            self.assertEqual(config["timeout"], 123)

    def test_unknown_config_key_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote.local.json"
            path.write_text('{"host": "fedora", "typo": true}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)

    def test_relative_remote_repo_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "remote.local.json"
            path.write_text('{"remote_repo": "relative/path"}', encoding="utf-8")
            with self.assertRaises(ValueError):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
