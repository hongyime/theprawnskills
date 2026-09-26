"""Exercise restored command wrappers using fake Azure/taze commands, never the network."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BASH = str(Path(os.environ.get("ProgramFiles", "C:/Program Files")) / "Git/bin/bash.exe") if os.name == "nt" else shutil.which("bash")
PWSH = shutil.which("pwsh")
VARIANTS = ("skills/preset", "skills/deploy-model/preset", "skills/microsoft-foundry/models/deploy-model/preset")


class RestoredHelpersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="restored-helpers-")
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)

    def test_preset_variants_have_identical_self_contained_helpers(self):
        for suffix in ("sh", "ps1"):
            contents = [(ROOT / variant / f"scripts/generate_deployment_name.{suffix}").read_bytes() for variant in VARIANTS]
            self.assertEqual(contents[0], contents[1])
            self.assertEqual(contents[1], contents[2])

    @unittest.skipUnless(BASH and Path(BASH).exists(), "Bash not available")
    def test_bash_preset_collisions_and_query_failure(self):
        launcher = self.cwd / "run.sh"
        launcher.write_text('''#!/usr/bin/env bash
az() {
  [[ "$*" == *"deployment list"* ]] || return 88
  [[ "$*" == *"create"* ]] && return 89
  [[ "${PRAWN_TEST_FAILURE:-0}" == 0 ]] || return 7
  printf '%s\\n' "$PRAWN_TEST_NAMES"
}
export -f az
bash "$1" account group "$2"
''', encoding="utf-8", newline="\n")
        script = ROOT / VARIANTS[0] / "scripts/generate_deployment_name.sh"
        env = {**os.environ, "PRAWN_TEST_NAMES": "GPT-4O\ngpt-4o-2\ngpt-4o-4"}
        result = subprocess.run([BASH, launcher.as_posix(), script.as_posix(), "gpt-4o"], cwd=self.cwd, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "gpt-4o-3")
        env["PRAWN_TEST_FAILURE"] = "1"
        result = subprocess.run([BASH, launcher.as_posix(), script.as_posix(), "gpt-4o"], cwd=self.cwd, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

    @unittest.skipUnless(PWSH, "PowerShell not available")
    def test_powershell_preset_collisions_and_query_failure(self):
        launcher = self.cwd / "run.ps1"
        launcher.write_text('''param([string]$Helper)
function global:az {
    if (($args -join ' ') -notmatch 'deployment list') { throw 'Unexpected command' }
    if ($env:PRAWN_TEST_FAILURE -eq '1') { $global:LASTEXITCODE = 7; return }
    $global:LASTEXITCODE = 0
    $env:PRAWN_TEST_NAMES -split ','
}
& $Helper -AccountName account -ResourceGroup group -ModelName gpt-4o
''', encoding="utf-8")
        helper = ROOT / VARIANTS[0] / "scripts/generate_deployment_name.ps1"
        env = {**os.environ, "PRAWN_TEST_NAMES": "GPT-4O,gpt-4o-2,gpt-4o-4"}
        args = [PWSH, "-NoProfile", "-File", str(launcher), str(helper)]
        result = subprocess.run(args, cwd=self.cwd, env=env, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "gpt-4o-3")
        env["PRAWN_TEST_FAILURE"] = "1"
        result = subprocess.run(args, cwd=self.cwd, env=env, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")

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
