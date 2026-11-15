"""Tests for the HTML checker (skills/visual-explainer/scripts/check_html.py).

Covers the design-token check, the section-order check, and the existing
section-presence check, including the case where a token appears only in an
inline style attribute (which must not count — the stylesheet is what the
check protects).
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "check_html", ROOT / "skills/visual-explainer/scripts/check_html.py"
)
checker = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = checker
spec.loader.exec_module(checker)


def doc(tokens=None, order=("overview", "details", "next-steps"), inline=""):
    """Minimal document with a <style> block and the three sections."""
    if tokens is None:
        tokens = checker.EXPECTED_TOKENS
    style = ":root{" + ";".join(f"--{name}:{value}" for name, value in tokens) + "}"
    sections = "".join(f'<section id="{name}"></section>' for name in order)
    return (
        "<!doctype html><html><head><style>"
        + style
        + "</style></head><body>"
        + inline
        + sections
        + "</body></html>"
    )


class CheckHtmlTests(unittest.TestCase):
    def run_check(self, html):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "doc.html"
            path.write_text(html, encoding="utf-8")
            out = io.StringIO()
            with redirect_stdout(out):
                result = checker.check(path)
            return result, out.getvalue()

    def test_template_passes(self):
        template = ROOT / "skills/visual-explainer/templates/explainer.html"
        out = io.StringIO()
        with redirect_stdout(out):
            result = checker.check(template)
        self.assertEqual(result, 0, out.getvalue())

    def test_all_tokens_present_passes(self):
        result, _ = self.run_check(doc())
        self.assertEqual(result, 0)

    def test_missing_token_fails_and_names_it(self):
        missing = [pair for pair in checker.EXPECTED_TOKENS if pair[0] != "accent"]
        result, output = self.run_check(doc(tokens=missing))
        self.assertEqual(result, 1)
        self.assertIn("Missing design token: accent #67D4E8", output)

    def test_tokens_are_case_insensitive(self):
        lowered = doc().lower()
        result, _ = self.run_check(lowered)
        self.assertEqual(result, 0)

    def test_wrong_section_order_fails(self):
        result, output = self.run_check(doc(order=("details", "overview", "next-steps")))
        self.assertEqual(result, 1)
        self.assertIn("out of order", output)

    def test_missing_section_fails(self):
        result, output = self.run_check(doc(order=("overview", "details")))
        self.assertEqual(result, 1)
        self.assertIn("Missing document section: next-steps", output)

    def test_inline_style_token_does_not_count(self):
        missing = [pair for pair in checker.EXPECTED_TOKENS if pair[0] != "accent"]
        html = doc(tokens=missing, inline='<div style="color:#67D4E8">x</div>')
        result, output = self.run_check(html)
        self.assertEqual(result, 1)
        self.assertIn("Missing design token: accent #67D4E8", output)


if __name__ == "__main__":
    unittest.main()
