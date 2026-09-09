# Targeted updates for existing OneDrive/Windows machines. Preview is the default.
[CmdletBinding()]
param(
  [string]$Workspace = (Join-Path $env:USERPROFILE 'OneDrive\01 SKILLS\.agents'),
  [Parameter(Mandatory=$true)][string[]]$SkillNames,
  [switch]$Apply,
  [switch]$LocalOnly,
  [switch]$AsJson
)
$ErrorActionPreference = 'Stop'
$workspacePath = (Resolve-Path -LiteralPath $Workspace).Path
$registryPath = Join-Path $workspacePath 'machines.toml'
$profilePath = Join-Path $workspacePath 'default-profile.toml'
$parseToml = 'import json,pathlib,sys,tomllib; print(json.dumps(tomllib.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8-sig"))))'
$registryJson = & python -c $parseToml $registryPath
if ($LASTEXITCODE -ne 0) { throw 'Cannot read machine registry with Python 3.11+.' }
$registry = $registryJson | ConvertFrom-Json
$profileJson = & python -c $parseToml $profilePath
if ($LASTEXITCODE -ne 0) { throw 'Cannot read daily profile.' }
$profile = $profileJson | ConvertFrom-Json
$names = @($SkillNames | Select-Object -Unique)
foreach ($name in $names) {
  if ($name -cnotmatch '^[a-z0-9][a-z0-9-]{0,63}$' -or $name -notin $profile.skills) {
    throw "Skill is not in the daily profile: $name"
  }
}

# The same worker runs locally or over SSH. It never writes a remote canonical library.
$worker = {
  param($Request)
  $ErrorActionPreference = 'Stop'
  function Get-SkillManifest([string]$Folder) {
    if (-not (Test-Path -LiteralPath (Join-Path $Folder 'SKILL.md'))) { throw "Skill source is not ready: $Folder. Check OneDrive sync or preserve/review this installed directory." }
    $source = (Resolve-Path -LiteralPath $Folder).Path.TrimEnd('\')
    if (-not (Test-Path -LiteralPath (Join-Path $source 'SKILL.md'))) { throw "Missing skill: $source" }
    $items = @(Get-ChildItem -LiteralPath $source -Recurse -Force)
    foreach ($item in $items) {
      if ($item.LinkType -in @('SymbolicLink','Junction')) { throw "Linked content needs review: $($item.FullName)" }
    }
    $entries = @($items | Where-Object { -not $_.PSIsContainer } | ForEach-Object {
      $relative = $_.FullName.Substring($source.Length + 1).Replace('\','/')
      $hash = (Get-FileHash -LiteralPath $_.FullName -Algorithm SHA256).Hash
      "$relative|$hash"
    } | Sort-Object)
    return ,$entries
  }
  function Same-Manifest($Left, $Right) {
    if (@($Left).Count -ne @($Right).Count) { return $false }
    return (@(Compare-Object -ReferenceObject @($Left) -DifferenceObject @($Right)).Count -eq 0)
  }
  function Assert-LocalTarget([string]$Path, [string]$UserRoot) {
    $full = [IO.Path]::GetFullPath($Path)
    $prefix = $UserRoot.TrimEnd('\') + '\'
    if (-not $full.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw "Target is outside this user home: $full" }
    $cursor = $full
    while ($cursor.Length -gt $UserRoot.Length) {
      $item = Get-Item -LiteralPath $cursor -Force -ErrorAction SilentlyContinue
      if ($item -and $item.LinkType -in @('SymbolicLink','Junction')) { throw "Redirected destination needs review: $cursor" }
      $cursor = Split-Path -Parent $cursor
    }
  }
  if ($Request.Action -eq 'Manifest') { return ,(Get-SkillManifest $Request.Source) }
  $userRoot = (Resolve-Path -LiteralPath $env:USERPROFILE).Path.TrimEnd('\')
  $backupBase = Join-Path $userRoot ('Backups\' + (Get-Date -Format 'yyyy-MM-dd') + '\skills\' + [guid]::NewGuid().ToString('N'))
  $plans = New-Object System.Collections.Generic.List[object]

  # Verify every selected source and destination before changing this machine.
  foreach ($skill in @($Request.Skills)) {
    $source = Join-Path $Request.CanonicalRoot ('skills\' + $skill.Name)
    $actual = Get-SkillManifest $source
    if (-not (Same-Manifest $actual $skill.Manifest)) { throw "OneDrive source not synchronized or has edits: $($skill.Name). Retry after sync." }
    foreach ($root in @($Request.Roots)) {
      $destination = Join-Path $root $skill.Name
      Assert-LocalTarget $destination $userRoot
      $present = Test-Path -LiteralPath $destination
      $old = @()
      if ($present) { $old = Get-SkillManifest $destination }
      $same = $present -and (Same-Manifest $old $actual)
      $rootKey = ($root -replace '[:\\]+','_').Trim('_')
      $backup = Join-Path $backupBase (Join-Path $rootKey $skill.Name)
      Assert-LocalTarget $backup $userRoot
      $plans.Add([pscustomobject]@{ Source=$source; Destination=$destination; Backup=$backup; Present=$present; Same=$same; Old=$old; Manifest=$actual; Name=$skill.Name })
    }
  }
  $rows = New-Object System.Collections.Generic.List[object]
  foreach ($plan in $plans) {
    $status = if ($plan.Same) { 'CURRENT' } elseif ($Request.Apply) { 'INSTALLED' } else { 'WOULD-INSTALL' }
    if (-not $plan.Same -and $Request.Apply) {
      try {
      Assert-LocalTarget $plan.Destination $userRoot
      Assert-LocalTarget $plan.Backup $userRoot
      if (-not (Same-Manifest (Get-SkillManifest $plan.Source) $plan.Manifest)) { throw "Source changed during sync: $($plan.Name)" }
      if ($plan.Present) {
        if (-not (Same-Manifest (Get-SkillManifest $plan.Destination) $plan.Old)) { throw "Installed skill changed during sync: $($plan.Name)" }
        New-Item -ItemType Directory -Force -Path (Split-Path -Parent $plan.Backup) | Out-Null
        # Targets are checked above, including all parent symlinks/junctions.
        Move-Item -LiteralPath $plan.Destination -Destination $plan.Backup
      } elseif (Test-Path -LiteralPath $plan.Destination) { throw "New destination appeared: $($plan.Destination)" }
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $plan.Destination) | Out-Null
      # Reserve the directory exclusively. Preserve a partial copy on failure.
      New-Item -ItemType Directory -Path $plan.Destination -ErrorAction Stop | Out-Null
      Get-ChildItem -LiteralPath $plan.Source -Force | Copy-Item -Destination $plan.Destination -Recurse
      if (-not (Same-Manifest (Get-SkillManifest $plan.Destination) $plan.Manifest)) { throw "Copy verification failed; retain backup: $($plan.Backup)" }
      } catch {
        $recovery = if (Test-Path -LiteralPath $plan.Backup) { "Original copy retained at $($plan.Backup)." } else { 'No original copy was moved to this backup location.' }
        throw "Update stopped for $($plan.Destination). $recovery Inspect any partial copy. $($_.Exception.Message)"
      }
    }
    $rows.Add([pscustomobject]@{ Machine=$Request.Machine; Skill=$plan.Name; Root=$plan.Destination; Status=$status; Backup=$(if ($plan.Present -and -not $plan.Same -and $Request.Apply) {$plan.Backup} else {''}) })
  }
  return ,$rows.ToArray()
}

$selected = @($names | ForEach-Object {
  $manifest = & $worker @{ Action='Manifest'; Source=(Join-Path $workspacePath ('skills\' + $_)) }
  [pscustomobject]@{ Name=$_; Manifest=@($manifest) }
})
$results = New-Object System.Collections.Generic.List[object]
foreach ($machine in @($registry.machines)) {
  if (-not $machine.enabled) { continue }
  $isLocal = $env:COMPUTERNAME -ieq $machine.id
  if ($LocalOnly -and -not $isLocal) { continue }
  $request = @{ Action='Install'; Machine=$machine.id; CanonicalRoot=$machine.canonical_root; Roots=@($machine.installed_roots); Skills=$selected; Apply=[bool]$Apply }
  try {
    if ($isLocal) {
      $rows = & $worker $request
    } else {
      if (-not $machine.ssh) { throw 'Missing SSH alias.' }
      $payload = $request | ConvertTo-Json -Depth 10 -Compress
      $payload64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($payload))
      $remoteScript = '$ProgressPreference = ''SilentlyContinue''; $request = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String(''' + $payload64 + ''')) | ConvertFrom-Json' + "`n" + 'try { & {' + $worker.ToString() + '} $request | ConvertTo-Json -Depth 5 -Compress } catch { [pscustomobject]@{Machine=$request.Machine;Skill="-";Root="-";Status="FAILED";Backup="";Detail=$_.Exception.Message} | ConvertTo-Json -Compress; exit 1 }'
      # Windows SSH can keep stdin open indefinitely. Transfer a small, auditable
      # helper file instead of waiting for Console.In.ReadToEnd on the target.
      $relativeFolder = 'Backups/' + (Get-Date -Format 'yyyy-MM-dd') + '/skills'
      $relativeFile = $relativeFolder + '/sync-helper-' + [guid]::NewGuid().ToString('N') + '.ps1'
      $localHelper = Join-Path $env:USERPROFILE $relativeFile
      New-Item -ItemType Directory -Force -Path (Split-Path -Parent $localHelper) | Out-Null
      [IO.File]::WriteAllText($localHelper, $remoteScript, [Text.UTF8Encoding]::new($false))
      $helperHash = (Get-FileHash -LiteralPath $localHelper -Algorithm SHA256).Hash
      $prepare = '$ProgressPreference = ''SilentlyContinue''; $ErrorActionPreference = ''Stop''; $p = Join-Path $env:USERPROFILE ''' + $relativeFolder + '''; $c = $p; while ($c.Length -gt $env:USERPROFILE.Length) { $i = Get-Item -LiteralPath $c -Force -ErrorAction SilentlyContinue; if ($i -and $i.LinkType -in @(''SymbolicLink'',''Junction'')) { throw ''Backup directory is redirected'' }; $c = Split-Path -Parent $c }; New-Item -ItemType Directory -Force -Path $p | Out-Null'
      $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($prepare))
      & ssh -o BatchMode=yes -o ConnectTimeout=10 $machine.ssh "powershell -NoProfile -NonInteractive -EncodedCommand $encoded"
      if ($LASTEXITCODE -ne 0) { throw 'Cannot prepare remote helper directory.' }
      & scp -q -o BatchMode=yes -o ConnectTimeout=10 $localHelper ($machine.ssh + ':' + $relativeFile)
      if ($LASTEXITCODE -ne 0) { throw 'Cannot transfer remote helper.' }
      $bootstrap = '$ProgressPreference = ''SilentlyContinue''; $ErrorActionPreference = ''Stop''; $p = Join-Path $env:USERPROFILE ''' + $relativeFile + '''; if ((Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash -ne ''' + $helperHash + ''') { throw ''Helper hash mismatch'' }; & ([scriptblock]::Create([IO.File]::ReadAllText($p)))'
      $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($bootstrap))
      $output = & ssh -o BatchMode=yes -o ConnectTimeout=10 $machine.ssh "powershell -NoProfile -NonInteractive -EncodedCommand $encoded"
      $remoteExit = $LASTEXITCODE
      if (-not $output) { throw 'No result from SSH; inspect connection/helper errors.' }
      $rows = ($output -join "`n") | ConvertFrom-Json
      if ($remoteExit -ne 0 -and -not @($rows | Where-Object Status -eq 'FAILED').Count) { throw 'SSH/helper failed without a structured error.' }
    }
    foreach ($row in @($rows)) { $results.Add($row) }
  } catch {
    $results.Add([pscustomobject]@{ Machine=$machine.id; Skill='-'; Root='-'; Status='FAILED'; Backup=''; Detail=$_.Exception.Message })
  }
}
if ($AsJson) { $results.ToArray() | ConvertTo-Json -Depth 5 }
else {
  $results | Format-Table Machine,Skill,Status -AutoSize
  foreach ($row in $results) {
    if ($row.Backup) { Write-Output "BACKUP $($row.Machine) $($row.Skill): $($row.Backup)" }
    if ($row.Status -eq 'FAILED') { Write-Output "FAILED $($row.Machine): $($row.Detail)" }
  }
}
if (@($results | Where-Object Status -eq 'FAILED').Count) { exit 1 }
if ($results.Count -eq 0) { throw 'No enabled machine matched this operation.' }
