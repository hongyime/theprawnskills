"""Exercise the legacy PowerShell profile installer in isolated directories."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PWSH = shutil.which("pwsh") or shutil.which("powershell")


@unittest.skipUnless(PWSH, "PowerShell is not available")
class InstallDefaultSkillProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="default-profile-installer-")
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.workspace = self.base / "workspace with apostrophe ' marker"
        self.workspace.mkdir()
        self.installed = self.base / "installed"
        (self.workspace / "scripts").mkdir()
        for name in ("Install-DefaultSkillProfile.ps1", "Get-MachineRegistryPath.ps1"):
            shutil.copy2(ROOT / "scripts" / name, self.workspace / "scripts" / name)
        skill = self.workspace / "skills" / "alpha"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: alpha\n---\n", encoding="utf-8")
        (self.workspace / "default-profile.toml").write_text('skills = ["alpha"]\n', encoding="utf-8")
        self._write_registry()

    def _write_registry(self) -> None:
        self.workspace.joinpath("machines.local.toml").write_text(
            "version = 1\n\n[[machines]]\nid = \"test\"\nenabled = true\nlocal = true\n"
            f"installed_roots = [\"{self.installed.as_posix()}\"]\n",
            encoding="utf-8",
        )

    def _run(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [PWSH, "-NoProfile", "-File", str(self.workspace / "scripts" / "Install-DefaultSkillProfile.ps1"), "-Workspace", str(self.workspace)],
            capture_output=True,
            text=True,
        )

    def test_toml_parser_accepts_workspace_paths_with_apostrophes(self) -> None:
        result = self._run()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue((self.installed / "alpha" / "SKILL.md").is_file())

    def test_toml_parser_stops_on_a_python_parse_failure(self) -> None:
        (self.workspace / "default-profile.toml").write_text("skills = [\n", encoding="utf-8")
        result = self._run()
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.installed.exists())

    @unittest.skipUnless(os.name == "nt", "Junctions are a Windows-specific reparse point")
    def test_linked_skill_destination_is_preserved(self) -> None:
        self.installed.mkdir()
        linked_target = self.base / "linked-target"
        linked_target.mkdir()
        marker = linked_target / "preserve.txt"
        marker.write_text("keep", encoding="utf-8")
        junction = self.installed / "alpha"
        created = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), str(linked_target)], capture_output=True, text=True)
        self.assertEqual(created.returncode, 0, created.stdout + created.stderr)

        result = self._run()

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SKIPPED-LINK", result.stdout)
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")
        self.assertFalse((linked_target / "SKILL.md").exists())

    def test_local_and_ssh_workers_guard_reparse_points(self) -> None:
        script = (ROOT / "scripts" / "Install-DefaultSkillProfile.ps1").read_text(encoding="utf-8")
        self.assertEqual(script.count("function Test-ReparsePoint"), 2)
        self.assertEqual(script.count("SKIPPED-LINK"), 4)
        self.assertIn("sys.argv[1]", script)
        self.assertIn("$LASTEXITCODE -ne 0", script)


if __name__ == "__main__":
    unittest.main()
