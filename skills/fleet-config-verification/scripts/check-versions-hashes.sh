#!/bin/sh
# check-versions-hashes.sh — tool versions + config-file hashes. READ ONLY.
# Usage: EXPECTED_HOST=<hostname> MACHINE=<label> sh check-versions-hashes.sh
# Piped to the target: cat check-versions-hashes.sh | <host>-ssh 'bash -s'
# Emits JSON lines: machine, check, field, type, status, evidence, value.
# Status vocabulary: pass | fail | unproven | not-covered | unavailable.
# A missing tool/file is not-covered, never pass and never fail on its own.
# Divergence is decided by diff-reports.py, not here.
MACHINE="${MACHINE:-$(hostname)}"
EXPECTED_HOST="${EXPECTED_HOST:-}"
HOSTNAME="$(hostname)"
if [ -n "$EXPECTED_HOST" ] && [ "$HOSTNAME" = "$EXPECTED_HOST" ]; then ID_OK=1; else ID_OK=0; fi
jemit() { python3 -c 'import json,sys; print(json.dumps({"machine":sys.argv[1],"check":sys.argv[2],"field":sys.argv[3],"type":sys.argv[4],"status":sys.argv[5],"evidence":sys.argv[6],"value":sys.argv[7] if len(sys.argv)>7 and sys.argv[7]!="" else None}))' "$MACHINE" "$1" "$2" "$3" "$4" "$5" "$6"; }
st() { if [ "$ID_OK" = 1 ]; then printf '%s' "$1"; else printf 'unproven'; fi; }
ver() {
  _t="$1"
  _bin="$(command -v "$_t" 2>/dev/null)"
  [ -n "$_bin" ] || [ -x "$HOME/.local/bin/$_t" ] && _bin="${_bin:-$HOME/.local/bin/$_t}"
  [ -n "$_bin" ] || [ -x "$HOME/workspace/bin/$_t" ] && _bin="${_bin:-$HOME/workspace/bin/$_t}"
  if [ -z "$_bin" ]; then
    jemit "version" "$_t" "version" "$(st not-covered)" "$_t not installed" ""
    return
  fi
  _p="$_bin"
  if command -v timeout >/dev/null 2>&1; then _v="$(timeout 10 "$_p" --version 2>&1 | head -1)"; else _v="$("$_p" --version 2>&1 | head -1)"; fi
  if [ -z "$_v" ]; then
    jemit "version" "$_t" "version" "$(st unavailable)" "$_p present but --version returned nothing" "$_p"
  else
    jemit "version" "$_t" "version" "$(st pass)" "$_p | $_v" "$_v"
  fi
}
for t in codex agy opencode hc herdr strix kiro gh; do ver "$t"; done
hashfile() {
  _field="$1"; _path="$2"
  if [ ! -f "$_path" ]; then
    jemit "file" "$_field" "file" "$(st not-covered)" "$_path missing" ""
    return
  fi
  if command -v sha256sum >/dev/null 2>&1; then _h="$(sha256sum "$_path" | cut -d' ' -f1)"; else _h="$(shasum -a 256 "$_path" | cut -d' ' -f1)"; fi
  _b="$(stat -c%s "$_path" 2>/dev/null || stat -f%z "$_path" 2>/dev/null)"
  jemit "file" "$_field" "file" "$(st pass)" "$_path sha256=$_h bytes=$_b" "$_h"
}
hashfile "opencode_jsonc" "$HOME/.config/opencode/opencode.jsonc"
hashfile "model_fallback" "$HOME/.config/opencode/model-fallback.json"
hashfile "codex_config" "$HOME/.codex/config.toml"
hashfile "omo_jsonc" "$HOME/.omo/omo.jsonc"
hashfile "library_json" "$HOME/.config/theprawnskills/library.json"
hashfile "forge_agents" "/home/bryan/Projects/forge/AGENTS.md"
if [ -d "$HOME/.agents/skills" ]; then
  _n="$(ls "$HOME/.agents/skills" 2>/dev/null | wc -l | tr -d ' ')"
  jemit "file" "skills_dir_entries" "file" "$(st pass)" "$HOME/.agents/skills entries=$_n" "$_n"
else
  jemit "file" "skills_dir_entries" "file" "$(st not-covered)" "$HOME/.agents/skills missing" ""
fi
