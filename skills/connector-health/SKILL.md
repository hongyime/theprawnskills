---
name: connector-health
description: >-
  When to read: 'check connector health', 'which connectors need re-login',
  'is Gmail still connected', or a digest flags a connector. Use for: running
  the live connector health check, reading per-connector state, and telling
  Bryan which connectors need re-login and how to re-auth each. Does: runs
  ~/workspace/connector-health/check_connectors.sh, reads state.json, and
  reports OK / NEEDS_RELOGIN / UNKNOWN per connector with the reconnect command.
license: MIT
metadata:
  author: Local setup
  version: "1.0.0"
  platform: "Codex, Antigravity (agy), OpenCode, Muse on Windows, macOS, Linux (Debian)"
---

# Connector Health

Check every connected connector's live auth state. Never trust the app's
"Connected" flag: the Canva incident (2026-11-07) showed the app card saying
Connected while the CLI returned `reauthorization_required` with a dead
refresh token. Connected and authenticated are different things — verify
live, per connector, with that connector's own status command.

## Run the check

```bash
bash ~/workspace/connector-health/check_connectors.sh
```

Read-only. Nothing here connects, disconnects, re-authenticates, or changes
any state. Each probe is non-interactive with a 20s timeout (30s for
Telegram sessions).

- Exit 0 = zero connectors NEEDS_RELOGIN. Exit 2 = at least one
  NEEDS_RELOGIN. Exit 1 = script error.
- Stdout: one line per connector —
  `OK <id>`, `NEEDS_RELOGIN <id> <hint>`, `UNKNOWN <id> <reason>`.
- The script rewrites `~/workspace/connector-health/state.json` on every
  run: per-connector `state` (`connected` / `needs_relogin` / `unknown`),
  `probed_at_sgt`, and `last_known_good` (the last run that reported OK).

Read `state.json` for the last probe; re-run the script for a live verdict.
Never report health from a stale state file. The daily cron
`connector-health-check` runs ~08:06 SGT and alerts Daily Digests with
connectors needing re-login; silent when healthy.

## How each connector is probed

The script in `~/workspace/connector-health/check_connectors.sh` is the
reference — read it, do not re-derive the probe list from memory:

- Google Workspace (`hatch_gws_cli <resource> status`): gmail, calendar,
  docs, drive, sheets, slides, contacts, tasks, forms.
- MCP / OAuth CLIs (`<cli> status`): canva, dropbox, github, notion, slack,
  spotify, zoom, vercel, shopify, opentable, grab_mcp, lovable, replit,
  figma, granola, onepassword.
- Social, no status subcommand (a cheap read-only call proves auth):
  instagram / instagram_messages / threads via `accounts`; facebook via
  `me` (identity = linked, `{}` = not); messenger via `check`;
  threads_messages via `inbox` with the account id from `threads-cli
  accounts`.
- Special cases: meta_ads — verdict from the output file's top-level
  `auth_status`, never from grepping the 1.1 MB catalogue (its tool
  descriptions mention "not_connected" in prose). tailscale — `status`
  prints "Connected" when enrolled. flightaware — `ok:true` plus
  `status:available`. outlook — `--status` returns `status:connected` plus
  `disconnect_url` when linked, a top-level `connect_url` when not.
- Telegram sessions (5): connect + `get_me` per session via the digest's
  read-only reader (`~/workspace/telegram/read_messages.py`, never sends,
  never re-authenticates). `tg_osint` @valerieleqq, `tg_osint_2`
  @bryanseah234 (Bryan's), `tg_osint_3` @shotsbyseah234 (Bryan's),
  `tg_osint_5` @txuanning (not Bryan's), `tg_osint_6` @patrickschen.
- No verifiable live check — always UNKNOWN, never assumed OK:
  apple_healthkit, google_health_connect, ticketmaster, places, shop-pay,
  shopify-ucp, stripe-link, custom.legacy-gemini.

## Classification rules (learned the hard way)

- Re-login signals are checked FIRST. Some CLIs return `ok:true` alongside
  `status:not_connected` (1Password) — `ok:true` alone never means OK.
- When output is JSON, the top-level `status` / `auth_status` field
  decides; free-text patterns are only a fallback. Bare grep over a big
  output false-positives (meta_ads, 2026-11-07).
- Outlook: never grep for the bare string `connect_url` — `disconnect_url`
  contains it as a substring and false-positives every connected account.

## Reporting a NEEDS_RELOGIN

The hint on the `NEEDS_RELOGIN` line carries the reconnect command
(`authorize-url` / `connect-url` / the GWS status command that returns a
`connect_url`). Report it verbatim with the connector id.

Re-authentication is Bryan-owned: the agent reports which connectors need
it and the exact command or URL; it never re-authenticates itself. A
connector that needs re-login stays NEEDS_RELOGIN in every report until a
fresh probe says OK — never clear it on a promise.

## Special cases

- **Stripe is one item**: NEEDS_RELOGIN until BOTH re-login works AND the
  keys are vaulted in the Secure Vault. Vaulting is Bryan-owned and not
  machine-checkable: the marker file
  `~/workspace/connector-health/stripe-keys-vaulted` is created ONLY when
  Bryan confirms the keys are in the vault. Stripe NEEDS_RELOGIN since
  2026-11-22.
- **Telegram session 5 (@txuanning)**: NEEDS_RELOGIN; re-auth is
  Bryan-owned, see `~/workspace/osint/tg_auth.py`. It is not Bryan's
  account — label non-Bryan sessions with the owning account, never frame
  them as Bryan's. Same identity rule as the digest: an account is his
  iff its username contains 'bryan' or 'seah'.
- **UNKNOWN is not OK and not NEEDS_RELOGIN.** Report it as unproven with
  the reason (timed out, empty output, unclear status). Never claim a
  connector healthy on an UNKNOWN.

## Report format

Per check, one line per connector that is not OK, then the counts:

```text
Connector health — <date> <time> SGT (probed <probed_at_sgt>)
- NEEDS_RELOGIN — <id>: <hint verbatim>
- UNKNOWN — <id>: <reason>
Connected: <n>/<total> · NEEDS_RELOGIN: <n> · UNKNOWN: <n>
```

Zero NEEDS_RELOGIN = silent (cron discipline); only report when something
needs Bryan.
