"""Bound foreground repair commands; detect worktree scope changes, not a sandbox."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import sys
import time


class CleanupError(RuntimeError):
    """The supervisor cannot verify termination of the owned process tree."""


def git(root: Path, *args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(root), *args], stderr=subprocess.PIPE, timeout=30)


def snapshot(root: Path) -> dict[str, str]:
    paths = git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    result = {}
    for raw in paths.split(b"\0"):
        if not raw:
            continue
        name = os.fsdecode(raw)
        path = root / name
        if path.is_symlink():
            data = b"symlink:" + os.fsencode(os.readlink(path))
        elif path.is_file():
            data = path.read_bytes()
        else:
            data = b"missing-or-nonfile"
        mode = stat.S_IMODE(path.lstat().st_mode) if path.exists() or path.is_symlink() else 0
        result[name] = f"{mode:o}:" + hashlib.sha256(data).hexdigest()
    return result


def stop_process(process: subprocess.Popen) -> None:
    failure = None
    if os.name == "nt":
        if process.poll() is None:
            for _ in range(2):
                try:
                    result = subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=45)
                    if result.returncode == 0:
                        failure = None
                        break
                    failure = f"taskkill exited {result.returncode}"
                except (OSError, subprocess.TimeoutExpired) as exc:
                    failure = str(exc)
    else:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        except PermissionError:
            rows = subprocess.check_output(["ps", "-eo", "pgid=,stat="], timeout=10).decode().splitlines()
            if any(len(parts := row.split()) == 2 and parts[0] == str(process.pid)
                   and not parts[1].startswith("Z") for row in rows):
                raise
    try:
        process.wait(timeout=15)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=15)
    if failure is not None:
        raise CleanupError("Process-tree cleanup could not be verified; inspect surviving children: " + failure)


def command(argv: list[str], root: Path, log: Path, seconds: float,
            env: dict[str, str]) -> int:
    with log.open("wb") as output:
        process = subprocess.Popen(argv, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                   stdout=output, stderr=subprocess.STDOUT,
                                   start_new_session=os.name != "nt")
        try:
            return process.wait(timeout=seconds)
        finally:
            # Foreground workers must retain their leader until children finish.
            try:
                stop_process(process)
            except CleanupError:
                raise
            except (OSError, subprocess.SubprocessError) as exc:
                raise CleanupError("Process cleanup failed; inspect surviving children: " + str(exc)) from exc


def run(plan: dict, run_dir: Path) -> dict:
    root = Path(plan["root"]).resolve(strict=True)
    if Path(os.fsdecode(git(root, "rev-parse", "--show-toplevel")).strip()).resolve() != root:
        raise ValueError("root must be the worktree root")
    if root == run_dir or root in run_dir.parents:
        raise ValueError("run directory must be outside the worktree")
    attempts = plan["max_attempts"]
    if type(attempts) is not int or not 1 <= attempts <= 3:
        raise ValueError("max_attempts must be an integer from 1 to 3")
    for key in ("wall_seconds", "command_seconds"):
        if type(plan[key]) not in (int, float) or not 0 < plan[key] <= 86400:
            raise ValueError(f"{key} must be positive and at most 86400")
    for key in ("worker", "verify"):
        if not isinstance(plan[key], list) or not plan[key] or not all(
                isinstance(item, str) and item for item in plan[key]):
            raise ValueError(f"{key} must be a nonempty argument array")
    allowed = plan["allowed_files"]
    if not isinstance(allowed, list) or not allowed:
        raise ValueError("allowed_files must list exact relative file paths")
    for name in allowed:
        path = Path(name)
        if not isinstance(name, str) or path.is_absolute() or ".." in path.parts or ".git" in path.parts:
            raise ValueError("allowed file escapes worktree")
        if not path.parts or (root / path).resolve().is_relative_to(root) is False:
            raise ValueError("allowed file escapes worktree")
    allowed = {Path(name).as_posix() for name in allowed}
    index = git(root, "ls-files", "--stage", "-v", "-z")
    if any(entry.split(b" ", 2)[1:2] == [b"160000"] for entry in index.split(b"\0") if entry):
        raise ValueError("submodules are unsupported; use a separate bounded worktree without gitlinks")
    if git(root, "status", "--porcelain", "--untracked-files=all"):
        raise ValueError("initial worktree must be clean")
    baseline = snapshot(root)
    head = git(root, "rev-parse", "HEAD").strip().decode()
    branch = git(root, "rev-parse", "--symbolic-full-name", "HEAD")
    run_dir.mkdir(mode=0o700, parents=True, exist_ok=False)
    started = time.monotonic()
    state = {"status": "running", "root": str(root), "head": head, "attempts": 0,
             "elapsed_seconds": 0, "changed_files": [], "commands": [], "plan": plan}

    def save() -> None:
        state["elapsed_seconds"] = round(time.monotonic() - started, 3)
        temporary = run_dir / "checkpoint.tmp"
        temporary.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        temporary.replace(run_dir / "checkpoint.json")

    def check_scope() -> dict[str, str]:
        current = snapshot(root)
        changed = sorted(name for name in baseline.keys() | current.keys()
                         if baseline.get(name) != current.get(name))
        state["changed_files"] = changed
        if set(changed) - allowed:
            raise ValueError("scope violation: " + ", ".join(sorted(set(changed) - allowed)))
        if (git(root, "rev-parse", "HEAD").strip().decode() != head
                or git(root, "rev-parse", "--symbolic-full-name", "HEAD") != branch
                or git(root, "ls-files", "--stage", "-v", "-z") != index):
            raise ValueError("HEAD, branch or index changed")
        return current

    def execute(kind: str, number: int) -> tuple[int, Path]:
        remaining = plan["wall_seconds"] - (time.monotonic() - started)
        if remaining <= 0:
            raise TimeoutError("wall-clock budget exhausted")
        log = run_dir / f"{number}-{kind}.log"
        env = dict(os.environ, PRAWN_LOOP_ATTEMPT=str(number),
                   PRAWN_LOOP_FEEDBACK=str(run_dir / f"{max(number - 1, 0)}-verify.log"))
        code = command(plan[kind], root, log, min(remaining, plan["command_seconds"]), env)
        state["commands"].append({"kind": kind, "attempt": number, "exit": code, "log": log.name})
        check_scope()
        save()
        if time.monotonic() - started >= plan["wall_seconds"]:
            raise TimeoutError("wall-clock budget exhausted")
        return code, log

    save()
    try:
        code, log = execute("verify", 0)
        previous = (code, snapshot(root))
        if code == 0:
            state["status"] = "already-passing"
        else:
            for number in range(1, attempts + 1):
                state["attempts"] = number
                save()  # Consume the attempt before launch; interrupted runs retain it.
                code, _ = execute("worker", number)
                if code:
                    state["status"] = "worker-failed"
                    break
                code, log = execute("verify", number)
                if code == 0:
                    state["status"] = "passed"
                    break
                # Conservative progress gate: timing/noise in logs cannot buy retries.
                current = (code, snapshot(root))
                if current == previous:
                    state["status"] = "no-progress"
                    break
                previous = current
            else:
                state["status"] = "attempts-exhausted"
    except CleanupError as exc:
        state.update(status="cleanup-failed", error=str(exc))
    except (subprocess.TimeoutExpired, TimeoutError) as exc:
        state.update(status="timeout", error=str(exc))
    except KeyboardInterrupt:
        state.update(status="cancelled", error="Interrupted; inspect checkpoint before resuming")
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        state.update(status="stopped", error=str(exc))
    finally:
        try:
            check_scope()
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            if state["status"] == "cleanup-failed":
                state["scope_error"] = str(exc)
            else:
                state.update(status="stopped", error=str(exc))
        save()
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    args = parser.parse_args()
    try:
        state = run(json.loads(args.plan.read_text(encoding="utf-8")), args.run_dir.resolve())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"Cannot start: {exc}", file=sys.stderr)
        return 2
    print(json.dumps({key: state[key] for key in ("status", "attempts", "changed_files", "elapsed_seconds")}))
    return 0 if state["status"] in ("passed", "already-passing") else 1


if __name__ == "__main__":
    raise SystemExit(main())
