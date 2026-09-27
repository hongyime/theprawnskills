"""Behavior tests for the contract teaching fixture and bounded supervisor."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SUPERVISOR = ROOT / "skills/bounded-agent-loop/scripts/run_loop.py"
spec = importlib.util.spec_from_file_location("prawn_loop", SUPERVISOR)
loop = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loop)


class ContractFixtureTests(unittest.TestCase):
    def test_example_runs_from_unrelated_directory_and_detects_provider_regressions(self):
        with tempfile.TemporaryDirectory(prefix="contract spaces ") as temp:
            example = Path(temp) / "example"
            shutil.copytree(ROOT / "skills/api-contracts/examples", example)
            command = [sys.executable, str(example / "test_contract.py")]
            def execute():
                return subprocess.run(command, cwd=temp, capture_output=True, text=True, timeout=90)
            self.assertEqual(execute().returncode, 0)
            provider = example / "provider.py"
            original = provider.read_text(encoding="utf-8")
            for before, after in [("'9007199254740993'", '9007199254740993'), ("'label':", "'renamed':")]:
                self.assertIn(before, original)
                provider.write_text(original.replace(before, after), encoding="utf-8")
                result = execute()
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)


class LoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bounded loop spaces ")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.root = self.base / "repo"
        self.root.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.root / "value.txt").write_text("bad", encoding="utf-8")
        (self.root / "check.py").write_text("from pathlib import Path\nimport sys\nsys.exit(0 if Path('value.txt').read_text() == 'good' else 1)\n", encoding="utf-8")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        self.plan = {"root": str(self.root), "worker": [sys.executable, "-c", "from pathlib import Path; Path('value.txt').write_text('good')"],
                     "verify": [sys.executable, "check.py"], "allowed_files": ["value.txt"],
                     "max_attempts": 3, "wall_seconds": 300, "command_seconds": 30}

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.PIPE, timeout=30)

    def execute(self):
        return loop.run(self.plan, self.base / "run")

    def worker(self, code):
        self.plan["worker"] = [sys.executable, "-c", code]

    def test_repair_keeps_tests_and_history_and_records_exits(self):
        before = (self.root / "check.py").read_bytes()
        head = self.git("rev-parse", "HEAD")
        state = self.execute()
        self.assertEqual(state["status"], "passed")
        self.assertEqual(state["attempts"], 1)
        self.assertEqual([item["exit"] for item in state["commands"]], [1, 0, 0])
        self.assertEqual((self.root / "check.py").read_bytes(), before)
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(json.loads((self.base / "run/checkpoint.json").read_text())["status"], "passed")

    def test_repeated_failure_without_changes_stops(self):
        self.worker("pass")
        state = self.execute()
        self.assertEqual((state["status"], state["attempts"]), ("no-progress", 1))

    def test_varying_timestamps_do_not_buy_more_attempts(self):
        self.plan["verify"] = [sys.executable, "-c", "import time; print(time.time()); raise SystemExit(1)"]
        self.worker("pass")
        state = self.execute()
        self.assertEqual((state["status"], state["attempts"]), ("no-progress", 1))

    def test_intent_to_add_is_detected(self):
        self.plan["allowed_files"].append("extra.txt")
        self.worker("from pathlib import Path; import subprocess; Path('extra.txt').write_text('new'); subprocess.check_call(['git','add','-N','extra.txt']); Path('value.txt').write_text('good')")
        self.assertEqual(self.execute()["status"], "stopped")

    @unittest.skipIf(os.name == "nt", "POSIX permission bits")
    def test_acceptance_mode_change_is_detected(self):
        self.worker("from pathlib import Path; Path('check.py').chmod(0o755); Path('value.txt').write_text('good')")
        state = self.execute()
        self.assertEqual(state["status"], "stopped")
        self.assertIn("check.py", state["changed_files"])

    def test_attempt_budget(self):
        self.worker("from pathlib import Path; p=Path('value.txt'); p.write_text(p.read_text()+'x')")
        state = self.execute()
        self.assertEqual((state["status"], state["attempts"]), ("attempts-exhausted", 3))

    def test_worker_failure(self):
        self.worker("raise SystemExit(7)")
        self.assertEqual(self.execute()["status"], "worker-failed")

    def test_missing_tool(self):
        self.plan["worker"] = [str(self.base / "missing-tool")]
        self.assertEqual(self.execute()["status"], "stopped")

    def test_deleted_acceptance_test_stops_before_verification(self):
        self.worker("from pathlib import Path; Path('check.py').unlink()")
        state = self.execute()
        self.assertEqual(state["status"], "stopped")
        self.assertIn("check.py", state["error"])

    def test_weakened_acceptance_and_unrelated_edits_stop(self):
        self.worker("from pathlib import Path; Path('check.py').write_text('pass'); Path('unrelated.txt').write_text('x')")
        state = self.execute()
        self.assertEqual(state["status"], "stopped")
        self.assertEqual(state["changed_files"], ["check.py", "unrelated.txt"])

    def test_staging_is_detected(self):
        self.worker("import subprocess; subprocess.check_call(['git','add','value.txt']); from pathlib import Path; Path('value.txt').write_text('good'); subprocess.check_call(['git','add','value.txt'])")
        state = self.execute()
        self.assertEqual(state["status"], "stopped")
        self.assertIn("index", state["error"])

    def test_dirty_start_rejected(self):
        (self.root / "value.txt").write_text("dirty")
        with self.assertRaisesRegex(ValueError, "clean"):
            self.execute()
        self.assertFalse((self.base / "run").exists())

    def test_gitlink_is_rejected_before_launch(self):
        head = self.git("rev-parse", "HEAD").strip().decode()
        self.git("update-index", "--add", "--cacheinfo", f"160000,{head},deps/library")
        with self.assertRaisesRegex(ValueError, "submodules"):
            self.execute()
        self.assertFalse((self.base / "run").exists())

    def test_interrupted_run_evidence_is_not_overwritten(self):
        directory = self.base / "run"
        directory.mkdir()
        (directory / "checkpoint.json").write_text('{"status":"running","attempts":2}')
        with self.assertRaises(FileExistsError):
            self.execute()
        self.assertEqual(json.loads((directory / "checkpoint.json").read_text())["attempts"], 2)

    def test_path_escape_rejected(self):
        self.plan["allowed_files"] = ["../outside.txt"]
        with self.assertRaises(ValueError):
            self.execute()

    def test_hanging_child_is_stopped_on_timeout(self):
        import signal
        started = self.base / "child-started.json"
        child = "import os,time,json; from pathlib import Path; Path(" + repr(str(started)) + ").write_text(json.dumps({'pid':os.getpid()})); time.sleep(90)"
        self.worker("import subprocess,sys,time; subprocess.Popen([sys.executable,'-c'," + repr(child) + "]); time.sleep(90)")
        self.plan["command_seconds"] = 10
        def alive(pid):
            if os.name == "nt":
                import ctypes
                from ctypes import wintypes
                kernel = ctypes.WinDLL("kernel32", use_last_error=True)
                kernel.OpenProcess.restype = wintypes.HANDLE
                kernel.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
                kernel.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
                kernel.CloseHandle.argtypes = [wintypes.HANDLE]
                handle = kernel.OpenProcess(0x00100000, False, pid)
                if not handle:
                    return False
                try:
                    return kernel.WaitForSingleObject(handle, 0) == 258
                finally:
                    kernel.CloseHandle(handle)
            result = subprocess.run(["ps", "-p", str(pid), "-o", "stat="], capture_output=True, text=True)
            return result.returncode == 0 and bool(result.stdout.strip()) and not result.stdout.strip().startswith("Z")
        try:
            state = self.execute()
            self.assertEqual((state["status"], state["attempts"]), ("timeout", 1))
            self.assertTrue(started.exists(), "worker child never reached the cleanup probe")
            self.assertFalse(alive(json.loads(started.read_text())["pid"]), "foreground descendant survived timeout")
        finally:
            if started.exists():
                pid = json.loads(started.read_text())["pid"]
                if alive(pid):
                    if os.name == "nt":
                        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, timeout=15)
                    else:
                        os.kill(pid, signal.SIGKILL)

    def test_wall_budget(self):
        self.plan["wall_seconds"] = 0.001
        self.assertEqual(self.execute()["status"], "timeout")

    def test_cleanup_failure_survives_final_scope_violation(self):
        def execute_command(argv, root, log, seconds, env):
            log.write_text("controlled cleanup failure probe")
            if argv == self.plan["verify"]:
                return 1
            (root / "check.py").write_text("pass")
            raise loop.CleanupError("owned children may survive")
        with mock.patch.object(loop, "command", side_effect=execute_command):
            state = self.execute()
        self.assertEqual(state["status"], "cleanup-failed")
        self.assertIn("children", state["error"])
        self.assertIn("check.py", state["scope_error"])

    @unittest.skipUnless(os.name == "nt", "Windows tree cleanup failure injection")
    def test_taskkill_timeout_is_explicit_and_leader_is_reaped(self):
        process = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(90)"])
        try:
            with mock.patch.object(loop.subprocess, "run", side_effect=subprocess.TimeoutExpired("taskkill", 45)):
                with self.assertRaises(loop.CleanupError):
                    loop.stop_process(process)
            self.assertIsNotNone(process.poll())
        finally:
            if process.poll() is None:
                process.kill()
                process.wait(timeout=15)

    @unittest.skipIf(os.name == "nt", "POSIX interrupt delivery; Windows timeout/tree termination tested separately")
    def test_cancel_writes_checkpoint(self):
        import signal
        import time
        self.worker("import time; time.sleep(30)")
        plan_path = self.base / "plan.json"
        plan_path.write_text(json.dumps(self.plan))
        run_dir = self.base / "run"
        process = subprocess.Popen([sys.executable, str(SUPERVISOR), "--plan", str(plan_path), "--run-dir", str(run_dir)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.addCleanup(lambda: process.kill() if process.poll() is None else None)
        deadline = time.monotonic() + 15
        while not (run_dir / "1-worker.log").exists() and time.monotonic() < deadline:
            time.sleep(0.05)
        self.assertTrue((run_dir / "1-worker.log").exists())
        process.send_signal(signal.SIGINT)
        process.communicate(timeout=20)
        state = json.loads((run_dir / "checkpoint.json").read_text())
        self.assertEqual((state["status"], state["attempts"]), ("cancelled", 1))


if __name__ == "__main__":
    unittest.main()
