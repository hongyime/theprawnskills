"""Regression tests for metadata decoding, portable discovery and stale-index gates."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from skill_catalog import CatalogError, catalog, profile, read_skill, render_index


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill library spaces ")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        (self.root / "default-profile.toml").write_text('skills = ["example"]\n', encoding="utf-8")

    def skill(self, description, name="example", prefix="skills", extra=""):
        path = self.root / prefix / name / "SKILL.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"---\nname: {name}\ndescription: {description}\n{extra}---\n# Example\n", encoding="utf-8")
        return path

    def test_literal_folded_and_quoted_descriptions_have_real_index_text(self):
        for style in ("|", "|-", ">", ">-"):
            with self.subTest(style=style):
                p = self.skill(style + "\n  Review project changes and report evidence.\n  Use when finishing a task.")
                self.assertEqual(read_skill(p).description,
                                 "Review project changes and report evidence. Use when finishing a task.")
                self.assertIn("| `example` | Review project changes", render_index(self.root))
        p = self.skill('"Use when checking YAML: quoted descriptions with a # and | remain intact."')
        self.assertIn("# and \\| remain intact", render_index(self.root))

    def test_bom_crlf_and_unicode_survive(self):
        p = self.skill('"Review multilingual guidance and preserve 中文 and emoji when building skills."')
        p.write_bytes(b"\xef\xbb\xbf" + p.read_bytes().replace(b"\n", b"\r\n"))
        self.assertIn("中文", read_skill(p).description)

    def test_invalid_metadata_fails_without_echoing_values(self):
        p = self.skill('"Review changes and report actual project evidence before completion."')
        for body in (
            "# no frontmatter",
            "---\nname: other\ndescription: Valid descriptive content for a review of changes.\n---\n",
            "---\nname: example\nname: example\ndescription: This is a sufficiently long duplicate name example.\n---\n",
            "---\nname: example\ndescription: [not, a, string]\n---\n",
            "---\nname: example\ndescription: tiny\n---\n",
            "---\nname: example\ndescription: unquoted: PRIVATE_SENTINEL\n---\n",
            "---\nname: example\ndescription: !!python/object/apply:os.system [PRIVATE_SENTINEL]\n---\n",
            "---\nname: example\ndescription: !!int PRIVATE_SENTINEL\n---\n",
            "---\nname: example\ndescription: !!float PRIVATE_SENTINEL\n---\n",
            "---\nname: example\ndescription: !!timestamp PRIVATE_SENTINEL\n---\n",
        ):
            with self.subTest(body=body[:30]):
                p.write_text(body, encoding="utf-8")
                with self.assertRaises(CatalogError) as caught:
                    read_skill(p)
                self.assertNotIn("PRIVATE_SENTINEL", str(caught.exception))

    def test_nested_skills_and_platform_variants_are_validated(self):
        self.skill('"Review project changes and report evidence when requested."')
        self.skill('"Review nested functionality and report evidence when requested."', "nested", "skills/example")
        self.skill('"Review portable functionality and report evidence when requested."', prefix="platforms/linux/skills")
        self.assertEqual(len(catalog(self.root)), 3)
        index = render_index(self.root)
        self.assertIn("| Top-level skills | 1 |", index)
        self.assertIn("| Portable variants | 1 |", index)
        self.assertNotIn("| `nested`", index)
        self.assertEqual(index.count("| `example`"), 1)

    def test_profile_rejects_missing_and_duplicate_skills(self):
        self.skill('"Review project changes and report evidence when requested."')
        for names in ('["absent"]', '["example", "example"]', '"example"', '[]'):
            (self.root / "default-profile.toml").write_text("skills = " + names, encoding="utf-8")
            with self.assertRaises(CatalogError):
                profile(self.root, catalog(self.root))

    def test_check_cli_detects_drift_without_rewriting(self):
        p = self.skill('"Review project changes and report evidence when requested."')
        index = self.root / "INDEX.md"
        index.write_text(render_index(self.root), encoding="utf-8")
        command = [sys.executable, str(REPO / "scripts/update_skill_index.py"), "--root", str(self.root), "--check"]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        before = index.read_bytes()
        p.write_text(p.read_text().replace("Review project", "Verify project"), encoding="utf-8")
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1)
        self.assertEqual(index.read_bytes(), before)

    def test_cli_redacts_typed_scalar_constructor_errors(self):
        for tag in ("int", "float", "timestamp"):
            self.skill(f"!!{tag} PRIVATE_SENTINEL")
            result = subprocess.run([sys.executable, str(REPO / "scripts/update_skill_index.py"),
                                     "--root", str(self.root), "--check"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 2)
            self.assertNotIn("PRIVATE_SENTINEL", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

    def test_render_is_deterministic_and_does_not_claim_installation(self):
        self.skill('"Review project changes and report evidence when requested."')
        self.skill('"Use when testing an optional workflow without changing the daily profile."', "optional")
        first = render_index(self.root)
        self.assertEqual(first, render_index(self.root))
        self.assertIn("| DAILY |", first)
        self.assertIn("| ON-DEMAND |", first)
        self.assertNotIn(str(self.root), first)
        self.assertNotIn("INSTALLED", first)


if __name__ == "__main__":
    unittest.main()
