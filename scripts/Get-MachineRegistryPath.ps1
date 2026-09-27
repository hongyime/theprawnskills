function Get-MachineRegistryPath {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory=$true)][string]$Workspace,
    [string]$ExplicitPath = $env:THEPRAWNSKILLS_MACHINE_CONFIG
  )
  if (-not [string]::IsNullOrWhiteSpace($ExplicitPath)) {
    $candidate = $ExplicitPath
  } else {
    $privatePath = Join-Path $Workspace "machines.local.toml"
    $candidate = if (Test-Path -LiteralPath $privatePath -PathType Leaf) { $privatePath } else { Join-Path $Workspace "machines.toml" }
  }
  if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) {
    throw "Machine registry file is missing. Supply THEPRAWNSKILLS_MACHINE_CONFIG or a private machines.local.toml."
  }
  return (Resolve-Path -LiteralPath $candidate).Path
}
