from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("resource_audit", ROOT / "scripts/audit_skill_resources.py")
audit = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = audit
spec.loader.exec_module(audit)


class ResourceAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill-resource-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.skill = self.root / "skills/example"
        self.skill.mkdir(parents=True)
        (self.skill / "SKILL.md").write_text("# Example\n", encoding="utf-8")

    def write(self, relative, text):
        path = self.skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def test_nested_links_and_commands_use_distinct_bases(self):
        self.write("SKILL.md", "[guide](references/guide.md)\n")
        self.write("references/guide.md", "[sibling](other.md)\npython scripts/tool.py\n")
        self.write("references/other.md", "# Other\n")
        self.write("scripts/tool.py", "pass\n")
        self.assertEqual(audit.audit(self.root)["missing"], [])
        (self.skill / "scripts/tool.py").unlink()
        result = audit.audit(self.root)
        self.assertEqual(result["missing"][0]["target"], "scripts/tool.py")

    def test_external_dynamic_and_fenced_links_not_false_missing(self):
        self.write("SKILL.md", '[remote](https://example.invalid/x)\n[anchor](#section)\n```md\n[example](placeholder.md)\n```\n')
        self.assertEqual(audit.audit(self.root)["missing"], [])

    def test_windows_commands_and_extension_boundaries(self):
        self.write("SKILL.md", "pwsh -File .\\scripts\\tool.ps1\n`assets/config.json`\n")
        self.write("assets/config.json", "{}")
        missing = audit.audit(self.root)["missing"]
        self.assertEqual([x["target"] for x in missing], ["./scripts/tool.ps1"])

    def test_bad_link_not_masked_by_file_at_skill_root(self):
        self.write("references/read.md", "[bad relative](scripts/tool.py)\n")
        self.write("scripts/tool.py", "pass")
        missing = audit.audit(self.root)["missing"]
        self.assertEqual(missing[0]["kind"], "link")

    def test_exact_exception_is_reported_and_becomes_stale_when_fixed(self):
        self.write("SKILL.md", "`scripts/example.py`\n")
        policy = self.root / "exceptions.json"
        policy.write_text(json.dumps({"exceptions": [{"source": "skills/example/SKILL.md", "target": "scripts/example.py", "kind": "resource", "reason": "Illustrative test fixture."}]}), encoding="utf-8")
        result = audit.audit(self.root, policy)
        self.assertEqual(len(result["contextual_exceptions"]), 1)
        self.assertEqual(result["missing"], [])
        self.write("scripts/example.py", "pass")
        self.assertEqual(len(audit.audit(self.root, policy)["stale_exceptions"]), 1)

    def test_platform_variants_and_nested_skill_definitions_are_scanned(self):
        portable = self.root / "platforms/linux/skills/example"
        portable.mkdir(parents=True)
        (portable / "SKILL.md").write_text("[missing](references/required.md)", encoding="utf-8")
        self.write("nested/SKILL.md", "# Nested")
        result = audit.audit(self.root)
        self.assertEqual(result["skill_definitions"], 3)
        self.assertEqual(result["missing"][0]["source"], "platforms/linux/skills/example/SKILL.md")

    def test_repository_has_no_unresolved_or_stale_entries(self):
        result = audit.audit(ROOT, ROOT / "scripts/skill-resource-exceptions.json")
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["stale_exceptions"], [])
        self.assertGreaterEqual(result["skill_definitions"], 224)

    def test_absent_or_empty_root_fails(self):
        with self.assertRaises(ValueError):
            audit.audit(self.root / "missing-root")
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(ValueError):
            audit.audit(empty)

    def test_parent_relative_command_and_reference_style_links(self):
        self.write("SKILL.md", "python ../scripts/missing.py\n[guide][id]\n[id]: absent.md\n")
        result = audit.audit(self.root)
        self.assertEqual({x["target"] for x in result["missing"]}, {"../scripts/missing.py", "absent.md"})

    def test_four_backtick_fence_preserves_real_links_after_close(self):
        self.write("SKILL.md", "````md\n```\n[example](ignored.md)\n````\n[real](missing.md)\n")
        result = audit.audit(self.root)
        self.assertEqual([x["target"] for x in result["missing"]], ["missing.md"])


if __name__ == "__main__":
    unittest.main()
