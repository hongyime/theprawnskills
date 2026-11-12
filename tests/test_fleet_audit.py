"""Regression tests for the portable fleet-audit script."""
from __future__ import annotations

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import audit_fleet_skills as audit


class FleetAuditTests(unittest.TestCase):
    def test_local_discovery_uses_temporary_home(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            skill = home / ".agents" / "skills" / "alpha"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: alpha\n---\n", encoding="utf-8")
            with mock.patch.object(audit.Path, "home", return_value=home):
                result = audit.audit_local_host(ROOT, ["alpha"])

        self.assertEqual(result.status, "ONLINE")
        self.assertEqual(result.roots[0].profile_present, 1)

    def test_computername_takes_precedence_over_hostname(self) -> None:
        with mock.patch.dict(audit.os.environ, {"COMPUTERNAME": "PRAWN-T14", "HOSTNAME": "fallback"}, clear=True), \
             mock.patch.object(audit.Path, "home", return_value=ROOT):
            result = audit.audit_local_host(ROOT, [])

        self.assertEqual(result.display_name, "PRAWN-T14 (local)")

    def test_macos_remote_path_is_sanitized(self) -> None:
        remote_output = json.dumps([{
            "path": "/Users/alice/.agents/skills",
            "label": "Shared",
            "exists": True,
            "count": 1,
            "present": 1,
            "missing": [],
            "broken": [],
        }])
        completed = subprocess.CompletedProcess(["ssh"], 0, remote_output, "")
        with mock.patch.object(audit.subprocess, "run", return_value=completed):
            result = audit.audit_remote_host("example", "example", "darwin", ["alpha"])

        self.assertEqual(result.roots[0].path, "~/.agents/skills")

    def test_json_keeps_already_sanitized_root_path(self) -> None:
        results = [audit.HostAuditResult(
            host_id="localhost",
            display_name="** (local)",
            os_name="windows",
            status="ONLINE",
            roots=[audit.RootAuditResult(path=r"%USERPROFILE%\.agents\skills", label="Shared")],
        )]
        stdout = io.StringIO()
        with mock.patch.object(audit, "run_fleet_audit", return_value=results), \
             mock.patch.object(sys, "argv", ["audit_fleet_skills.py", "--json"]), \
             redirect_stdout(stdout):
            self.assertEqual(audit.main(), 0)

        self.assertEqual(json.loads(stdout.getvalue())[0]["roots"][0]["path"], r"%USERPROFILE%\.agents\skills")

    def test_bundled_audit_copy_is_byte_identical(self) -> None:
        bundled = ROOT / "skills" / "fleet-skill-audit" / "scripts" / "audit_fleet_skills.py"
        self.assertEqual((ROOT / "scripts" / "audit_fleet_skills.py").read_bytes(), bundled.read_bytes())


if __name__ == "__main__":
    unittest.main()
