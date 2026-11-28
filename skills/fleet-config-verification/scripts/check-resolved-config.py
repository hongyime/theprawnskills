#!/usr/bin/env python3
"""check-resolved-config.py — live resolved configuration. READ ONLY.

Usage (piped to the target, never ssh 'a; b'):
  cat check-resolved-config.py | <host>-ssh 'python3 -'
  EXPECTED_HOST=<hostname> MACHINE=<label> python3 check-resolved-config.py
Env: EXPECTED_HOST (required for identity), MACHINE (label, default hostname).
Emits JSON lines: machine, check, field, type, status, evidence, value.
Type is always "resolved". Status: pass | fail | unproven | not-covered | unavailable.
Only allow-listed fields are emitted — never file contents, never secrets.
No dump subcommand exists for codex or opencode, so "resolved" here means:
the tool's own config files parsed for the fields it actually resolves,
plus the codex models catalog (live, with fetched_at).
"""
import json
import os
import re
import socket
import subprocess
import sys

MACHINE = os.environ.get("MACHINE") or socket.gethostname()
EXPECTED_HOST = os.environ.get("EXPECTED_HOST", "")
HOSTNAME = socket.gethostname()
ID_OK = bool(EXPECTED_HOST) and HOSTNAME == EXPECTED_HOST


def st(s):
    return s if ID_OK else "unproven"


def emit(check, field, status, evidence, value=None):
    print(json.dumps({
        "machine": MACHINE, "check": check, "field": field,
        "type": "resolved", "status": st(status),
        "evidence": evidence, "value": value,
    }))


def strip_jsonc(text):
    """Remove // and /* */ comments outside string literals."""
    out, i, n = [], 0, len(text)
    in_str, esc = False, False
    while i < n:
        c = text[i]
        if in_str:
            out.append(c)
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
            i += 1
            continue
        if c == '"':
            in_str = True
            out.append(c)
            i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            while i < n and text[i] != "\n":
                i += 1
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            i += 2
            while i + 1 < n and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        out.append(c)
        i += 1
    s = "".join(out)
    s = re.sub(r",\s*([}\]])", r"\1", s)  # trailing commas
    return s


def load_jsonc(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(strip_jsonc(f.read()))


def tailscale_ip():
    try:
        r = subprocess.run(["tailscale", "ip", "-4"], capture_output=True,
                           text=True, timeout=10)
        ip = r.stdout.strip().splitlines()
        return ip[0] if ip else "UNAVAILABLE"
    except Exception:
        return "UNAVAILABLE"


emit("host-identity", "hostname", "pass" if ID_OK else "unproven",
     "hostname=%s tailscale_ip=%s expected_host=%s"
     % (HOSTNAME, tailscale_ip(), EXPECTED_HOST or "unset"), HOSTNAME)

# --- Codex: config.toml + live models catalog ---
codex_cfg = os.path.expanduser("~/.codex/config.toml")
model, reasoning = None, None
if os.path.isfile(codex_cfg):
    with open(codex_cfg, encoding="utf-8", errors="replace") as f:
        for line in f:
            m = re.match(r'^\s*model\s*=\s*"([^"]+)"', line)
            if m:
                model = m.group(1)
            m = re.match(r'^\s*model_reasoning_effort\s*=\s*"([^"]+)"', line)
            if m:
                reasoning = m.group(1)
    emit("resolved", "codex.model", "pass" if model else "unavailable",
         "codex config model=%s" % model, model)
    emit("resolved", "codex.reasoning", "pass" if reasoning else "unavailable",
         "codex config reasoning=%s" % reasoning, reasoning)
else:
    emit("resolved", "codex.model", "not-covered", "codex config.toml missing", None)
    emit("resolved", "codex.reasoning", "not-covered", "codex config.toml missing", None)

cache = os.path.expanduser("~/.codex/models_cache.json")
if os.path.isfile(cache):
    try:
        d = json.load(open(cache, encoding="utf-8"))
        slugs = sorted(m.get("slug") for m in d.get("models", []) if m.get("slug"))
        emit("resolved", "codex.catalog_slugs", "pass",
             "models_cache slugs=%s fetched_at=%s" % (",".join(slugs), d.get("fetched_at")),
             ",".join(slugs))
        if model:
            emit("resolved", "codex.model_in_catalog",
                 "pass" if model in slugs else "fail",
                 "configured model %s in live catalog: %s" % (model, model in slugs),
                 str(model in slugs))
    except Exception as e:
        emit("resolved", "codex.catalog_slugs", "unavailable",
             "models_cache.json unreadable: %s" % e, None)
else:
    emit("resolved", "codex.catalog_slugs", "not-covered",
         "models_cache.json missing (path not verified on this machine)", None)

# --- opencode: opencode.jsonc + model-fallback.json ---
oc = os.path.expanduser("~/.config/opencode/opencode.jsonc")
if os.path.isfile(oc):
    try:
        c = load_jsonc(oc)
        emit("resolved", "opencode.model", "pass",
             "opencode model=%s" % c.get("model"), c.get("model"))
        emit("resolved", "opencode.small_model", "pass",
             "opencode small_model=%s" % c.get("small_model"), c.get("small_model"))
        dp = c.get("disabled_providers") or []
        emit("resolved", "opencode.disabled_providers", "pass",
             "disabled_providers=%s" % ",".join(dp), ",".join(sorted(dp)))
        providers = c.get("provider") or {}
        emit("resolved", "opencode.provider_models", "pass",
             "provider models=%s" % json.dumps(
                 {k: sorted(v.get("models", {}).keys()) for k, v in providers.items()}),
             None)
        agents = c.get("agent") or {}
        models = [a.get("model") for a in agents.values() if a.get("model")]
        deep = sum(1 for m in models if m and m.startswith("deepseek/"))
        other = sorted(set(m for m in models if m and not m.startswith("deepseek/")))
        emit("resolved", "opencode.primary_slots", "pass",
             "agent slots=%d deepseek=%d other=%s" % (len(models), deep, ",".join(other) or "none"),
             "%d/%d" % (deep, len(models)))
        emit("resolved", "opencode.primary_other_models", "pass" if not other else "fail",
             "non-deepseek primary models=%s" % (",".join(other) or "none"),
             ",".join(other) or "none")
    except Exception as e:
        emit("resolved", "opencode.model", "unavailable",
             "opencode.jsonc unreadable: %s" % e, None)
else:
    for f in ("opencode.model", "opencode.small_model",
              "opencode.disabled_providers", "opencode.provider_models",
              "opencode.primary_slots", "opencode.primary_other_models"):
        emit("resolved", f, "not-covered", "opencode.jsonc missing (opencode not installed)", None)

fb = os.path.expanduser("~/.config/opencode/model-fallback.json")
if os.path.isfile(fb):
    try:
        d = json.load(open(fb, encoding="utf-8"))
        agents = d.get("agents", {})
        all_fb = set()
        for a in agents.values():
            all_fb.update(a.get("fallbackModels") or [])
        defaults = d.get("defaults", {})
        emit("resolved", "opencode.fallback_enabled", "pass",
             "fallback enabled=%s" % d.get("enabled"), str(d.get("enabled")))
        emit("resolved", "opencode.fallback_models", "pass",
             "fallback models=%s" % ",".join(sorted(all_fb)), ",".join(sorted(all_fb)))
        emit("resolved", "opencode.fallback_depth", "pass",
             "maxFallbackDepth=%s" % defaults.get("maxFallbackDepth"),
             str(defaults.get("maxFallbackDepth")))
        emit("resolved", "opencode.fallback_triggers", "pass",
             "fallbackOn=%s" % ",".join(defaults.get("fallbackOn") or []),
             ",".join(defaults.get("fallbackOn") or []))
        other_fb = sorted(m for m in all_fb if not m.startswith("opencode/deepseek"))
        emit("resolved", "opencode.fallback_other_models", "pass",
             "non-deepseek fallback models=%s" % (",".join(other_fb) or "none"),
             ",".join(other_fb) or "none")
    except Exception as e:
        emit("resolved", "opencode.fallback_models", "unavailable",
             "model-fallback.json unreadable: %s" % e, None)
else:
    emit("resolved", "opencode.fallback_models", "not-covered",
         "model-fallback.json missing", None)

# --- omo.jsonc: models / fallback_models / disabled_providers (union across blocks) ---
omo = os.path.expanduser("~/.omo/omo.jsonc")
if os.path.isfile(omo):
    try:
        d = load_jsonc(omo)

        def collect(obj, key, acc):
            if isinstance(obj, dict):
                if isinstance(obj.get(key), list):
                    acc.update(str(x) for x in obj[key])
                for v in obj.values():
                    collect(v, key, acc)
            elif isinstance(obj, list):
                for v in obj:
                    collect(v, key, acc)

        models, fallbacks, disabled = set(), set(), set()
        collect(d, "models", models)
        collect(d, "fallback_models", fallbacks)
        collect(d, "disabled_providers", disabled)
        emit("resolved", "omo.models", "pass",
             "omo models=%s" % ",".join(sorted(models)), ",".join(sorted(models)))
        emit("resolved", "omo.fallback_models", "pass",
             "omo fallback_models=%s" % ",".join(sorted(fallbacks)), ",".join(sorted(fallbacks)))
        emit("resolved", "omo.disabled_providers", "pass",
             "omo disabled_providers=%s" % ",".join(sorted(disabled)), ",".join(sorted(disabled)))
    except Exception as e:
        emit("resolved", "omo.models", "unavailable",
             "omo.jsonc unreadable: %s" % e, None)
else:
    for f in ("omo.models", "omo.fallback_models", "omo.disabled_providers"):
        emit("resolved", f, "not-covered", "omo.jsonc missing", None)
