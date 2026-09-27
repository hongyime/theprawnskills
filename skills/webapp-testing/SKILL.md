---
name: webapp-testing
description: >-
  Verify web applications in a real browser with Playwright: user flows, layout,
  screenshots, logs, CI artifacts and flaky-test diagnosis. Use for browser
  testing and end-to-end flows; use react-testing for isolated component tests.
license: Complete terms in LICENSE.txt; ECC-derived guidance also carries ECC-LICENSE.txt
---

# Web Application Testing

Verify the user's intended flow with browser evidence and explicit readiness.

## Choose the existing test surface

Read repository instructions, package scripts and test configuration first.
Use the project's existing Playwright/Cypress suite for persistent tests.
Use a small Python Playwright script for an isolated browser check when suitable;
do not replace an established TypeScript suite with a second Python framework.
Use `react-testing` for component behavior that does not need a real browser.

## Workflow

1. Identify the requirement, target URL/environment, test data and expected final
   state. Use isolated test accounts and data; do not submit payments, messages
   or destructive actions against a live service as an incidental test.
2. Establish server readiness. If the app is already running, reuse it. The
   bundled [server helper](scripts/with_server.py) can start one or more servers;
   run it with `--help` first. It checks ports, which does not prove the app
   has hydrated or its dependencies are working.
3. Navigate, then assert a meaningful app-specific locator or response. Do not
   use `networkidle` or arbitrary sleeps as a universal readiness condition:
   polling and streaming apps may never become idle.
4. Inspect the rendered DOM, choose accessible roles/names, then perform the
   user's action. Use locator auto-waiting and retrying assertions. Arm response
   waits before triggering the action to avoid missing a fast response.
5. Assert the resulting user-visible state and relevant API/data outcome.
   Distinguish mocked responses from real integration evidence. A screenshot
   alone cannot prove a save reached the database.
6. Capture failure artifacts and report the process result. Use the suite's
   configured runner/CI rather than assuming every host provides named agents
   or slash commands. Close browser contexts and processes in cleanup paths.

## Portable helper invocation

Resolve `$skillDir` to this loaded skill's directory, independently of the
target project's working directory. Resolve `$testScript` to your actual test.

```powershell
python (Join-Path $skillDir 'scripts/with_server.py') --help
python (Join-Path $skillDir 'scripts/with_server.py') --server "npm run dev" --port 5173 -- python $testScript
```

Run from the target project so its npm script resolves correctly. The server
must stay in the foreground: no daemon, detached process or background launch.
The helper refuses occupied ports and checks that its ports close after cleanup.
Use an existing server directly when another process owns its lifecycle.
Its command is shell-executed by the helper: use a trusted command, never
interpolate untrusted input. The server command uses `cmd.exe` on Windows and
`/bin/sh` on POSIX, regardless of the terminal that launched Python. The helper
requires Python and the standard POSIX `ps` utility on macOS/Linux; browser
scripts additionally require Playwright and its browser
runtime. Report missing prerequisites; do not claim a browser check ran.

On POSIX, resolve `skill_dir` and `test_script` to their real paths, then use:

```bash
python3 "$skill_dir/scripts/with_server.py" --server "npm run dev" --port 5173 -- python3 "$test_script"
```

## Stable suites and CI

Read [suite and artifact guidance](references/suites-and-artifacts.md) for
fixtures, CI lifecycle, traces, retries and reporting. Reuse providers/test data
rather than sharing mutable state between cases. Keep failures and quarantined
tests visible. A retry pass is flaky evidence, not the same as a clean first pass.

## Bundled examples

These scripts take explicit inputs, support `--help`, and write to a selected
output folder. They are examples for isolated environments, not a complete app
test suite. Install browser prerequisites only within the authorized task.

- [Discover page elements](examples/element_discovery.py): requires a URL and an
  app-ready selector; captures the DOM's elements and a screenshot.
- [Capture a flow's console messages](examples/console_logging.py): requires the
  initial-ready selector, link name to click and resulting-state selector.
- [Inspect local HTML](examples/static_html_automation.py): uses a correct file
  URI and an explicit ready selector, including on Windows paths with spaces.

## Completion and related skills

Report command, environment, exit code, passed/failed/flaky/skipped counts, and
artifact paths. A hanging process or a test skipped because its prerequisite is
absent remains incomplete. Use `verification-loop` for overall completion,
`systematic-debugging` for failures, and `skill-router` for on-demand companions.

## Attribution

Original Apache-2.0 notice remains in [LICENSE.txt](LICENSE.txt). Suite/artifact
guidance is adapted from [ECC e2e-testing](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/e2e-testing/SKILL.md);
its [MIT notice](ECC-LICENSE.txt) is retained. Examples are locally revised.
