#!/bin/sh
# diff-fleet-config.sh — hash/byte-compare config files across the fleet, outlier report.
# READ ONLY. Runs from the VM. Part of the fleet-parity skill.
#
# Usage:
#   diff-fleet-config.sh [--git-identity] [relative-path ...]
#   Relative paths are relative to $HOME (Linux) / %USERPROFILE% (Windows).
#   Default file set (no args): the standard fleet config files.
#   --git-identity: also sweep repo-level git identity overrides via the
#     fleet-config-verification check-git-drift scripts and list them as outliers.
#
# Output: per-file table, then an OUTLIERS section. Exit 0 = no outliers,
# exit 2 = outliers found, exit 1 = usage/transport error.
# Host identity is proven per machine (hostname in the probe output must
# match EXPECTED_HOST); a mismatch marks that machine UNPROVEN, never passed.
#
# Transport (same as fleet-config-verification): Linux probes are piped via
# stdin (never ssh 'a; b' — that splits across the jump host); Windows
# probes are scp'd as .ps1, run with powershell -NoProfile, then deleted.
# SSH from the VM passes -F /home/hatch/.ssh/config explicitly.

SKILL_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
VERIFY_SCRIPTS="${FLEET_VERIFY_SCRIPTS:-$SKILL_DIR/../fleet-config-verification/scripts}"

DEFAULT_FILES=".config/opencode/opencode.jsonc .config/opencode/model-fallback.json .codex/config.toml .codex/models_cache.json .codex/AGENTS.md .omo/omo.jsonc .config/theprawnskills/library.json Projects/forge/AGENTS.md AGENTS.md"

GIT_IDENTITY=0
FILES=""
for a in "$@"; do
  case "$a" in
    --git-identity) GIT_IDENTITY=1 ;;
    --help|-h) sed -n '2,14p' "$0"; exit 0 ;;
    *) FILES="$FILES $a" ;;
  esac
done
[ -z "$FILES" ] && FILES="$DEFAULT_FILES"

# machine|expected_host|transport|address
MACHINES="vm|htch-runtime|local|
l390|prawn-l390|ssh|prawn-l390
3410|prawn-3410|ssh|prawn-3410
t14|Prawn-T14|win|prawn-t14
e14|PRAWN-E14|win|prawn-e14"

OUTDIR="${TMPDIR:-/tmp}/diff-fleet-config-$$"
mkdir -p "$OUTDIR" || exit 1
trap 'rm -rf "$OUTDIR"' EXIT INT TERM

probe_linux() {
  # $1 = file list (space-separated, relative paths)
  # HOST line first: hostname proven in the same session as the hashes.
  # Single remote command only (bash -s) — never 'hostname; bash -s',
  # which splits across the jump host (second command runs on L390).
  cat <<'PROBE'
echo "HOST $(hostname)"
for p in "$@"; do
  f="$HOME/$p"
  if [ -f "$f" ]; then echo "FILE $p $(sha256sum "$f" | cut -d' ' -f1)"
  elif [ -d "$f" ]; then echo "DIR $p"
  else echo "MISSING $p"; fi
done
PROBE
}

probe_windows() {
  # $1 = probe file path to write
  cat > "$1" <<'PROBE'
"HOST $env:COMPUTERNAME"
foreach ($p in $args) {
  $f = Join-Path $env:USERPROFILE ($p -replace '/', '\')
  if (Test-Path $f -PathType Leaf) {
    $h = (Get-FileHash $f -Algorithm SHA256).Hash.ToLower()
    "FILE $p $h"
  } elseif (Test-Path $f -PathType Container) { "DIR $p" }
  else { "MISSING $p" }
}
PROBE
}

collect() {
  _m="$1"; _host="$2"; _t="$3"; _addr="$4"
  _out="$OUTDIR/$_m.txt"
  case "$_t" in
    local)
      # shellcheck disable=SC2086
      probe_linux $FILES | sh -s -- $FILES > "$_out" 2>"$OUTDIR/$_m.err"
      ;;
    ssh)
      _wrap="$HOME/workspace/bin/${_m}-ssh"
      if [ -x "$_wrap" ]; then _ssh="$_wrap"; else _ssh="ssh -F /home/hatch/.ssh/config $_addr"; fi
      # Single remote command (bash -s); hostname comes from inside the probe.
      # shellcheck disable=SC2086
      probe_linux $FILES | $_ssh 'bash -s -- '"$FILES"'' > "$_out" 2>"$OUTDIR/$_m.err"
      ;;
    win)
      probe_windows "$OUTDIR/probe-$_m.ps1"
      # < /dev/null on scp/ssh: this runs inside a while-read loop whose
      # stdin is the machine list — an ssh that inherits it consumes the
      # remaining lines and kills the loop before the last machine runs.
      scp -F /home/hatch/.ssh/config "$OUTDIR/probe-$_m.ps1" "$_addr:C:/Users/bryan/diff-fleet-probe.ps1" < /dev/null 2>"$OUTDIR/$_m.err" || { echo "HOST UNREACHABLE" > "$_out"; return; }
      # '&' is cmd's separator (';' is passed through as a script argument).
      # shellcheck disable=SC2086
      ssh -F /home/hatch/.ssh/config -o ConnectTimeout=20 "$_addr" "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\bryan\diff-fleet-probe.ps1 $FILES < NUL & del C:\Users\bryan\diff-fleet-probe.ps1" < /dev/null 2>>"$OUTDIR/$_m.err" | tr -d '\r' > "$_out"
      ;;
  esac
  # Host-truth: the HOST line must equal the expected hostname (case-insensitive).
  _got="$(sed -n 's/^HOST //p' "$_out" | head -1)"
  if [ "$(printf '%s' "$_got" | tr 'A-Z' 'a-z')" != "$(printf '%s' "$_host" | tr 'A-Z' 'a-z')" ]; then
    echo "UNPROVEN $_m: expected host $_host, got ${_got:-<none>}" >&2
    printf 'UNPROVEN %s\n' "$_m" >> "$OUTDIR/unproven.txt"
  fi
}

echo "fleet-parity diff — $(date -u +%Y-%m-%dT%H:%M:%SZ) — files:$FILES"
echo "$MACHINES" | while IFS='|' read -r m h t a; do
  [ -n "$m" ] || continue
  collect "$m" "$h" "$t" "$a"
done

# Compare with python3 (present on the VM); plain table + outlier list.
python3 - "$OUTDIR" $FILES <<'PYEOF'
import sys, os
outdir, files = sys.argv[1], sys.argv[2:]
machines = ["vm", "l390", "3410", "t14", "e14"]
table = {}   # file -> {machine: value}
unproven = set()
up = os.path.join(outdir, "unproven.txt")
if os.path.exists(up):
    unproven = {l.split()[1] for l in open(up) if l.strip()}
for m in machines:
    p = os.path.join(outdir, m + ".txt")
    if not os.path.exists(p):
        for f in files:
            table.setdefault(f, {})[m] = "NO-DATA"
        continue
    for line in open(p):
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("FILE", "MISSING", "DIR"):
            table.setdefault(parts[1], {})[m] = parts[2] if len(parts) > 2 else parts[0]
outliers = []
print("file | " + " | ".join(machines))
for f in files:
    vals = {m: table.get(f, {}).get(m, "NO-DATA") for m in machines}
    distinct = set(vals.values())
    flag = "OUTLIER" if len(distinct) > 1 else "same"
    if flag == "OUTLIER":
        outliers.append((f, vals))
    short = {m: (v[:12] if v not in ("MISSING", "DIR", "NO-DATA") else v) for m, v in vals.items()}
    print(f"{f} | " + " | ".join(short[m] for m in machines) + f" | {flag}")
print()
print("OUTLIERS:")
if not outliers and not unproven:
    print("none")
for f, vals in outliers:
    for m in machines:
        print(f"  {f}: {m}={vals[m]}")
if unproven:
    for m in sorted(unproven):
        print(f"  UNPROVEN host: {m} (hostname mismatch — result not attributed)")
sys.exit(2 if (outliers or unproven) else 0)
PYEOF
RC=$?
if [ "$GIT_IDENTITY" = 1 ]; then
  echo
  echo "GIT IDENTITY OVERRIDES (check-git-drift, expected: bryanseah234 <66017805+bryanseah234@users.noreply.github.com>):"
  OVERRIDE_FOUND=0
  for m in vm l390 3410 t14 e14; do
    case "$m" in
      vm) EXPECTED_HOST=htch-runtime MACHINE=vm EXPECTED_NAME=bryanseah234 EXPECTED_EMAIL=66017805+bryanseah234@users.noreply.github.com sh "$VERIFY_SCRIPTS/check-git-drift.sh" 2>/dev/null | grep '"status": "fail"' | sed "s/^/  $m: /" && OVERRIDE_FOUND=1 || true ;;
      l390|3410) cat "$VERIFY_SCRIPTS/check-git-drift.sh" | "$HOME/workspace/bin/$m-ssh" "EXPECTED_HOST=prawn-$m MACHINE=$m EXPECTED_NAME=bryanseah234 EXPECTED_EMAIL=66017805+bryanseah234@users.noreply.github.com bash -s" 2>/dev/null | grep '"status": "fail"' | sed "s/^/  $m: /" && OVERRIDE_FOUND=1 || true ;;
      t14|e14) scp -F /home/hatch/.ssh/config "$VERIFY_SCRIPTS/check-git-drift.ps1" "prawn-$m:C:/Users/bryan/check-git-drift.ps1" 2>/dev/null && ssh -F /home/hatch/.ssh/config -o ConnectTimeout=30 "prawn-$m" "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\bryan\check-git-drift.ps1 < NUL & del C:\Users\bryan\check-git-drift.ps1" 2>/dev/null | grep '"status": "fail"' | sed "s/^/  $m: /" && OVERRIDE_FOUND=1 || true ;;
    esac
  done
  [ "$OVERRIDE_FOUND" = 0 ] && echo "  none"
  [ "$OVERRIDE_FOUND" = 1 ] && RC=2
fi
exit $RC
