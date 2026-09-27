---
name: python-testing
description: >-
  Design and repair Python tests using the project's unittest or pytest setup.
  Use for Python fixtures, parametrization, mocks, async tests, boundary cases,
  regression tests and test isolation. Preserve coursework and framework rules.
license: MIT
metadata:
  author: Local setup, adapted from ECC
  version: "1.0.0"
  platform: Windows, macOS, Linux
---

# Python Testing

Test observable behavior with independent expectations and isolated fixtures.

## When to use

Use for Python test design, failures, coverage gaps or test infrastructure.
Use `python-sdk` for inference.sh integration and `systematic-debugging` to
investigate a failure before guessing at a fix. This skill does not require
converting an existing unittest suite to pytest.

## Workflow

1. Read the assignment/specification and permitted-edit boundaries first.
   Inspect the existing test runner, config, supported Python versions and CI.
   Preserve public APIs and deliverable boundaries, especially for coursework.
2. Map each changed requirement to inputs and independently expected results.
   Include boundary values, invalid inputs and interactions that can change the
   result. Do not derive the oracle by copying the implementation under test.
3. For a bug, reproduce it with a failing assertion when practical; verify the
   test fails for the intended behavior, not an import/configuration error.
   For new behavior use a short red/green/refactor cycle. Match effort to risk;
   do not add tests for a harmless prose edit or chase an arbitrary percentage.
4. Reuse the repo's unittest or pytest facilities. Use temporary directories,
   injected clocks and deterministic inputs. Close files before reopening on
   Windows; use pathlib and paths containing spaces in file-tool tests.
5. Mock only external boundaries. Patch where the symbol is looked up. Check
   observable results as well as relevant calls; avoid mocking the code whose
   behavior is the subject of the test. Separate real integration tests clearly.
6. Run focused tests, inspect collected/skipped counts and exit status, then
   run the broader suite required by the project. Report platform-specific
   skips. Passing mocks do not establish live API or database correctness.

## Runner selection

| Existing project | Starting command, adjusted to its configuration |
|---|---|
| unittest | `python -m unittest discover -s tests -v` |
| pytest | `python -m pytest` |
| uv-managed project | Use its documented `uv run` test command |
| Restricted assignment | Use only the assignment's allowed runner and files |

These commands run in the target project, not this skill folder. Check required
plugins before adding plugin-only flags. Do not install or upgrade packages just
because an example mentions them. Coverage targets come from project policy;
coverage measures exercised code, not correctness or hidden-test completeness.

## Patterns and verification

Read [testing patterns](references/patterns.md) for fixtures, mocks and async
boundaries. The small [stdlib example](examples/test_port_contract.py) is
self-contained and can be run using its absolute path with `python`; it touches
only temporary files. It illustrates testing style, not a production port parser.

Use `verification-loop` to report final evidence. Load optional companions
through `skill-router` if they are absent from the daily installation.

## Provenance

Adapted from [ECC python-testing](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/python-testing/SKILL.md).
See [MIT notice](LICENSE.txt). Local adaptation adds unittest/coursework support,
Windows file behavior and independent oracles; removes blanket coverage mandates.
