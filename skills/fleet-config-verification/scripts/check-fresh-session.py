#!/usr/bin/env python3
"""check-fresh-session.py — validate a fresh-session probe. READ ONLY.

A script cannot open a fresh agent session by itself. The procedure (in
SKILL.md) is: open a fresh agent session in a visible Herdr pane on the
target machine, ask it to state the model it is running on, capture its
verbatim reply, then run this validator against that reply.

Usage:
  python3 check-fresh-session.py --machine prawn-l390 --pane t1h --agent agy \
    --expected-model deepseek/deepseek-v4-pro \
    --reported-model deepseek/deepseek-v4-pro
  python3 check-fresh-session.py --probe-file probe.json
Probe file keys: machine, pane, agent, expected_model, reported_model.
Emits one JSON line, type "fresh-session": pass if reported == expected,
fail if different, unavailable if either side is missing. A file-check-only
report never claims runtime proof — this record is the runtime proof, and
it is labelled fresh-session, never file.
"""
import argparse
import json
import os
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--machine", default="")
ap.add_argument("--pane", default="")
ap.add_argument("--agent", default="")
ap.add_argument("--expected-model", default="")
ap.add_argument("--reported-model", default="")
ap.add_argument("--probe-file", default="")
a = ap.parse_args()

if a.probe_file:
    try:
        with open(a.probe_file, encoding="utf-8") as f:
            p = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(json.dumps({
            "machine": a.machine or os.environ.get("MACHINE", ""),
            "check": "fresh-session", "field": "fresh_session_model",
            "type": "fresh-session", "status": "unavailable",
            "evidence": "probe file unreadable: %s: %s" % (a.probe_file, e),
            "value": None,
        }))
        sys.exit(0)
    a.machine = a.machine or p.get("machine", "")
    a.pane = a.pane or p.get("pane", "")
    a.agent = a.agent or p.get("agent", "")
    a.expected_model = a.expected_model or p.get("expected_model", "")
    a.reported_model = a.reported_model or p.get("reported_model", "")

machine = a.machine or os.environ.get("MACHINE", "")
if not a.expected_model or not a.reported_model:
    status, evidence = "unavailable", (
        "fresh session probe incomplete: expected=%s reported=%s pane=%s agent=%s"
        % (a.expected_model or "missing", a.reported_model or "missing",
           a.pane or "missing", a.agent or "missing"))
elif a.reported_model.strip() == a.expected_model.strip():
    status, evidence = "pass", (
        "fresh session on %s pane=%s agent=%s runs %s as expected"
        % (machine, a.pane, a.agent, a.reported_model.strip()))
else:
    status, evidence = "fail", (
        "fresh session on %s pane=%s agent=%s runs %s, expected %s — fallthrough, reopen scope"
        % (machine, a.pane, a.agent, a.reported_model.strip(), a.expected_model.strip()))

print(json.dumps({
    "machine": machine, "check": "fresh-session", "field": "fresh_session_model",
    "type": "fresh-session", "status": status, "evidence": evidence,
    "value": a.reported_model.strip() or None,
}))
sys.exit(0)
