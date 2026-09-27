"""Process lifecycle tests for the browser helper; no browser dependency."""
import os
from pathlib import Path
import shlex
import signal
import socket
import subprocess
import sys
import tempfile
import time
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'skills/webapp-testing/scripts/with_server.py'
SERVER = """import http.server,sys,os
from pathlib import Path
Path(sys.argv[2]).write_text(str(os.getpid()), encoding='ascii')
print('x' * 250000, flush=True)
http.server.HTTPServer(('127.0.0.1', int(sys.argv[1])), http.server.SimpleHTTPRequestHandler).serve_forever()
"""


def shell_command(parts):
    return subprocess.list2cmdline(parts) if os.name == 'nt' else shlex.join(parts)


class BrowserServerTests(unittest.TestCase):
    def test_noisy_foreground_child_is_stopped_and_failure_exit_is_preserved(self):
        with tempfile.TemporaryDirectory(prefix='server helper spaces ') as directory:
            script = Path(directory) / 'noisy server.py'
            script.write_text(SERVER, encoding='utf-8')
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            pid_file = Path(directory) / 'fixture.pid'
            server = shell_command([sys.executable, str(script), str(port), str(pid_file)])
            try:
                result = subprocess.run([sys.executable, str(HELPER), '--server', server,
                                     '--port', str(port), '--timeout', '15', '--',
                                     sys.executable, '-c', 'raise SystemExit(7)'],
                                        cwd=directory, capture_output=True, text=True, timeout=120)
                self.assertEqual(result.returncode, 7, result.stderr + result.stdout)
                self.assertIn('All managed foreground servers stopped', result.stdout)
                with self.assertRaises(OSError):
                    with socket.create_connection(('127.0.0.1', port), timeout=1):
                        pass
            finally:
                # Cleanup must not depend solely on the helper being tested.
                if pid_file.exists():
                    pid = int(pid_file.read_text(encoding='ascii'))
                    if os.name == 'nt':
                        subprocess.run(['taskkill', '/PID', str(pid), '/T', '/F'],
                                       capture_output=True, timeout=60)
                    else:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                    time.sleep(0.1)

    def test_occupied_port_is_preserved_and_command_never_runs(self):
        with socket.socket() as sock, tempfile.TemporaryDirectory() as directory:
            sock.bind(('127.0.0.1', 0))
            sock.listen()
            port = sock.getsockname()[1]
            marker = Path(directory) / 'should-not-exist'
            result = subprocess.run([sys.executable, str(HELPER), '--server', 'unused',
                                     '--port', str(port), '--', sys.executable, '-c',
                                     'from pathlib import Path; Path("should-not-exist").touch()'],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('already occupied', result.stderr)
            self.assertFalse(marker.exists())
            self.assertGreaterEqual(sock.fileno(), 0)

    def test_startup_failure_never_runs_downstream_command(self):
        with tempfile.TemporaryDirectory() as directory:
            with socket.socket() as sock:
                sock.bind(('127.0.0.1', 0))
                port = sock.getsockname()[1]
            command = shell_command([sys.executable, '-c', 'raise SystemExit(2)'])
            result = subprocess.run([sys.executable, str(HELPER), '--server', command,
                                     '--port', str(port), '--timeout', '1', '--', sys.executable,
                                     '-c', 'from pathlib import Path; Path("unexpected").touch()'],
                                    cwd=directory, capture_output=True, text=True, timeout=30)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('failed to start', result.stderr)
            self.assertFalse((Path(directory) / 'unexpected').exists())


if __name__ == '__main__':
    unittest.main()
