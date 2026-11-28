#!/usr/bin/env python3
"""diff-reports.py — cross-machine diff + expected-value check. READ ONLY.

Usage:
  python3 diff-reports.py [--expected expected.json] vm.jsonl l390.jsonl 3410.jsonl t14.jsonl e14.jsonl
Each input file holds one machine's JSONL records (from the check-*.sh/.ps1 scripts).
Groups records by (check, field). For each group with a comparable "value":
  - baseline = most common value; outliers = machines whose value differs.
  - emits one diff record per group: status fail if outliers exist, else pass.
With --expected (JSON object keyed "check.field" -> expected string):
  - emits one expected record per matching record: pass if value == expected else fail.
Ends with one summary record:
  - verdict "no changes detected by these checks" when 0 diffs and 0 fails
    (V5: a zero-change re-run is never proof the fleet is correct), else
    "differences found: N fields".
Never averages a difference away; one machine's result is never fleet proof.
"""
import argparse
import collections
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("--expected", default="")
ap.add_argument("files", nargs="+")
a = ap.parse_args()

expected = {}
if a.expected:
    with open(a.expected, encoding="utf-8") as f:
        expected = json.load(f)

records = []
for path in a.files:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

machines = sorted({r.get("machine") for r in records if r.get("machine")})
groups = collections.defaultdict(list)
for r in records:
    groups[(r.get("check"), r.get("field"))].append(r)

diffs = 0
fails = 0
skipped = 0
not_covered = sorted({(r["machine"], r["check"], r["field"]) for r in records
                      if r.get("status") == "not-covered"})
unproven = sorted({(r["machine"], r["check"], r["field"]) for r in records
                   if r.get("status") == "unproven"})

# Fields that must never be cross-machine diffed: identity (unique per
# machine by definition), live Herdr state (viewpoint- and minute-dependent),
# and per-repo git records (each machine has different repos). Their
# individual pass/fail records still count in the summary.
NON_COMPARABLE = {
    ("host-identity", "hostname"), ("host-identity", "tailscale_ip"),
    ("herdr", "machines_connected"), ("herdr", "terminal"),
    ("herdr", "terminals_live"),
    ("git", "repo_identity"), ("git", "repo_drift"), ("git", "repo_sweep"),
}

for (check, field), rs in sorted(groups.items(), key=lambda kv: (kv[0][0], kv[0][1])):
    if (check, field) in NON_COMPARABLE:
        skipped += 1
        continue
    vals = {r.get("machine"): r.get("value") for r in rs if r.get("value") is not None}
    if len(vals) < 2:
        continue
    counts = collections.Counter(vals.values())
    baseline, _ = counts.most_common(1)[0]
    outliers = sorted(m for m, v in vals.items() if v != baseline)
    status = "fail" if outliers else "pass"
    if outliers:
        diffs += 1
    print(json.dumps({
        "machine": "*", "check": check, "field": field, "type": "diff",
        "status": status,
        "evidence": "values=%s baseline=%s outliers=%s"
                    % (json.dumps(vals, sort_keys=True), baseline, ",".join(outliers) or "none"),
        "value": baseline,
    }))
    key = "%s.%s" % (check, field)
    if key in expected:
        for r in rs:
            if r.get("value") is None:
                continue
            ok = str(r["value"]) == str(expected[key])
            if not ok:
                fails += 1
            print(json.dumps({
                "machine": r["machine"], "check": check, "field": field,
                "type": "expected", "status": "pass" if ok else "fail",
                "evidence": "machine=%s value=%s expected=%s"
                            % (r["machine"], r["value"], expected[key]),
                "value": r.get("value"),
            }))

fails += len({(r["machine"], r["check"], r["field"], str(r.get("value")))
                for r in records if r.get("status") == "fail"})
verdict = ("no changes detected by these checks"
           if diffs == 0 else "differences found: %d fields" % diffs)
if diffs == 0 and fails:
    verdict += "; %d fail record(s) remain" % fails
print(json.dumps({
    "machine": "*", "check": "summary", "field": "fleet",
    "type": "diff", "status": "pass" if diffs == 0 and fails == 0 else "fail",
    "evidence": ("machines=%s records=%d diff_fields=%d fail_records=%d "
                 "not_covered=%d unproven=%d noncomparable_skipped=%d verdict=%s"
                 % (",".join(machines), len(records), diffs, fails,
                    len(not_covered), len(unproven), skipped, verdict)),
    "value": verdict,
}))
