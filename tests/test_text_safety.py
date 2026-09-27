from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from audit_text_safety import TAG_FLAGS, audit, findings


class TextSafetyTests(unittest.TestCase):
    def test_hidden_controls_are_reported_at_exact_positions(self):
        for code in (0x202E, 0x2066, 0xE0061, 0x200B, 0x2060, 0xFEFF):
            with self.subTest(code=code):
                self.assertEqual(findings("safe\nabc" + chr(code)), [(2, 4, code)])

    def test_legitimate_languages_emoji_and_leading_bom_are_preserved(self):
        text = "\ufeff中文 日本語 العربية\n" + "👩\u200d💻 ✅️ می\u200cروم"
        self.assertEqual(findings(text), [])

    def test_worktree_scan_includes_untracked_text_and_never_rewrites(self):
        with tempfile.TemporaryDirectory(prefix="unicode audit spaces ") as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            (root / ".gitignore").write_text("private.md\n", encoding="utf-8")
            bad = root / "new-skill.md"
            bad.write_text("PRIVATE_SENTINEL" + chr(0x202E), encoding="utf-8")
            (root / "private.md").write_text(chr(0x202E), encoding="utf-8")
            (root / "photo.png").write_bytes(b"\xff\xfe")
            before = bad.read_bytes()
            result = audit(root)
            self.assertEqual(len(result), 1)
            self.assertIn("new-skill.md:1:17: suspicious U+202E", result[0])
            self.assertNotIn("PRIVATE_SENTINEL", result[0])
            self.assertEqual(bad.read_bytes(), before)

    def test_complete_subdivision_flags_are_allowed_but_extra_tags_are_not(self):
        for flag in TAG_FLAGS:
            self.assertEqual(findings(flag), [])
            self.assertEqual(findings(flag + chr(0xE0061)), [(1, len(flag) + 1, 0xE0061)])
        self.assertTrue(findings("\U0001f3f4\U000e0061\U000e007f"))

    def test_invalid_utf8_is_a_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            (root / "bad.md").write_bytes(b"\xff")
            self.assertEqual(audit(root), ["bad.md: text must be UTF-8"])

    def test_filename_controls_are_detected_and_escaped_in_diagnostics(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "-q", str(root)], check=True, capture_output=True)
            (root / ("review" + chr(0x202E) + ".md")).write_text("clean body", encoding="utf-8")
            result = audit(root)
            self.assertEqual(len(result), 1)
            self.assertIn("filename", result[0])
            self.assertNotIn(chr(0x202E), result[0])
            self.assertIn("\\u202e", result[0])


if __name__ == "__main__":
    unittest.main()
