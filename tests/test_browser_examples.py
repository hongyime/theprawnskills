"""Real Chromium probes; opt in after installing requirements-browser-checks.txt."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
import signal
from socketserver import TCPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "skills/webapp-testing/examples"
HTML = """<!doctype html><html><body>
<main id="ready" hidden><button>Save</button><input aria-label="Name">
<a href="#result" onclick="document.getElementById('result').hidden=false;
console.log('fixture navigation complete')">Dashboard</a></main>
<section id="result" hidden>Dashboard ready</section>
<script>setTimeout(()=>document.getElementById('ready').hidden=false, 300);
if(location.protocol==='http:') setInterval(()=>fetch('/poll'), 100);</script>
</body></html>"""


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class LocalHTTPServer(ThreadingHTTPServer):
    def server_bind(self):
        # This isolated loopback fixture must not depend on external DNS.
        TCPServer.server_bind(self)
        self.server_name = 'localhost'
        self.server_port = self.server_address[1]


@unittest.skipUnless(os.environ.get("PRAWN_BROWSER_TESTS") == "1", "opt-in real Chromium suite")
class BrowserExamplesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix="browser examples spaces ")
        cls.root = Path(cls.temp.name)
        cls.html = cls.root / "page with spaces.html"
        cls.html.write_text(HTML, encoding="utf-8")
        (cls.root / "poll").write_text("ok", encoding="utf-8")
        cls.server = LocalHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=cls.temp.name))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/page%20with%20spaces.html"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)
        cls.temp.cleanup()

    def run_example(self, name, *args):
        command = [sys.executable, str(EXAMPLES / name), *map(str, args)]
        process = subprocess.Popen(command, cwd=self.root, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, text=True,
                                   start_new_session=(os.name != 'nt'))
        try:
            stdout, stderr = process.communicate(timeout=120)
        except subprocess.TimeoutExpired:
            if os.name == 'nt':
                subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                               capture_output=True, timeout=15)
            else:
                os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate(timeout=15)
            self.fail(f'Browser example exceeded its deadline: {stdout}\n{stderr}')
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)

    def assert_png(self, path):
        self.assertEqual(path.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")

    def test_discovery_waits_for_delayed_ui_while_network_keeps_polling(self):
        output = self.root / "discovery outputs"
        result = self.run_example("element_discovery.py", "--url", self.url,
                                  "--ready-selector", "#ready", "--output-dir", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("buttons: 1", result.stdout)
        self.assert_png(output / "page-discovery.png")

    def test_console_flow_records_the_actual_action(self):
        output = self.root / "console outputs"
        result = self.run_example("console_logging.py", "--url", self.url,
                                  "--ready-selector", "#ready", "--link-name", "Dashboard",
                                  "--result-selector", "#result", "--output-dir", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("fixture navigation complete", (output / "console.log").read_text(encoding="utf-8"))

    def test_static_file_uri_supports_spaces(self):
        output = self.root / "static outputs"
        result = self.run_example("static_html_automation.py", "--html", self.html,
                                  "--ready-selector", "#ready", "--output-dir", output)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assert_png(output / "static-page.png")

    def test_missing_ready_state_fails_without_success_artifact(self):
        output = self.root / "failed outputs"
        result = self.run_example("element_discovery.py", "--url", self.url,
                                  "--ready-selector", "#never-exists", "--output-dir", output)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AssertionError", result.stderr)
        self.assertFalse((output / "page-discovery.png").exists())


if __name__ == "__main__":
    unittest.main()
