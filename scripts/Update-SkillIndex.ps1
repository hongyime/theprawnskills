# Preserve the existing PowerShell entrypoint; YAML parsing lives in one place.
[CmdletBinding()]
param([switch]$Check)
$ErrorActionPreference = 'Stop'
$indexScript = Join-Path $PSScriptRoot 'update_skill_index.py'
if ($Check) { & python $indexScript --check }
else { & python $indexScript }
if ($LASTEXITCODE -ne 0) { throw "Skill index command failed (exit $LASTEXITCODE)." }
