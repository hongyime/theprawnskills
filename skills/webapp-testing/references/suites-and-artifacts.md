# Stable suites and useful evidence

## Project organization

Follow the current project. Group persistent browser cases by feature/flow,
keep authentication and seed data in fixtures, and use page objects only when
they reduce repeated interaction logic. Keep assertions visible in tests.
Use a fresh browser context and isolated data for each independent case.

## Readiness and response races

Prefer assertions on an app-ready heading, control or known state. A port check
and DOMContentLoaded only establish narrower readiness. Long polling or a
streaming connection makes network-idle waits unsuitable as universal gates.

For Python Playwright, register the response wait before the triggering action:

```python
with page.expect_response(lambda response: "/api/save" in response.url) as pending:
    page.get_by_role("button", name="Save", exact=True).click()
assert pending.value.ok
expect(page.get_by_role("status")).to_have_text("Saved")
```

Match method/status/path carefully in real tests. In Playwright Test, create the
waitForResponse promise before clicking, then await it and the visible result.

## CI artifacts

Use the current runner's config. For Playwright Test, useful options include
`forbidOnly` in CI, a bounded retry policy, screenshots on failure, video retained
on failure and traces on the first retry or retained on failure. Reuse a running
server only when the environment guarantees it is the intended application.

Upload reports/artifacts even when tests fail, using the repo's action/version
policy. Limit retention to what review needs. Traces, screenshots, storage state
and logs can contain session tokens or personal data; do not commit them into
the shared skill library or publish them without review.

For Python Playwright, use `context.tracing.start(screenshots=True, snapshots=True)`
and `context.tracing.stop(path=...)` for a Playwright trace. Browser-level Chromium
tracing is a different facility. Artifact capture must not swallow the test's
original failure or turn its exit status into success.

## Flakes and completion

Investigate races, shared state and external dependencies before adding retries.
Quarantine only with a visible reason/issue and retained failure evidence. Report
passed on first attempt, passed after retry, failed and skipped separately.
Wait for the runner to exit; printed successes before a shutdown hang do not
prove the complete suite passed. Repeat tests only to investigate suspected
flakiness or verify a relevant change, not on an arbitrary schedule.

Sources: [Playwright assertions](https://playwright.dev/docs/test-assertions),
[traces](https://playwright.dev/docs/trace-viewer-intro),
[CI](https://playwright.dev/docs/ci), and
[ECC e2e-testing](https://github.com/affaan-m/ECC/blob/e482e579415fde18357cafce70f177ae19fd7f03/skills/e2e-testing/SKILL.md).
