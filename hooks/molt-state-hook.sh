#!/usr/bin/env bash
# MOLT state hook (bash equivalent of molt-state-hook.ps1)
# Auto-updates .agents/STATE.md and .agents/JOURNAL.md on hook events.
# All errors are swallowed; always exits 0.
set -u

EVENT="manual"
HARNESS="unknown"
DEBOUNCE_SECONDS=300
DRY_RUN=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --event) EVENT="$2"; shift 2 ;;
    --harness) HARNESS="$2"; shift 2 ;;
    --debounce-seconds) DEBOUNCE_SECONDS="$2"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) shift ;;
  esac
done

exit_clean() {
  [[ $DRY_RUN -eq 1 && -n "${1:-}" ]] && echo "$1"
  exit 0
}

# Sanitize event/harness (allow A-Za-z0-9_.:-, replace rest with -)
EVENT="$(printf '%s' "$EVENT" | sed 's/[^A-Za-z0-9_.:-]/-/g')"
HARNESS="$(printf '%s' "$HARNESS" | sed 's/[^A-Za-z0-9_.:-]/-/g')"

# Must be in a git repo
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit_clean "MOLT: not in a git repo"
[[ -z "$REPO_ROOT" ]] && exit_clean "MOLT: not in a git repo"

STATE_PATH="$REPO_ROOT/.agents/STATE.md"
JOURNAL_PATH="$REPO_ROOT/.agents/JOURNAL.md"
[[ -f "$STATE_PATH" ]] || exit_clean "MOLT: .agents/STATE.md not present"

# Origin must be owned by hongyime or bryanseah234
REMOTE_URL="$(git -C "$REPO_ROOT" remote get-url origin 2>/dev/null || true)"
if ! printf '%s' "$REMOTE_URL" | grep -Eq 'github\.com[:/](hongyime|bryanseah234)/'; then
  exit_clean "MOLT: repo origin not owned"
fi

BRANCH="$(git -C "$REPO_ROOT" branch --show-current 2>/dev/null || true)"
[[ -z "$BRANCH" ]] && BRANCH="detached"
HEAD="$(git -C "$REPO_ROOT" rev-parse --short HEAD 2>/dev/null || true)"
[[ -z "$HEAD" ]] && HEAD="unknown"

# Dirty count excluding .agents/STATE.md and .agents/JOURNAL.md
DIRTY_COUNT="$(git -C "$REPO_ROOT" status --porcelain 2>/dev/null | grep -vE '\s\.agents/(STATE|JOURNAL)\.md$' | wc -l | tr -d ' ')"

TIMESTAMP="$(date '+%Y-%m-%d %H:%M:%S %z')"
MACHINE="$(hostname 2>/dev/null || echo unknown-machine)"
RESUME_HINT="Read .agents/STATE.md, then the latest file in .agents/handoffs/ if present."

# Debounce via SHA256 of repoRoot|branch|harness|event
CACHE_ROOT="$HOME/.cache/molt"
CACHE_INPUT="${REPO_ROOT}|${BRANCH}|${HARNESS}|${EVENT}"
CACHE_NAME="$(printf '%s' "$CACHE_INPUT" | sha256sum | cut -d' ' -f1)"
CACHE_PATH="$CACHE_ROOT/${CACHE_NAME}.stamp"

if [[ $DRY_RUN -eq 0 && $DEBOUNCE_SECONDS -gt 0 && -f "$CACHE_PATH" ]]; then
  LAST_WRITE="$(stat -c %Y "$CACHE_PATH" 2>/dev/null || echo 0)"
  NOW="$(date +%s)"
  if (( NOW - LAST_WRITE < DEBOUNCE_SECONDS )); then
    exit_clean "MOLT: debounced"
  fi
fi

JOURNAL_LINE="- $TIMESTAMP [$MACHINE/$HARNESS/$EVENT] branch=$BRANCH head=$HEAD dirty=$DIRTY_COUNT"

read -r -d '' AUTO_BLOCK <<EOF || true
<!-- MOLT_AUTO_START -->
## Auto State

- Updated: $TIMESTAMP
- Machine: $MACHINE
- Harness: $HARNESS
- Event: $EVENT
- Branch: $BRANCH
- HEAD: $HEAD
- Dirty files: $DIRTY_COUNT
- Resume hint: $RESUME_HINT
<!-- MOLT_AUTO_END -->
EOF

if [[ $DRY_RUN -eq 1 ]]; then
  echo "MOLT dry run"
  echo "Repo: $REPO_ROOT"
  echo "Journal: $JOURNAL_LINE"
  printf '%s\n' "$AUTO_BLOCK"
  exit 0
fi

AGENTS_DIR="$(dirname "$STATE_PATH")"
[[ -d "$AGENTS_DIR" ]] || exit_clean "MOLT: .agents missing"
mkdir -p "$CACHE_ROOT" 2>/dev/null || true

# Lock, update journal + state + stamp
LOCK_FILE="$CACHE_ROOT/${CACHE_NAME}.lock"
exec 9>"$LOCK_FILE" 2>/dev/null || exit_clean "MOLT: lock busy"
if ! flock -w 2 9 2>/dev/null; then
  exit_clean "MOLT: lock busy"
fi

[[ -f "$JOURNAL_PATH" ]] || : > "$JOURNAL_PATH"
printf '%s\n' "$JOURNAL_LINE" >> "$JOURNAL_PATH"

# Replace existing MOLT_AUTO block or append
if grep -q '<!-- MOLT_AUTO_START -->' "$STATE_PATH" 2>/dev/null; then
  # Use python for reliable multiline replace
  python3 - "$STATE_PATH" "$AUTO_BLOCK" <<'PYEOF' 2>/dev/null || true
import re, sys
path, block = sys.argv[1], sys.argv[2]
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()
pattern = r'<!-- MOLT_AUTO_START -->.*?<!-- MOLT_AUTO_END -->'
new_content, n = re.subn(pattern, block, content, count=1, flags=re.DOTALL)
if n == 0:
    new_content = content.rstrip() + '\n\n' + block + '\n'
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
PYEOF
else
  printf '\n%s\n' "$AUTO_BLOCK" >> "$STATE_PATH"
fi

printf '%s' "$TIMESTAMP" > "$CACHE_PATH" 2>/dev/null || true

exit 0
