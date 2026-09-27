# Python test patterns

Choose the project's existing runner. These fragments are patterns to adapt;
names such as `client` and `service` represent the target project's own objects.

## Inputs and boundaries

Write a small table of inputs and literal expected values before touching the
implementation. Exercise both sides of each boundary and representative
interactions. Separate equivalence classes rather than generating thousands of
redundant examples. Property-based testing is useful when the project already
supports it or the input domain warrants it; keep seed/reproduction evidence.

For unittest, use `subTest` for a readable case matrix. For pytest, use
`pytest.mark.parametrize` with case IDs. Both should assert results independently
of the production algorithm. Keep test data separate from the expected-result
calculation when evaluating numerical logic.

## Fixture lifetime

- unittest: pair `TemporaryDirectory` with `addCleanup`, or use a context manager.
- pytest: prefer `tmp_path`, function-scoped fixtures and `monkeypatch` cleanup.
- Scope expensive shared resources only when state resets are explicit.
- Database tests need a disposable database and proven isolation. A transaction
  fixture is insufficient if production code commits outside that transaction.
- Do not disable warnings globally to make test output look clean.

## External calls and errors

Patch the imported name in the consumer module, use `autospec` when practical,
and assert the result/error seen by the caller. Test unavailable dependencies,
timeouts and malformed responses as well as success. Never make a live paid API
call from a unit test or read credentials from the developer's real home folder.

For subprocesses, pass an argument array with `shell=False`, set a timeout and
assert the exit code plus relevant output. For a CLI path test, include spaces
in both the executable argument's input path and the working directory.

## Async

Use `unittest.IsolatedAsyncioTestCase` when staying in the stdlib. If pytest uses
pytest-asyncio strict mode, async fixtures need `pytest_asyncio.fixture`; merely
decorating an async fixture with `pytest.fixture` is not equivalent in all modes.
Check the project's plugin version and mode. Await async assertions and use
`AsyncMock` for async boundaries, with `assert_awaited_once_with` where useful.

## Reading results

Capture collection failures, unexpected skips and the process exit code. A zero
coverage percentage from the wrong source path is a configuration problem; a
high percentage cannot prove the assertions detect incorrect behavior. When
assessing test quality, introduce a small, deliberate fault in a disposable
fixture and confirm the relevant assertion detects it. Never mutate a user's
working implementation solely to inflate a mutation score.

Current references: [unittest](https://docs.python.org/3/library/unittest.html),
[pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html),
[pytest-asyncio modes](https://pytest-asyncio.readthedocs.io/en/stable/concepts.html).
