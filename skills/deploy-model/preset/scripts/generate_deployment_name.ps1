# Query existing Azure deployments; print a free name. Never creates a deployment.
[CmdletBinding()]
param(
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$AccountName,
    [Parameter(Mandatory)][ValidateNotNullOrEmpty()][string]$ResourceGroup,
    [Parameter(Mandatory)][ValidatePattern('^[A-Za-z0-9][A-Za-z0-9_.-]{0,63}$')][string]$ModelName
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command az -ErrorAction SilentlyContinue)) { throw 'Azure CLI is required.' }
$existing = @(& az cognitiveservices account deployment list --name $AccountName --resource-group $ResourceGroup --query '[].name' --output tsv --only-show-errors)
if ($LASTEXITCODE -ne 0) { throw 'Cannot list deployments; no name was selected.' }
$names = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
foreach ($line in $existing) { [void]$names.Add(([string]$line).Trim()) }
$candidate = $ModelName
$suffix = 2
while ($names.Contains($candidate)) {
    $suffixText = "-$suffix"
    $baseLength = [Math]::Min($ModelName.Length, 64 - $suffixText.Length)
    $candidate = $ModelName.Substring(0, $baseLength) + $suffixText
    $suffix++
}
$candidate
