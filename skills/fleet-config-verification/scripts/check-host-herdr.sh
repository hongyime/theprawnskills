#!/bin/sh
# check-host-herdr.sh — host identity + Herdr live state. READ ONLY.
# Usage: EXPECTED_HOST=<hostname> MACHINE=<label> sh check-host-herdr.sh
# Piped to the target: cat check-host-herdr.sh | <host>-ssh 'bash -s'
# Emits JSON lines: machine, check, field, type, status, evidence, value.
# Status vocabulary: pass | fail | unproven | not-covered | unavailable.
# If hostname != EXPECTED_HOST, every record is unproven (V2), never passed.
MACHINE="${MACHINE:-$(hostname)}"
EXPECTED_HOST="${EXPECTED_HOST:-}"
HOSTNAME="$(hostname)"
TSIP="$(tailscale ip -4 2>/dev/null | head -1)"
[ -n "$TSIP" ] || TSIP="UNAVAILABLE"
if [ -n "$EXPECTED_HOST" ] && [ "$HOSTNAME" = "$EXPECTED_HOST" ]; then ID_OK=1; else ID_OK=0; fi
jemit() { python3 -c 'import json,sys; print(json.dumps({"machine":sys.argv[1],"check":sys.argv[2],"field":sys.argv[3],"type":sys.argv[4],"status":sys.argv[5],"evidence":sys.argv[6],"value":sys.argv[7] if len(sys.argv)>7 and sys.argv[7]!="" else None}))' "$MACHINE" "$1" "$2" "$3" "$4" "$5" "$6"; }
st() { if [ "$ID_OK" = 1 ]; then printf '%s' "$1"; else printf 'unproven'; fi; }
if [ "$ID_OK" = 1 ]; then ID_ST="pass"; else ID_ST="unproven"; fi
jemit "host-identity" "hostname" "host" "$ID_ST" "hostname=$HOSTNAME tailscale_ip=$TSIP expected_host=${EXPECTED_HOST:-unset}" "$HOSTNAME"
jemit "host-identity" "tailscale_ip" "host" "$(st pass)" "tailscale_ip=$TSIP" "$TSIP"
HC_BIN="$(command -v hc 2>/dev/null)"
[ -n "$HC_BIN" ] || [ -x "$HOME/.local/bin/hc" ] && HC_BIN="${HC_BIN:-$HOME/.local/bin/hc}"
[ -n "$HC_BIN" ] || [ -x "$HOME/workspace/bin/hc" ] && HC_BIN="${HC_BIN:-$HOME/workspace/bin/hc}"
if [ -z "$HC_BIN" ]; then
  jemit "herdr" "hc-present" "resolved" "$(st not-covered)" "hc not installed on this machine" ""
  exit 0
fi
HC_OUT="$("$HC_BIN" ls --json 2>&1)"
HC_RC=$?
if [ "$HC_RC" -ne 0 ]; then
  jemit "herdr" "hc-ls" "resolved" "$(st unavailable)" "hc ls exited $HC_RC: $(printf '%s' "$HC_OUT" | head -c 200)" ""
  exit 0
fi
printf '%s' "$HC_OUT" | EXPECTED="$MACHINE" ID_OK="$ID_OK" python3 -c '
import json, sys, os
raw = sys.stdin.read()
mid = os.environ.get("EXPECTED", "")
id_ok = os.environ.get("ID_OK", "0") == "1"
def st(s): return s if id_ok else "unproven"
try:
    d = json.loads(raw)
except Exception as e:
    print(json.dumps({"machine": mid, "check": "herdr", "field": "hc-ls", "type": "resolved", "status": st("unavailable"), "evidence": "hc ls output is not JSON: %s" % str(e)[:120], "value": None}))
    sys.exit(0)
machines = d.get("machines", [])
terms = d.get("terminals", [])
conn = [m.get("name") for m in machines if m.get("state") == "connected"]
live = [t for t in terms if t.get("state") == "live"]
statuses = {}
for t in live:
    statuses[t.get("status", "no-status")] = statuses.get(t.get("status", "no-status"), 0) + 1
print(json.dumps({"machine": mid, "check": "herdr", "field": "machines_connected", "type": "resolved", "status": st("pass"), "evidence": "connected=%s hidden_finished=%s" % (",".join(conn), d.get("hidden_finished")), "value": ",".join(sorted(conn))}))
print(json.dumps({"machine": mid, "check": "herdr", "field": "terminals_live", "type": "resolved", "status": st("pass"), "evidence": "live_terminals=%d statuses=%s" % (len(live), json.dumps(statuses)), "value": str(len(live))}))
for t in live:
    print(json.dumps({"machine": mid, "check": "herdr", "field": "terminal", "type": "resolved", "status": st("pass"), "evidence": "address=%s agent=%s cwd=%s state=%s status=%s turn=%s where=%s" % (t.get("address"), t.get("agent"), t.get("cwd"), t.get("state"), t.get("status"), t.get("turn"), t.get("where")), "value": t.get("address")}))
'
