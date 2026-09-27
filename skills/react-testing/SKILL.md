---
name: react-testing
description: >-
  Write and repair React component and hook tests with Testing Library and the
  project's Jest or Vitest runner. Use for form behavior, async state, network
  mocks, accessible queries, and deciding between component and browser tests.
license: MIT
metadata:
  author: Local setup, adapted from ECC
  version: "1.0.0"
  platform: Windows, macOS, Linux
---

# React Testing

Assert what users can observe, using the test stack the project already owns.

## When to use

Use for component, hook and form behavior tests. Use `react-dev` for implementation
and `webapp-testing` for real layout, navigation and complete browser flows.
Do not switch Jest to Vitest or install a second runner merely to use this guide.

## Workflow

1. Read the component's contract and repo test configuration. Identify the
   existing runner, DOM environment, setup file, providers and network mocks.
   Preserve project and coursework boundaries. Server components/framework-only
   behavior may require the framework's integration or browser test support.
2. Define observable cases: success, loading, empty, error and invalid input
   where they apply. Write an independent expected result. For a bug, confirm
   the regression test fails for the actual behavior before changing code.
3. Render through real providers with a fresh cache/store per test. Use
   `getByRole` with an accessible name or `getByLabelText`. Use a test ID only
   when semantic queries cannot express the target.
4. Create `userEvent.setup()` per test and await interactions. Use `findBy*`
   for arriving content, `queryBy*` for absence, and `waitFor` for asynchronous
   assertions. Do not put repeated side-effectful clicks inside `waitFor`.
5. Mock HTTP at the network boundary with the existing MSW setup when present;
   fail unexpected requests, reset handlers between tests, and test error
   responses. An injected service fake is also valid for a narrow component
   contract; label it honestly as a fake, not a real integration test.
6. Assert visible results and relevant external effects. Avoid checking private
   state, render counts or calling internal handlers directly. Restore spies,
   timers and global modifications after each test. Treat act warnings as work
   to investigate, not noise to suppress globally.
7. Run the runner in one-shot mode for verification, inspect collection and
   skipped tests, and report the process exit code. Coverage targets follow the
   project; they do not replace behavioral assertions.

## Choose the right boundary

| Behavior | Suitable test |
|---|---|
| Form validation, hook results, loading/error UI | Testing Library with Jest/Vitest |
| Real layout, contrast, scrolling, downloads, native browser behavior | Browser/component tests in a real browser |
| Login through API/database to another page | Isolated full-flow browser integration |

DOM accessibility checks catch some issues; JSDOM does not establish visual
contrast, layout correctness or complete accessibility compliance. Use browser
evidence and relevant manual checks for those requirements.

## References and prerequisites

Read [component test patterns](references/patterns.md). The skill supplies no
named ECC agents, slash commands or installed packages. Check the project's
dependencies before using Testing Library, MSW or an accessibility checker.
Use `skill-router` to resolve `webapp-testing`, `react-dev` and `verification-loop`
from the full library when they are not installed locally.

## Provenance

Adapted from [ECC react-testing](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/react-testing/SKILL.md).
See [MIT notice](LICENSE.txt). Local changes narrow routing, preserve existing
runners, correct accessibility claims and remove ECC-only dependencies.
