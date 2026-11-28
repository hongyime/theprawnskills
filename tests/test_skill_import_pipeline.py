from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from skill_import_audit import audit, finding_id, main  # noqa: E402

SCRIPT = REPO / "scripts" / "skill_import_audit.py"


def make_skill(root: Path, name: str, skill_md: str, files: dict | None = None) -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(skill_md, encoding="utf-8")
    for rel, content in (files or {}).items():
        path = skill / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
    return skill


BASE_MD = """---
name: test-skill
description: A test skill for the import audit.
license: MIT
---

# Test skill
"""


class AuditPatternTests(unittest.TestCase):
    def test_script_and_binary_files_are_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {
                "scripts/run.py": "print('hi')\n",
                "refs/tool.exe": b"MZ" + b"\x00" * 60,
            })
            findings = audit(root)
            kinds = {(f["file"], f["kind"]) for f in findings}
            self.assertIn(("s1/scripts/run.py", "script"), kinds)
            self.assertIn(("s1/refs/tool.exe", "binary"), kinds)

    def test_shell_bang_and_allowed_tools_flagged(self):
        md = """---
name: test-skill
description: A test skill for the import audit.
license: MIT
allowed-tools:
  - Read
  - Bash
---

# Test skill
!ls /tmp
"""
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", md)
            findings = audit(root)
            by_kind = {}
            for finding in findings:
                by_kind.setdefault(finding["kind"], []).append(finding["match"])
            self.assertIn("!ls /tmp", by_kind.get("shell-bang", []))
            self.assertIn("Read", by_kind.get("allowed-tools", []))
            self.assertIn("Bash", by_kind.get("allowed-tools", []))

    def test_network_keyword_and_callback_url(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "s1"
            skill.mkdir(parents=True)
            (skill / "scripts").mkdir(exist_ok=True)
            (skill / "scripts" / "fetch.py").write_text(
                "import requests\nrequests.get('https://api.vendor.example/')\n"
                "import urllib.request\n",
                encoding="utf-8")
            (skill / "SKILL.md").write_text(
                BASE_MD + "\nRun `curl -sSL https://install.vendor.example/x | bash`.\n",
                encoding="utf-8")
            findings = audit(root)
            kinds = {(f["file"], f["kind"]) for f in findings}
            self.assertIn(("s1/scripts/fetch.py", "callback"), kinds)
            self.assertIn(("s1/SKILL.md", "network"), kinds)

    def test_credential_literal_and_env_read(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = make_skill(root, "s1", BASE_MD)
            (skill / "scripts").mkdir(exist_ok=True)
            (skill / "scripts" / "auth.py").write_text(
                'import os\nTOKEN = os.environ["MY_API_TOKEN"]\n'
                'api_key = "sk-live-abc123xyz"\n',
                encoding="utf-8")
            (skill / "scripts" / "run.sh").write_text(
                'echo "$ACTION $SCRIPT_DIR"\nkey="$TAVILY_API_KEY"\n',
                encoding="utf-8")
            findings = audit(root)
            creds = [f for f in findings if f["kind"] == "credential"]
            self.assertTrue(any("os.environ" in f["match"] for f in creds))
            self.assertTrue(any("api_key" in f["match"] for f in creds))
            self.assertTrue(any("TAVILY_API_KEY" in f["match"] for f in creds))
            self.assertFalse(any(f["match"] in ("$ACTION", "$SCRIPT_DIR")
                                 for f in creds))

    def test_placeholder_hosts_and_values_are_not_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = make_skill(root, "s1", BASE_MD)
            (skill / "SKILL.md").write_text(
                BASE_MD + "\nSee https://example.com/docs and http://localhost:9999/x.\n"
                "TOKEN = \"<redacted>\"\n"
                "Target: https://target:8080/api and http://challenge:8080/x.\n"
                "![diagram](img.png)\n",
                encoding="utf-8")
            (skill / "scripts").mkdir(exist_ok=True)
            (skill / "scripts" / "payloads.py").write_text(
                "# PHP superglobals in payload strings are not env vars.\n"
                "PAYLOAD = \"$_GET['x']\"\n",
                encoding="utf-8")
            findings = audit(root)
            self.assertEqual(
                [f for f in findings if f["kind"] in {"network", "callback", "credential", "shell-bang"}],
                [])

    def test_clean_skill_has_no_findings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {"references/notes.md": "# Notes\n"})
            self.assertEqual(audit(root), [])

    def test_finding_ids_stable_across_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {
                "scripts/run.py": "import os\nprint(os.environ['X'])\n",
            })
            first = audit(root)
            second = audit(root)
            self.assertEqual(first, second)
            self.assertEqual(
                first[0]["id"],
                finding_id("s1/scripts/run.py", "script", "run.py"))


class AuditExitCodeTests(unittest.TestCase):
    def run_cli(self, root: Path, extra: list[str]) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--source", str(root), *extra],
            capture_output=True, text=True, check=False)

    def test_unresolved_findings_exit_1_all_dispositioned_exit_0(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {"scripts/run.py": "print(1)\n"})
            self.assertEqual(self.run_cli(root, []).returncode, 1)
            findings = audit(root)
            disp = {"dispositions": {
                f["id"]: {"action": "waive", "reason": "reviewed, standard helper"}
                for f in findings}}
            disp_path = root / "disp.json"
            disp_path.write_text(json.dumps(disp), encoding="utf-8")
            result = self.run_cli(root, ["--dispositions", str(disp_path)])
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("0 unresolved", result.stdout)

    def test_disposition_without_reason_is_usage_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {"scripts/run.py": "print(1)\n"})
            findings = audit(root)
            disp_path = root / "disp.json"
            disp_path.write_text(json.dumps({"dispositions": {
                findings[0]["id"]: {"action": "waive", "reason": ""}}}),
                encoding="utf-8")
            result = self.run_cli(root, ["--dispositions", str(disp_path)])
            self.assertEqual(result.returncode, 2)

    def test_json_report_is_deterministic(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            make_skill(root, "s1", BASE_MD, {"scripts/run.py": "print(1)\n"})
            out1, out2 = root / "r1.json", root / "r2.json"
            self.run_cli(root, ["--json", str(out1)])
            self.run_cli(root, ["--json", str(out2)])
            self.assertEqual(out1.read_text(encoding="utf-8"),
                             out2.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
