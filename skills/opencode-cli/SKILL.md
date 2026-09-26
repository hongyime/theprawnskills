---
name: opencode-cli
description: Delegate tasks to OpenCode CLI as a hidden background process. Use when the user asks to use OpenCode, or when a task needs Bedrock model access, or when an active OpenCode session already exists. Spawns opencode hidden with output capture in $env:TEMP\hermes-opencode-out.txt.
---

# OpenCode CLI Skill

Delegate coding tasks to OpenCode by spawning it as a **hidden background PowerShell process**. Output tee'd to a temp file — tail with `Get-Content -Wait` if you want to peek.

## When to Use

- User explicitly asks to "use opencode" or "delegate to opencode"
- Task needs AWS Bedrock model access (Claude via Bedrock)
- An OpenCode session is already running and should be reused
- MCP server integrations specific to OpenCode are needed (ctftoolkit, ast_grep)

## Running a Task

### 1. Spawn as hidden background process

```powershell
# Standard: delegate a task
$out = "$env:TEMP\hermes-opencode-out.txt"; Remove-Item $out -EA SilentlyContinue
$proc = Start-Process pwsh -WindowStyle Hidden -PassThru -ArgumentList '-NoProfile','-Command',"opencode 'YOUR_PROMPT_HERE' 2>&1 | Tee-Object -FilePath '$out'; Add-Content '$out' '=== OPENCODE COMPLETE ==='"

# In a specific project directory
$out = "$env:TEMP\hermes-opencode-out.txt"; Remove-Item $out -EA SilentlyContinue
$proc = Start-Process pwsh -WindowStyle Hidden -PassThru -ArgumentList '-NoProfile','-Command',"Set-Location 'C:\path\to\project'; opencode 'YOUR_PROMPT_HERE' 2>&1 | Tee-Object -FilePath '$out'; Add-Content '$out' '=== OPENCODE COMPLETE ==='"
```

### 2. Poll for completion

```powershell
$outFile = "$env:TEMP\hermes-opencode-out.txt"
$timeout = 300; $start = Get-Date
while (((Get-Date) - $start).TotalSeconds -lt $timeout) {
    if ((Test-Path $outFile) -and (Get-Content $outFile -Raw) -match "=== OPENCODE COMPLETE ===") { break }
    Start-Sleep -Seconds 10
}
$result = Get-Content $outFile -Raw -ErrorAction SilentlyContinue
```

### 3. Report results

Summarize what OpenCode found or changed, flag any errors, and offer follow-up.

## Authentication

Use the provider authentication configured on the current machine. The older
`hermes-opencode-setup` integration is an optional external tool and is not
bundled in this library. Do not assume its setup script or menu exists. If the
user has installed that integration, locate and inspect its current instructions;
otherwise follow the installed OpenCode provider's authentication workflow.
Report missing authentication as a prerequisite, without copying credentials
from another machine or printing authentication files.

Or if using ABSK static keys, these are configured in the OpenCode config at:
`%USERPROFILE%\.config\opencode\opencode.jsonc`

## OpenCode Config Location

- Config: `%USERPROFILE%\.config\opencode\opencode.jsonc`
- Auth: `%USERPROFILE%\.local\share\opencode\auth.json`
- Default model: `bedrock/global.anthropic.claude-sonnet-4-6`

## Critical Rules

1. OpenCode may start an interactive TUI — for automated delegation, prefer piping the prompt
2. Check that the selected provider's authentication is valid before spawning.
3. If authentication expires, use that provider's current login workflow; do not assume a setup-script menu or a fixed token lifetime.
4. OpenCode has its own MCP servers (ctftoolkit, ast_grep) — these give it capabilities other agents lack

## Comparison with Other Agents

| Feature | OpenCode | Claude Code | Codex | Gemini |
|---|---|---|---|---|
| Best at | Bedrock access, MCP tools | Multi-file reasoning | OpenAI models | Huge context |
| Auth | AWS SSO / ABSK | Anthropic account | OpenAI account | Google account |
| Model | Claude via Bedrock | Claude direct | GPT-5.2 | Gemini 3 |
| MCP support | Yes (ctftoolkit, ast_grep) | Yes (via config) | No | Yes (built-in) |
