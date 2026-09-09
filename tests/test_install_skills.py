"""Behavioral tests using isolated homes, never the actual agent directories."""

from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import install_skills as installer


class Fixture(unittest.TestCase):
    install_mode = "symlink"

    def setUp(self) -> None:
        self.temp_parent = Path(os.environ.get("PRAWN_TEST_TMP", tempfile.gettempdir())).resolve()
        self.scratch = tempfile.TemporaryDirectory(prefix="prawn-skills-test-", dir=self.temp_parent)
        self.base = Path(self.scratch.name).resolve()
        self.repo = self.base / "repo with spaces"
        self.home = self.base / "isolated home"
        self.repo.mkdir()
        self.home.mkdir()
        for name in ("alpha", "skill-router", "on-demand"):
            folder = self.repo / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(f"---\nname: {name}\ndescription: Useful workflow instructions for testing skill installation.\n---\n", encoding="utf-8")
        (self.repo / "skills/alpha/reference.txt").write_text("supporting content", encoding="utf-8")
        variant = self.repo / "platforms/linux/skills/skill-router"
        variant.mkdir(parents=True)
        (variant / "SKILL.md").write_text("Linux router", encoding="utf-8")
        self.profile = self.repo / "default-profile.toml"
        self.profile.write_text('skills = ["alpha", "skill-router"]\n', encoding="utf-8-sig")

    def tearDown(self) -> None:
        # Only the exact test-owned temporary directory may be recursively cleaned.
        if self.base != Path(self.scratch.name).resolve() or self.base.parent != self.temp_parent or not self.base.name.startswith("prawn-skills-test-"):
            raise RuntimeError("Unexpected cleanup target")
        self.scratch.cleanup()

    def plan(self, agents: list[str] | None = None) -> installer.Plan:
        return installer.make_plan(self.repo, self.home, agents or ["codex"], mode=self.install_mode)


@unittest.skipIf(os.name == "nt", "Windows uses copies without symlink privileges; symlink behavior is tested on macOS/Linux")
class InstallerTests(Fixture):

    def test_preview_writes_nothing(self) -> None:
        plan = self.plan()
        self.assertEqual(len(plan.links), 2)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_install_repeat_and_linux_router_discovery(self) -> None:
        installer.apply_plan(self.plan())
        plan = self.plan()
        self.assertTrue(all(link.exists for link in plan.links))
        self.assertTrue(plan.pointer_exists)
        installer.apply_plan(plan)
        metadata = json.loads(plan.pointer.read_text(encoding="utf-8"))
        library = Path(metadata["library"])
        self.assertTrue((library / "skills/on-demand/SKILL.md").is_file())
        router = self.home / ".agents/skills/skill-router"
        self.assertEqual(router.resolve(), self.repo / "platforms/linux/skills/skill-router")
        self.assertEqual((self.home / ".agents/skills/alpha/reference.txt").read_text(), "supporting content")
        self.assertFalse((self.home / ".agents/skills/on-demand").exists())

    def test_shared_agents_do_not_duplicate_links(self) -> None:
        plan = self.plan(["codex", "opencode", "claude", "cursor"])
        self.assertEqual(len(plan.links), 4)
        installer.apply_plan(plan)
        self.assertFalse((self.home / ".config/opencode/skills").exists())

    def test_conflict_preserves_existing_skill_and_makes_no_changes(self) -> None:
        existing = self.home / ".agents/skills/skill-router"
        existing.mkdir(parents=True)
        marker = existing / "user-content.txt"
        marker.write_text("keep me", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Existing skill preserved"):
            self.plan()
        self.assertEqual(marker.read_text(), "keep me")
        self.assertFalse((self.home / ".agents/skills/alpha").exists())
        self.assertFalse((self.home / ".config").exists())

    def test_missing_source_validates_before_installation(self) -> None:
        self.profile.write_text('skills = ["alpha", "missing"]\n', encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Missing canonical skill"):
            self.plan()
        self.assertEqual(list(self.home.iterdir()), [])

    def test_duplicate_and_traversal_profile_entries_rejected(self) -> None:
        for names in ('["alpha", "alpha"]', '["../outside"]', '[]'):
            with self.subTest(names=names):
                self.profile.write_text(f"skills = {names}\n", encoding="utf-8")
                with self.assertRaises(ValueError):
                    self.plan()
                self.assertEqual(list(self.home.iterdir()), [])

    def test_whole_library_symlink_is_refused(self) -> None:
        (self.home / ".agents").symlink_to(self.repo, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Parent is a symlink"):
            self.plan()
        self.assertTrue((self.repo / "skills/alpha/SKILL.md").is_file())

    def test_dangling_skill_link_is_preserved(self) -> None:
        root = self.home / ".agents/skills"
        root.mkdir(parents=True)
        destination = root / "alpha"
        destination.symlink_to(self.base / "missing", target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Existing skill preserved"):
            self.plan()
        self.assertTrue(destination.is_symlink())

    def test_legacy_codex_duplicate_is_reported(self) -> None:
        legacy = self.home / ".codex/skills/alpha"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("user version", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Legacy Codex"):
            self.plan()
        self.assertFalse((self.home / ".agents").exists())

    def test_different_library_pointer_is_preserved(self) -> None:
        pointer = self.home / ".config/theprawnskills/library.json"
        pointer.parent.mkdir(parents=True)
        original = '{"version": 1, "library": "/another/clone"}'
        pointer.write_text(original, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Existing library configuration"):
            self.plan()
        self.assertEqual(pointer.read_text(), original)
        self.assertFalse((self.home / ".agents").exists())

    def test_profile_reduction_never_prunes(self) -> None:
        installer.apply_plan(self.plan())
        self.profile.write_text('skills = ["alpha"]\n', encoding="utf-8")
        installer.apply_plan(self.plan())
        self.assertTrue((self.home / ".agents/skills/skill-router").is_symlink())

    def test_content_updates_are_visible_through_links(self) -> None:
        installer.apply_plan(self.plan())
        source = self.repo / "skills/alpha/reference.txt"
        source.write_text("updated content", encoding="utf-8")
        self.assertEqual((self.home / ".agents/skills/alpha/reference.txt").read_text(), "updated content")

    def test_racing_destination_is_never_overwritten(self) -> None:
        plan = self.plan()
        destination = self.home / ".agents/skills/alpha"
        destination.mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            installer.apply_plan(plan)
        self.assertTrue(destination.is_dir())
        self.assertFalse(destination.is_symlink())


class CopyInstallerTests(Fixture):
    install_mode = "copy"

    def test_copy_install_needs_no_symlink_privileges_and_is_repeatable(self) -> None:
        with mock.patch.object(Path, "symlink_to", side_effect=AssertionError("Copy mode must not create symlinks")):
            plan = self.plan()
            self.assertEqual(list(self.home.iterdir()), [])
            installer.apply_plan(plan)
            repeated = self.plan()
            self.assertTrue(all(item.exists and item.mode == "copy" for item in repeated.links))
            installer.apply_plan(repeated)
        skill = self.home / ".agents/skills/alpha"
        self.assertFalse(skill.is_symlink())
        self.assertEqual((skill / "reference.txt").read_text(), "supporting content")
        self.assertFalse((self.home / ".agents/skills/on-demand").exists())
        self.assertEqual((self.home / ".agents/skills/skill-router/SKILL.md").read_text(), "Linux router")

    def test_update_backs_up_old_copy_before_installing_new_content(self) -> None:
        installer.apply_plan(self.plan())
        (self.repo / "skills/alpha/reference.txt").write_text("new content", encoding="utf-8")
        plan = self.plan()
        update = next(item for item in plan.links if item.destination.name == "alpha")
        self.assertFalse(update.exists)
        self.assertIsNotNone(update.backup)
        self.assertEqual((update.destination / "reference.txt").read_text(), "supporting content")
        installer.apply_plan(plan)
        self.assertEqual((update.destination / "reference.txt").read_text(), "new content")
        self.assertEqual((update.backup / "reference.txt").read_text(), "supporting content")
        self.assertTrue(all(item.exists for item in self.plan().links))

    def test_local_edits_are_never_replaced(self) -> None:
        installer.apply_plan(self.plan())
        target = self.home / ".agents/skills/alpha/reference.txt"
        target.write_text("my local changes", encoding="utf-8")
        (self.repo / "skills/alpha/reference.txt").write_text("upstream changes", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Local edits preserved"):
            self.plan()
        self.assertEqual(target.read_text(), "my local changes")
        self.assertFalse((self.home / "Backups").exists())

    def test_unmanaged_copy_is_preserved(self) -> None:
        existing = self.home / ".agents/skills/alpha"
        existing.mkdir(parents=True)
        (existing / "SKILL.md").write_text("my skill", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Existing skill preserved"):
            self.plan()
        self.assertEqual((existing / "SKILL.md").read_text(), "my skill")
        self.assertFalse((self.home / ".agents/skills/skill-router").exists())

    def test_racing_copy_destination_is_preserved(self) -> None:
        plan = self.plan()
        existing = self.home / ".agents/skills/alpha"
        existing.mkdir(parents=True)
        with self.assertRaises(FileExistsError):
            installer.apply_plan(plan)
        self.assertEqual(list(existing.iterdir()), [])

    def test_interrupted_update_leaves_old_content_in_backup(self) -> None:
        installer.apply_plan(self.plan())
        (self.repo / "skills/alpha/reference.txt").write_text("new content", encoding="utf-8")
        plan = self.plan()
        update = next(item for item in plan.links if item.backup)
        with mock.patch.object(installer.shutil, "copytree", side_effect=OSError("Simulated disk error")):
            with self.assertRaisesRegex(OSError, "Simulated disk error"):
                installer.apply_plan(plan)
        self.assertEqual((update.backup / "reference.txt").read_text(), "supporting content")

    def test_source_change_after_preview_stops_before_writing(self) -> None:
        plan = self.plan()
        (self.repo / "skills/alpha/reference.txt").write_text("new content", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Source changed since preview"):
            installer.apply_plan(plan)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_auto_mode_matches_operating_system(self) -> None:
        plan = installer.make_plan(self.repo, self.home, ["codex"])
        expected = "copy" if os.name == "nt" else "symlink"
        self.assertTrue(all(item.mode == expected for item in plan.links))


class ProfileIntegrationTests(Fixture):
    def test_actual_profile_cli_preview_apply_check_and_repeat(self) -> None:
        command = [sys.executable, str(ROOT / "scripts/install_skills.py"), "--home", str(self.home), "--agents", "codex"]
        preview = subprocess.run([*command, "--dry-run"], capture_output=True, text=True)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertEqual(list(self.home.iterdir()), [])
        before = subprocess.run([*command, "--check"], capture_output=True, text=True)
        self.assertEqual(before.returncode, 1)
        for mode in ("--apply", "--check", "--apply", "--check"):
            result = subprocess.run([*command, mode], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
        links = list((self.home / ".agents/skills").iterdir())
        self.assertEqual(len(links), 64)
        self.assertTrue(all((link / "SKILL.md").is_file() for link in links))
        self.assertTrue(all(link.is_symlink() == (os.name != "nt") for link in links))
        metadata = json.loads((self.home / ".config/theprawnskills/library.json").read_text())
        self.assertTrue((Path(metadata["library"]) / "skills/pdf/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
