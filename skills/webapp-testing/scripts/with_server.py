#!/usr/bin/env python3
"""
Start one or more servers, wait for them to be ready, run a command, then clean up.

Usage:
    # Single server
    python scripts/with_server.py --server "npm run dev" --port 5173 -- python automation.py
    python scripts/with_server.py --server "npm start" --port 3000 -- python test.py

    # Multiple servers
    python scripts/with_server.py \
      --server "cd backend && python server.py" --port 3000 \
      --server "cd frontend && npm run dev" --port 5173 \
      -- python test.py
"""

import subprocess
import socket
import time
import sys
import argparse
import os
import signal
import tempfile


def group_has_live_members(group):
    """Darwin killpg reports EPERM for zombie-only groups; inspect status only."""
    result = subprocess.run(['ps', '-eo', 'pgid=,stat='], capture_output=True,
                            text=True, check=True, timeout=5)
    return any(len(parts := line.split()) == 2 and parts[0] == str(group)
               and not parts[1].startswith('Z') for line in result.stdout.splitlines())


def stop_server(process):
    """Stop the foreground shell and its process tree, not just the shell PID."""
    if os.name == 'nt':
        if process.poll() is None:
            result = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                    capture_output=True, timeout=45)
            if result.returncode and process.poll() is None:
                raise RuntimeError('Could not stop server process tree')
    else:
        # The process group can outlive its leader. Reap the leader, then
        # distinguish live descendants from Darwin's zombie-only groups.
        process.poll()
        try:
            if group_has_live_members(process.pid):
                os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass
            try:
                if group_has_live_members(process.pid):
                    os.killpg(process.pid, signal.SIGKILL)
            except PermissionError:
                if group_has_live_members(process.pid):
                    raise
        except ProcessLookupError:
            pass
        except PermissionError:
            if group_has_live_members(process.pid):
                raise
    process.wait(timeout=10)


def port_open(port):
    try:
        with socket.create_connection(('localhost', port), timeout=0.2):
            return True
    except OSError:
        return False

def is_server_ready(port, timeout=30):
    """Wait for server to be ready by polling the port."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection(('localhost', port), timeout=1):
                return True
        except (socket.error, ConnectionRefusedError):
            time.sleep(0.5)
    return False


def main():
    parser = argparse.ArgumentParser(description='Run command with one or more servers')
    parser.add_argument('--server', action='append', dest='servers', required=True, help='Server command (can be repeated)')
    parser.add_argument('--port', action='append', dest='ports', type=int, required=True, help='Port for each server (must match --server count)')
    parser.add_argument('--timeout', type=int, default=30, help='Timeout in seconds per server (default: 30)')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command to run after server(s) ready')

    args = parser.parse_args()

    # Remove the '--' separator if present
    if args.command and args.command[0] == '--':
        args.command = args.command[1:]

    if not args.command:
        print("Error: No command specified to run")
        sys.exit(1)

    # Parse server configurations
    if len(args.servers) != len(args.ports):
        print("Error: Number of --server and --port arguments must match")
        sys.exit(1)

    servers = []
    for cmd, port in zip(args.servers, args.ports):
        servers.append({'cmd': cmd, 'port': port})

    server_processes = []
    server_logs = []

    try:
        # Start all servers
        for i, server in enumerate(servers):
            if port_open(server['port']):
                raise RuntimeError(f"Port {server['port']} is already occupied; reuse or stop its owner explicitly")
            print(f"Starting server {i+1}/{len(servers)}: {server['cmd']}")

            # Use shell=True to support commands with cd and &&
            # A file cannot deadlock on an unread pipe buffer. Keep raw logs local.
            log = tempfile.TemporaryFile(mode='w+b')
            server_logs.append(log)
            process = subprocess.Popen(
                server['cmd'],
                shell=True,
                stdout=log,
                stderr=subprocess.STDOUT,
                start_new_session=(os.name != 'nt'),
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            server_processes.append(process)

            # Wait for this server to be ready
            print(f"Waiting for server on port {server['port']}...")
            if not is_server_ready(server['port'], timeout=args.timeout):
                raise RuntimeError(f"Server failed to start on port {server['port']} within {args.timeout}s")
            if process.poll() is not None:
                raise RuntimeError('Server shell exited; use a foreground command without daemonization')

            print(f"Server ready on port {server['port']}")

        print(f"\nAll {len(servers)} server(s) ready")

        # Run the command
        print(f"Running: {' '.join(args.command)}\n")
        result = subprocess.run(args.command)
        sys.exit(result.returncode)

    finally:
        # Clean up all servers
        print(f"\nStopping {len(server_processes)} server(s)...")
        cleanup_errors = []
        for i, process in enumerate(server_processes):
            try:
                stop_server(process)
                deadline = time.monotonic() + 5
                while port_open(servers[i]['port']) and time.monotonic() < deadline:
                    time.sleep(0.1)
                if port_open(servers[i]['port']):
                    raise RuntimeError('Server port remains open; inspect its owner before continuing')
                print(f"Server {i+1} stopped")
            except Exception as error:
                cleanup_errors.append(f"Server {i+1}: {error}")
        for log in server_logs:
            log.close()
        if cleanup_errors:
            raise RuntimeError('; '.join(cleanup_errors))
        print("All managed foreground servers stopped")


if __name__ == '__main__':
    main()
