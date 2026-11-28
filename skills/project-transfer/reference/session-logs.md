### 1.4 Agent Session Logs (Home Folders)

Search agent session logs for mentions of `SOURCE`'s absolute path or folder name. Logs can be massive: use `rg` (ripgrep) or targeted file searches first; never read entire log files into context unfiltered.

#### Known Cross-Platform Locations

| Agent | Linux / macOS | Windows |
|---|---|---|
| Claude Code | `~/.claude/projects/` | `%USERPROFILE%\.claude\projects\` |
| Codex CLI | `~/.codex/sessions/` | `%USERPROFILE%\.codex\sessions\` |
| Gemini CLI / Antigravity | `~/.gemini/` | `%USERPROFILE%\.gemini\` |
| OpenCode | `~/.config/opencode/`, `~/.local/share/opencode/` | `%APPDATA%\opencode\`, `%LOCALAPPDATA%\opencode\` |
| Other Agents | `~/.cursor/`, `~/.kimi/`, `~/.qwen/`, `~/.windsurf/` | `%USERPROFILE%\.<agent>\` |

#### Fast Grep Patterns

```bash
# Linux / macOS — filter by repo path or owner/repo where possible to avoid short-name collisions and sweep meta-logs
rg -l -F -e "<owner>/<repo>" -e "/<SOURCE_NAME>" ~/.claude/projects ~/.codex/sessions ~/.gemini ~/.local/share/opencode -g "*.json" -g "*.jsonl" -g "*.md" -g "!*transcript*" 2>/dev/null | head -20
```

```powershell
# Windows PowerShell
$logs = "$HOME\.claude\projects", "$HOME\.codex\sessions", "$HOME\.gemini"
rg -l "SOURCE_NAME" $logs -g "*.json" -g "*.jsonl" -g "*.md"
```

From matched logs, extract surrounding context (3-5 lines). When inspecting matched `.jsonl` files, parse/truncate each matched line (`cut -c1-400`) instead of printing raw `rg -C 5` context, so single-line JSON records do not flood context. Ignore meta-logs from the current harvest sweep itself. If no local logs exist on this host, record `none on this host` rather than claiming none ever existed. Focus on: **user corrections** ("no", "don't", "instead", "again", "I told you", "stop doing"); **recurring errors** (same compilation/lint/runtime bug, multiple times); **loop-ending fixes** (the breakthrough that resolved a prolonged debugging session); **repeated manual steps** (commands/setup the user repeatedly ran or asked the agent to run).

