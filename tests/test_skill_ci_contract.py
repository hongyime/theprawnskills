"""Ensure documentation-only changes retain the intended CI coverage."""
import fnmatch
from pathlib import Path
import unittest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class SkillCIContractTests(unittest.TestCase):
    def test_secret_scan_includes_skills_and_handoffs(self):
        data = yaml.load((ROOT / ".github/workflows/trufflehog.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        for event in ("push", "pull_request"):
            ignored = data["on"][event].get("paths-ignore", [])
            for document in ("skills/example/SKILL.md", ".agents/handoffs/resume.md", "docs/guide.md"):
                self.assertFalse(any(fnmatch.fnmatch(document, pattern) for pattern in ignored), (event, document))

    def test_library_checks_run_for_index_and_dependency_changes(self):
        data = yaml.load((ROOT / ".github/workflows/skills.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
        for event in ("push", "pull_request"):
            patterns = data["on"][event]["paths"]
            for changed in ("INDEX.md", "requirements-skill-checks.txt", "skills/example/SKILL.md"):
                self.assertTrue(any(fnmatch.fnmatch(changed, pattern) for pattern in patterns), (event, changed))


if __name__ == "__main__":
    unittest.main()
