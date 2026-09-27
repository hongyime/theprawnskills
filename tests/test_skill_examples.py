"""Run the shipped stdlib example and ensure its boundaries detect real faults."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "skills/python-testing/examples/test_port_contract.py"


class PythonExampleTests(unittest.TestCase):
    def test_shipped_example_passes_from_unrelated_directory(self):
        with tempfile.TemporaryDirectory(prefix="python example spaces ") as directory:
            result = subprocess.run([sys.executable, str(EXAMPLE)], cwd=directory, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Ran 3 tests", result.stderr)

    def test_example_rejects_range_and_character_validation_faults(self):
        source = EXAMPLE.read_text(encoding="utf-8")
        mutations = [
            source.replace("1 <= port <= 65535", "0 <= port <= 65535"),
            source.replace("if not text.isascii() or not text.isdecimal():", "if not text.isdecimal():"),
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "faulty_example.py"
            for changed in mutations:
                self.assertNotEqual(source, changed)
                path.write_text(changed, encoding="utf-8")
                result = subprocess.run([sys.executable, str(path)], cwd=directory, capture_output=True, text=True)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("FAIL", result.stderr)


if __name__ == "__main__":
    unittest.main()
