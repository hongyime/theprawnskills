"""Tests for the platform-line audit (scripts/audit_skill_platforms.py).

Covers the token-set check, frontmatter parsing, Windows path
normalisation, and stale-exception detection, including the case where an
exception points at an existing file that is not a scanned skill.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "platform_audit", ROOT / "scripts/audit_skill_platforms.py"
)
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)

CONTRACT = "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"


def skill_md(platform=None):
    lines = [
        "---",
        "name: example",
        "description: An example skill for testing platform lines.",
        "metadata:",
        "  author: Local setup",
        '  version: "1.0.0"',
    ]
    if platform is not None:
        lines.append(f'  platform: "{platform}"')
    lines.append("---")
    lines.append("")
    lines.append("# Example")
    return "\n".join(lines) + "\n"


class TokenTests(unittest.TestCase):
    def test_missing_line_reports_all_tokens(self):
        self.assertEqual(audit.missing_tokens(None), list(audit.REQUIRED_TOKENS))

    def test_contract_line_reports_nothing_missing(self):
        self.assertEqual(audit.missing_tokens(CONTRACT), [])

    def test_superset_line_reports_nothing_missing(self):
        self.assertEqual(audit.missing_tokens(CONTRACT + ", Kiro"), [])

    def test_partial_line_reports_only_the_missing_tokens(self):
        self.assertEqual(
            audit.missing_tokens("Codex on Windows"),
            ["Antigravity (agy)", "OpenCode", "Muse", "macOS", "Linux (Debian)"],
        )


class ParseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-platform-parse-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def write(self, text):
        path = self.root / "SKILL.md"
        path.write_text(text, encoding="utf-8")
        return path

    def test_platform_of_reads_the_metadata_value(self):
        self.assertEqual(audit.platform_of(self.write(skill_md(CONTRACT))), CONTRACT)

    def test_platform_of_returns_none_without_a_platform_line(self):
        self.assertIsNone(audit.platform_of(self.write(skill_md())))

    def test_platform_of_returns_none_without_frontmatter(self):
        self.assertIsNone(audit.platform_of(self.write("# No frontmatter\n")))


class PosixTests(unittest.TestCase):
    def test_backslashes_become_forward_slashes(self):
        with mock.patch.object(os, "sep", "\\"):
            self.assertEqual(
                audit.to_posix("skills\\codex\\SKILL.md"), "skills/codex/SKILL.md"
            )

    def test_forward_slashes_are_unchanged(self):
        self.assertEqual(
            audit.to_posix("skills/codex/SKILL.md"), "skills/codex/SKILL.md"
        )


class MainTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-platform-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self._orig_root = audit.ROOT
        self._orig_exceptions = audit.EXCEPTIONS_PATH
        audit.ROOT = str(self.root)
        audit.EXCEPTIONS_PATH = str(self.root / "exceptions.json")
        self.addCleanup(setattr, audit, "ROOT", self._orig_root)
        self.addCleanup(setattr, audit, "EXCEPTIONS_PATH", self._orig_exceptions)
        self.write_exceptions([])

    def write_exceptions(self, entries):
        (self.root / "exceptions.json").write_text(
            json.dumps({"exceptions": entries}), encoding="utf-8"
        )

    def write_skill(self, relative, platform=CONTRACT):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(skill_md(platform), encoding="utf-8")
        return path

    def run_main(self):
        out = io.StringIO()
        with redirect_stdout(out):
            code = audit.main()
        return code, out.getvalue()

    def test_clean_tree_returns_zero(self):
        self.write_skill("skills/example/SKILL.md")
        code, out = self.run_main()
        self.assertEqual(code, 0)
        self.assertIn("OK", out)

    def test_violation_returns_one(self):
        self.write_skill("skills/example/SKILL.md", platform=None)
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("skills/example/SKILL.md", out)

    def test_exceptioned_violation_returns_zero(self):
        self.write_skill("skills/example/SKILL.md", platform=None)
        self.write_exceptions(
            [{"source": "skills/example/SKILL.md", "reason": "test exception"}]
        )
        code, _ = self.run_main()
        self.assertEqual(code, 0)

    def test_exception_for_complying_file_is_stale(self):
        self.write_skill("skills/example/SKILL.md")
        self.write_exceptions(
            [{"source": "skills/example/SKILL.md", "reason": "test exception"}]
        )
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("file now complies", out)

    def test_exception_for_missing_path_is_stale(self):
        self.write_exceptions(
            [{"source": "skills/gone/SKILL.md", "reason": "test exception"}]
        )
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("path does not exist", out)

    def test_exception_for_unscanned_file_is_stale(self):
        (self.root / "README.md").write_text("# Not a skill\n", encoding="utf-8")
        self.write_exceptions(
            [{"source": "README.md", "reason": "test exception"}]
        )
        code, out = self.run_main()
        self.assertEqual(code, 1)
        self.assertIn("not a scanned skill file", out)

    def test_platforms_tree_is_scanned(self):
        self.write_skill("platforms/linux/skills/example/SKILL.md", platform=None)
        self.write_exceptions(
            [
                {
                    "source": "platforms/linux/skills/example/SKILL.md",
                    "reason": "test exception",
                }
            ]
        )
        code, _ = self.run_main()
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
