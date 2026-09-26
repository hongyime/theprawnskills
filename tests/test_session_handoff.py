"""Exercise real handoff commands in disposable Git projects, including failure cases."""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills/session-handoff/scripts"
spec = importlib.util.spec_from_file_location("handoff_helpers", SCRIPTS / "_handoff.py")
handoff = importlib.util.module_from_spec(spec)
spec.loader.exec_module(handoff)


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="handoff-test-")
        self.addCleanup(self.temp.cleanup)
        self.project = Path(self.temp.name) / "project with spaces"
        self.project.mkdir()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "core.hooksPath", str(self.project / ".git/test-hooks"))
        (self.project / "README.md").write_text("Initial project\n", encoding="utf-8")
        self.git("add", "README.md")
        self.git("commit", "-m", "Initial fixture")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.project), *args], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def cli(self, script, *args, expected=0):
        result = subprocess.run([sys.executable, str(SCRIPTS / script), *args,
                                 "--project", str(self.project), "--json"],
                                cwd=self.temp.name, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return json.loads(result.stdout or result.stderr)

    def draft(self, slug="fixture"):
        return self.cli("create_handoff.py", slug)["file"]

    def complete(self, relative):
        path = self.project / relative
        text = path.read_text(encoding="utf-8")
        text = re.sub(r"\[TODO:.*?\]", "Verified fixture context and next action.", text, flags=re.S)
        text = text.replace("## Critical Files\n\nVerified fixture context and next action.",
                            "## Critical Files\n\n`README.md` contains the project entry point.")
        path.write_text(text, encoding="utf-8")
        return path

    def test_create_from_other_cwd_draft_validation_and_complete_round_trip(self):
        before = self.git("rev-parse", "HEAD")
        relative = self.draft()
        text = (self.project / relative).read_text(encoding="utf-8")
        self.assertNotIn(str(self.project), text)
        draft = self.cli("validate_handoff.py", relative, expected=1)
        self.assertFalse(draft["passed"])
        self.complete(relative)
        result = self.cli("validate_handoff.py", relative)
        self.assertEqual(result["score"], 100)
        self.assertEqual(self.cli("list_handoffs.py")[0]["status"], "COMPLETE")
        self.assertEqual(self.cli("check_staleness.py", relative)["level"], "FRESH")
        self.assertEqual(self.git("rev-parse", "HEAD"), before)
        self.assertEqual(self.git("diff", "--cached", "--name-only"), "")

    def test_collision_preserves_existing_handoff_and_chain(self):
        first = self.draft()
        original = (self.project / first).read_bytes()
        second = self.cli("create_handoff.py", "fixture", "--continues-from", Path(first).name)["file"]
        self.assertNotEqual(first, second)
        self.assertEqual((self.project / first).read_bytes(), original)
        self.assertEqual(handoff.read_handoff(self.project / second)[1]["continues_from"], first)

    def test_path_traversal_and_nonexistent_chain_rejected_without_writes(self):
        self.cli("create_handoff.py", "../../escape", expected=2)
        self.cli("create_handoff.py", "safe", "--continues-from", "missing.md", expected=2)
        self.assertFalse((self.project / ".agents").exists())
        self.cli("validate_handoff.py", "../../outside.md", expected=2)

    def test_missing_reference_and_secret_are_failures_without_echo(self):
        relative = self.draft()
        path = self.complete(relative)
        secret = "ghp_" + "x" * 30
        path.write_text(path.read_text(encoding="utf-8") + f"\n[missing](absent.py)\n{secret}\n", encoding="utf-8")
        result = self.cli("validate_handoff.py", relative, expected=1)
        self.assertTrue(any("Missing referenced" in e for e in result["errors"]))
        self.assertTrue(any("access token" in e for e in result["errors"]))
        self.assertNotIn(secret, json.dumps(result))

    def test_malformed_timestamp_does_not_echo_input(self):
        relative = self.draft()
        path = self.complete(relative)
        text = re.sub(r'"created_utc": "[^"]+"', '"created_utc": "password=SYNTHETIC_VALUE"', path.read_text(encoding="utf-8"))
        path.write_text(text, encoding="utf-8")
        result = self.cli("validate_handoff.py", relative, expected=1)
        self.assertNotIn("SYNTHETIC_VALUE", json.dumps(result))
        result = self.cli("check_staleness.py", relative, expected=2)
        self.assertNotIn("SYNTHETIC_VALUE", json.dumps(result))

    def test_valid_markdown_link_forms_and_decoded_traversal(self):
        for name in ["file (copy).md", "spaced file.md", "file#name.md"]:
            (self.project / name).write_text("reference", encoding="utf-8")
        relative = self.draft()
        path = self.complete(relative)
        path.write_text(path.read_text(encoding="utf-8") + '\n[one](<file (copy).md>)\n[two](spaced%20file.md "title")\n[three](file%23name.md)\n', encoding="utf-8")
        self.cli("validate_handoff.py", relative)
        path.write_text(path.read_text(encoding="utf-8") + "\n[escape](%2e%2e/outside.md)\n", encoding="utf-8")
        self.cli("validate_handoff.py", relative, expected=1)

    def test_secret_in_reference_destination_is_redacted(self):
        relative = self.draft()
        path = self.complete(relative)
        secret = "ghp_" + "z" * 30
        path.write_text(path.read_text(encoding="utf-8") + f"\n[reference]({secret})\n", encoding="utf-8")
        result = self.cli("validate_handoff.py", relative, expected=1)
        self.assertNotIn(secret, json.dumps(result))
        self.assertTrue(any("withheld" in e for e in result["errors"]))

    def test_code_renamed_into_handoff_directory_is_stale(self):
        relative = self.draft()
        self.git("mv", "README.md", ".agents/handoffs/project-code.md")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    def test_rename_source_is_recorded(self):
        for name in ("a.txt", "b.txt"):
            (self.project / name).write_text("identical contents", encoding="utf-8")
        self.git("add", "a.txt", "b.txt")
        self.git("commit", "-m", "Identical source files")
        self.git("mv", "a.txt", "destination.txt")
        relative = self.draft()
        metadata = handoff.read_handoff(self.project / relative)[1]
        self.assertEqual(metadata["dirty"]["destination.txt"]["original_name"], "a.txt")
        self.git("mv", "destination.txt", "a.txt")
        self.git("mv", "b.txt", "destination.txt")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    def test_changed_working_bytes_are_stale_even_when_status_is_same(self):
        readme = self.project / "README.md"
        readme.write_text("first dirty state", encoding="utf-8")
        relative = self.draft()
        self.assertEqual(self.cli("check_staleness.py", relative)["level"], "FRESH")
        readme.write_text("second dirty state", encoding="utf-8")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    def test_index_only_change_with_identical_worktree_is_stale(self):
        readme = self.project / "README.md"
        readme.write_text("staged one", encoding="utf-8")
        self.git("add", "README.md")
        readme.write_text("working", encoding="utf-8")
        relative = self.draft()
        readme.write_text("staged two", encoding="utf-8")
        self.git("add", "README.md")
        readme.write_text("working", encoding="utf-8")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    def test_large_dirty_file_is_fingerprinted(self):
        large = self.project / "large.txt"
        large.write_bytes(b"a" * 10_000_001)
        relative = self.draft()
        large.write_bytes(b"b" * 10_000_001)
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    def test_new_commit_branch_change_and_missing_history(self):
        relative = self.draft()
        (self.project / "other.txt").write_text("new file", encoding="utf-8")
        self.git("add", "other.txt")
        self.git("commit", "-m", "Next commit")
        result = self.cli("check_staleness.py", relative, expected=1)
        self.assertEqual(result["level"], "SLIGHTLY_STALE")
        self.assertEqual(result["changed_files"], ["other.txt"])
        self.git("checkout", "-b", "different")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")
        path = self.project / relative
        path.write_text(re.sub(r'"head": "[a-f0-9]+"', '"head": "' + "f" * 40 + '"', path.read_text(encoding="utf-8")), encoding="utf-8")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "VERY_STALE")

    def test_sensitive_files_and_non_git_projects_never_claim_freshness(self):
        (self.project / ".env").write_text("PRIVATE_TEST_VALUE", encoding="utf-8")
        relative = self.draft()
        self.assertNotIn("PRIVATE_TEST_VALUE", (self.project / relative).read_text(encoding="utf-8"))
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "UNKNOWN")
        plain = Path(self.temp.name) / "non-git"
        plain.mkdir()
        document = handoff.create(plain, "plain", None)
        self.assertEqual(handoff.staleness(document, plain)["level"], "UNKNOWN")

    @unittest.skipIf(os.name == "nt", "Symlink permissions are not required on Windows; exercised in Linux/macOS CI.")
    def test_external_symlink_identity_is_hashed_without_reading_target(self):
        outside = Path(self.temp.name) / "outside"
        outside.write_text("SYNTHETIC_PRIVATE_CONTENT", encoding="utf-8")
        link = self.project / "link.txt"
        link.symlink_to(outside)
        relative = self.draft()
        self.assertNotIn("SYNTHETIC_PRIVATE_CONTENT", (self.project / relative).read_text(encoding="utf-8"))
        self.assertEqual(self.cli("check_staleness.py", relative)["level"], "FRESH")
        link.unlink()
        link.symlink_to(Path(self.temp.name) / "other-outside")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    @unittest.skipIf(os.name == "nt", "Symlink permissions are not required on Windows; exercised in Linux/macOS CI.")
    def test_symlink_replaced_by_regular_file_is_stale(self):
        link = self.project / "link.txt"
        link.symlink_to("README.md")
        relative = self.draft()
        link.unlink()
        link.write_text("README.md", encoding="utf-8")
        self.assertEqual(self.cli("check_staleness.py", relative, expected=1)["level"], "STALE")

    @unittest.skipIf(os.name == "nt", "Directory symlink regression runs on Linux/macOS without extra privileges.")
    def test_project_directory_alias_is_normalized_by_helper_entrypoints(self):
        alias = Path(self.temp.name) / "project-alias"
        alias.symlink_to(self.project, target_is_directory=True)
        document = handoff.create(alias, "alias", None)
        self.assertTrue(document.is_relative_to(self.project.resolve()))
        self.assertFalse(handoff.validate(document, alias)["passed"])
        self.assertEqual(handoff.staleness(document, alias)["level"], "FRESH")


if __name__ == "__main__":
    unittest.main()
