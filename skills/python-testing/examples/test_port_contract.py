"""Self-contained unittest example; no network or installed pytest required."""
from pathlib import Path
import tempfile
import unittest


def load_port(path: Path) -> int:
    """Example contract: an ASCII decimal port, 1 through 65535 inclusive."""
    text = path.read_text(encoding="utf-8").strip()
    if not text.isascii() or not text.isdecimal():
        raise ValueError("Port must be an ASCII decimal integer")
    port = int(text)
    if not 1 <= port <= 65535:
        raise ValueError("Port outside supported range")
    return port


class PortContractTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="port example ")
        self.addCleanup(temporary.cleanup)
        self.path = Path(temporary.name) / "port value.txt"

    def test_valid_boundaries_and_whitespace(self):
        for content, expected in [("1", 1), ("65535", 65535), (" 8080\n", 8080)]:
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                self.assertEqual(load_port(self.path), expected)

    def test_rejects_invalid_and_outside_boundaries(self):
        for content in ["", "0", "65536", "-1", "1.5", "port", "１２"]:
            with self.subTest(content=content):
                self.path.write_text(content, encoding="utf-8")
                with self.assertRaises(ValueError):
                    load_port(self.path)

    def test_missing_file_is_not_silently_defaulted(self):
        with self.assertRaises(FileNotFoundError):
            load_port(self.path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
