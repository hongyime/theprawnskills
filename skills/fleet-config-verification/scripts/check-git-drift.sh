#!/bin/sh
# check-git-drift.sh — global git identity + per-repo local overrides + drift. READ ONLY.
# Usage: EXPECTED_HOST=<h> MACHINE=<label> EXPECTED_NAME=<n> EXPECTED_EMAIL=<e>
#        REPO_ROOT=<dir> sh check-git-drift.sh
# Piped to the target: cat check-git-drift.sh | <host>-ssh 'bash -s'
# Default REPO_ROOT: $HOME/workspace on the VM, $HOME/Projects elsewhere — pass it explicitly.
# Emits JSON lines: machine, check, field, type, status, evidence, value.
# A repo-local identity that differs from global is status fail (it is an
# unswept override until a human confirms it intentional). A repo with no
# local identity inherits global: pass.
MACHINE="${MACHINE:-$(hostname)}"
EXPECTED_HOST="${EXPECTED_HOST:-}"
EXPECTED_NAME="${EXPECTED_NAME:-}"
EXPECTED_EMAIL="${EXPECTED_EMAIL:-}"
HOSTNAME="$(hostname)"
if [ -n "$EXPECTED_HOST" ] && [ "$HOSTNAME" = "$EXPECTED_HOST" ]; then ID_OK=1; else ID_OK=0; fi
jemit() { python3 -c 'import json,sys; print(json.dumps({"machine":sys.argv[1],"check":sys.argv[2],"field":sys.argv[3],"type":sys.argv[4],"status":sys.argv[5],"evidence":sys.argv[6],"value":sys.argv[7] if len(sys.argv)>7 and sys.argv[7]!="" else None}))' "$MACHINE" "$1" "$2" "$3" "$4" "$5" "$6"; }
st() { if [ "$ID_OK" = 1 ]; then printf '%s' "$1"; else printf 'unproven'; fi; }
if [ -z "$EXPECTED_NAME" ] || [ -z "$EXPECTED_EMAIL" ]; then
  jemit "git" "global_identity" "unavailable" "$(st unavailable)" "EXPECTED_NAME/EXPECTED_EMAIL not supplied" ""
  exit 0
fi
GN="$(git config --global user.name 2>/dev/null)"
GE="$(git config --global user.email 2>/dev/null)"
if [ "$GN" = "$EXPECTED_NAME" ] && [ "$GE" = "$EXPECTED_EMAIL" ]; then
  jemit "git" "global_identity" "file" "$(st pass)" "global=$GN <$GE>" "$GN <$GE>"
else
  jemit "git" "global_identity" "file" "$(st fail)" "global=$GN <$GE> expected=$EXPECTED_NAME <$EXPECTED_EMAIL>" "$GN <$GE>"
fi
ROOT="${REPO_ROOT:-$HOME/Projects}"
[ -d "$ROOT" ] || ROOT="$HOME/workspace"
if [ ! -d "$ROOT" ]; then
  jemit "git" "repo_sweep" "file" "$(st unavailable)" "no repo root found ($ROOT)" ""
  exit 0
fi
COUNT=0; OVERRIDES=0
for gd in $(find "$ROOT" -maxdepth 3 -name .git 2>/dev/null | head -100); do
  REPO="$(dirname "$gd")"
  COUNT=$((COUNT + 1))
  LN="$(git -C "$REPO" config --local user.name 2>/dev/null)"
  LE="$(git -C "$REPO" config --local user.email 2>/dev/null)"
  if [ -z "$LN" ] && [ -z "$LE" ]; then
    jemit "git" "repo_identity" "file" "$(st pass)" "repo=$REPO local identity unset, inherits global" "$REPO:inherit"
  elif [ "$LN" = "$GN" ] && [ "$LE" = "$GE" ]; then
    jemit "git" "repo_identity" "file" "$(st pass)" "repo=$REPO local=$LN <$LE> (same as global)" "$REPO:same"
  else
    OVERRIDES=$((OVERRIDES + 1))
    jemit "git" "repo_identity" "file" "$(st fail)" "repo=$REPO LOCAL OVERRIDE local=$LN <$LE> global=$GN <$GE>" "$REPO:$LN <$LE>"
  fi
  BR="$(git -C "$REPO" rev-parse --abbrev-ref HEAD 2>/dev/null || echo unknown)"
  if command -v timeout >/dev/null 2>&1; then DIRTY="$(timeout 30 git -C "$REPO" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"; else DIRTY="$(git -C "$REPO" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"; fi
  AB="$(git -C "$REPO" rev-list --left-right --count HEAD...@{upstream} 2>/dev/null || echo no-upstream)"
  jemit "git" "repo_drift" "file" "$(st pass)" "repo=$REPO branch=$BR dirty_files=$DIRTY ahead_behind=$AB" "$REPO:$BR:$DIRTY:$AB"
done
jemit "git" "repo_sweep" "file" "$(st pass)" "root=$ROOT repos_scanned=$COUNT local_overrides=$OVERRIDES" "$COUNT:$OVERRIDES"
