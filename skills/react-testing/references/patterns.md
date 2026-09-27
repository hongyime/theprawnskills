# Component test patterns

These examples assume a project's existing React test environment. Adapt names
and imports to it; no global tool install or particular source layout is required.

## Async interactions

```tsx
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

const user = userEvent.setup();
render(<ProfileForm save={saveProfile} />);
await user.type(screen.getByLabelText(/display name/i), "Ada");
await user.click(screen.getByRole("button", { name: /save/i }));
await waitFor(() => expect(screen.getByRole("status")).toHaveTextContent("Saved"));
```

The project's setup must provide DOM matchers such as `toHaveTextContent`.
Use the runner-specific jest-dom entrypoint for Vitest or Jest. `findBy*` retries
the query; an already-present status may still say "Saving". Use `waitFor` to
retry the content assertion, or query text that appears only on completion.

## Network mocks

With MSW v2, use `http` and `HttpResponse`; check installed versions before
copying APIs. Start the test server with `onUnhandledRequest: "error"`, reset
handlers after each test and close it after the suite. Override a handler for a
500 response to check the visible error state. Do not silently allow requests to
real services from a component test. Keep any intentional browser/integration
network scope explicit.

## Provider lifetime and hooks

Create a QueryClient/store once per test, outside a wrapper component's render
body. Disable automatic query retries in tests when validating an immediate
error, then test production retry policy separately. Recreating the cache on
each render can make tests flaky or hide the state being tested.

Use `renderHook` for a hook's public API. Wrap state updates in `act` when they
are not already driven by Testing Library helpers. Assert results rather than
how many times a hook rendered. Test hooks through components when the behavior
depends primarily on user interaction.

## Isolation and honest failure evidence

Prefer fresh state to cleanup that assumes the previous test completed. Restore
console spies in `finally` blocks for intentionally thrown errors; never silence
all console errors across the suite. Keep fake timers scoped and configure
user-event's timer advancement when needed. Do not use arbitrary sleeps to
make flaky tests pass. A quarantined case must remain visible as skipped with
an issue/reason; quarantine is not a successful verification.

Use the project's existing one-shot command: commonly `npm test -- --run` for
a Vitest script or the documented CI command for Jest. Inspect the actual
package script before adding flags; a script may already include `run`.

Sources: [Testing Library queries](https://testing-library.com/docs/queries/about/),
[user-event setup](https://testing-library.com/docs/user-event/setup/),
[MSW Node integration](https://mswjs.io/docs/integrations/node/).
