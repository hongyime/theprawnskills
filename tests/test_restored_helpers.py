"""Exercise restored command wrappers using fake taze commands, never the network."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe") if os.name == "nt" else shutil.which("bash")


class RestoredHelpersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="restored-helpers-")
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)

    @unittest.skipUnless(BASH and Path(BASH).exists(), "Bash not available")
    def test_dependency_wrappers_forward_arguments_without_installing(self):
        launcher = self.cwd / "run.sh"
        launcher.write_text('''#!/usr/bin/env bash
taze() { printf 'arg:<%s>\\n' "$@"; }
export -f taze
bash "$1" -r '--include=one two'
''', encoding="utf-8", newline="\n")
        script = ROOT / "skills/dependency-updater/scripts/run-taze.sh"
        (self.cwd / "package.json").write_text("{}", encoding="utf-8")
        result = subprocess.run([BASH, launcher.as_posix(), script.as_posix()], cwd=self.cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("arg:<--include=one two>", result.stdout)
        (self.cwd / "package.json").unlink()
        result = subprocess.run([BASH, launcher.as_posix(), script.as_posix()], cwd=self.cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        check = ROOT / "skills/dependency-updater/scripts/check-tool.sh"
        result = subprocess.run([BASH, check.as_posix(), "prawn-nonexistent-test-tool", "do-not-run-me"], cwd=self.cwd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Install with: do-not-run-me", result.stdout)


if __name__ == "__main__":
    unittest.main()
