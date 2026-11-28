## Migrating from another CAPTCHA

During the Step 6 scan, also look for existing reCAPTCHA or hCaptcha. If found, switch Step 7 to a migration plan.

Detection signals: reCAPTCHA — `https://www.google.com/recaptcha/api.js`, `class="g-recaptcha"`, `data-sitekey="6L..."`, backend POST to `/recaptcha/api/siteverify`; hCaptcha — `https://js.hcaptcha.com/1/api.js`, `class="h-captcha"`, backend POST to `https://hcaptcha.com/siteverify`.

Substitution: as in the frontend-edit contract + Step 9, with Turnstile's script URL, `cf-turnstile` div, `cf-turnstile-response` field, and `challenges.cloudflare.com` siteverify. Drop `RECAPTCHA_SECRET` / `HCAPTCHA_SECRET`; add `TURNSTILE_SECRET`.

Edge cases to surface to the user:
- **reCAPTCHA v3 score thresholds.** Turnstile has no score — migrated code rejects on `success === false`.
- **reCAPTCHA Enterprise.** Don't auto-migrate. Point at [developers.cloudflare.com/turnstile/migration/recaptcha/](https://developers.cloudflare.com/turnstile/migration/recaptcha/).
- **Custom `action=` values.** Preserve any valid custom action passed to `grecaptcha.execute` as `data-action` on the widget; otherwise use the Step 7 action. Validate the returned action in the backend either way.

## Edge cases

Rows here add to the steps above; account-enumeration, multi-account, and token-expiry handling are in Steps 2–3 and not repeated.

| Situation | Action |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cloudflare Pages project | Wire siteverify inside a Pages Function (or the framework equivalent). The Pages Plugin at [developers.cloudflare.com/pages/functions/plugins/turnstile](https://developers.cloudflare.com/pages/functions/plugins/turnstile/) is a shortcut. |
| Cloudflare Workers backend | Use the Step 9 fetch idiom inside the Worker's request handler. `fetch` to `challenges.cloudflare.com` works the same as in Node. |
| `EXPECTED_HOSTNAME` mismatch | Update widget domains via PUT, not PATCH (PATCH returns `10405 Method not allowed`): `curl -X PUT .../widgets/$SITEKEY -d '{"name":"...","mode":"managed","domains":[...]}'` |
| Validation returns `invalid-input-secret` | Secret didn't reach the backend. Re-check `TURNSTILE_SECRET` in the customer's env / secret manager; for Workers, run `wrangler secret list` to confirm the secret is bound to the right script. |
| Validation returns `invalid-input-response` | Expected for a dummy probe token — the secret IS valid. validate.sh treats this as success. |
