# check-git-drift.ps1 — global git identity + per-repo local overrides + drift. READ ONLY.
# Transport: scp to host, run, delete (see check-host-herdr.ps1 header).
# Env: $env:EXPECTED_HOST, $env:MACHINE, $env:EXPECTED_NAME, $env:EXPECTED_EMAIL, $env:REPO_ROOT (default $env:USERPROFILE\Projects).
# Emits JSON lines, same schema as check-git-drift.sh.
$Machine = if ($env:MACHINE) { $env:MACHINE } else { $env:COMPUTERNAME }
$ExpectedHost = $env:EXPECTED_HOST
$ExpectedName = $env:EXPECTED_NAME
$ExpectedEmail = $env:EXPECTED_EMAIL
$IdOk = ($ExpectedHost -and ($env:COMPUTERNAME -eq $ExpectedHost))
function Emit($Check, $Field, $Type, $Status, $Evidence, $Value) {
  if (-not $IdOk -and $Status -ne "unproven") { $Status = "unproven" }
  $rec = [ordered]@{ machine = $Machine; check = $Check; field = $Field; type = $Type; status = $Status; evidence = $Evidence; value = $Value }
  Write-Output ($rec | ConvertTo-Json -Compress)
}
if (-not $ExpectedName -or -not $ExpectedEmail) {
  Emit "git" "global_identity" "file" "unavailable" "EXPECTED_NAME/EXPECTED_EMAIL not supplied" $null
  exit 0
}
$gn = (git config --global user.name 2>$null); $ge = (git config --global user.email 2>$null)
if ($gn -eq $ExpectedName -and $ge -eq $ExpectedEmail) {
  Emit "git" "global_identity" "file" "pass" "global=$gn <$ge>" "$gn <$ge>"
} else {
  Emit "git" "global_identity" "file" "fail" "global=$gn <$ge> expected=$ExpectedName <$ExpectedEmail>" "$gn <$ge>"
}
$Root = if ($env:REPO_ROOT) { $env:REPO_ROOT } else { "$env:USERPROFILE\Projects" }
if (-not (Test-Path $Root)) {
  Emit "git" "repo_sweep" "file" "unavailable" "no repo root found ($Root)" $null
  exit 0
}
$count = 0; $overrides = 0
$topDirs = @(Get-ChildItem $Root -Directory -ErrorAction SilentlyContinue)
$candidates = @($topDirs)
foreach ($d in $topDirs) { $candidates += @(Get-ChildItem $d.FullName -Directory -ErrorAction SilentlyContinue) }
$repos = @($candidates | Where-Object { Test-Path (Join-Path $_.FullName ".git") } | Select-Object -First 100)
foreach ($repo in $repos) {
  $count++
  $ln = (git -C $repo.FullName config --local user.name 2>$null); $le = (git -C $repo.FullName config --local user.email 2>$null)
  if (-not $ln -and -not $le) {
    Emit "git" "repo_identity" "file" "pass" "repo=$($repo.FullName) local identity unset, inherits global" "$($repo.FullName):inherit"
  } elseif ($ln -eq $gn -and $le -eq $ge) {
    Emit "git" "repo_identity" "file" "pass" "repo=$($repo.FullName) local=$ln <$le> (same as global)" "$($repo.FullName):same"
  } else {
    $overrides++
    Emit "git" "repo_identity" "file" "fail" "repo=$($repo.FullName) LOCAL OVERRIDE local=$ln <$le> global=$gn <$ge>" "$($repo.FullName):$ln <$le>"
  }
  $br = (git -C $repo.FullName rev-parse --abbrev-ref HEAD 2>$null); if (-not $br) { $br = "unknown" }
  $dirty = @(git -C $repo.FullName status --porcelain 2>$null).Count
  $ab = (git -C $repo.FullName rev-list --left-right --count 'HEAD...@{upstream}' 2>$null); if (-not $ab) { $ab = "no-upstream" }
  Emit "git" "repo_drift" "file" "pass" "repo=$($repo.FullName) branch=$br dirty_files=$dirty ahead_behind=$ab" "$($repo.FullName):$br`:$dirty`:$ab"
}
Emit "git" "repo_sweep" "file" "pass" "root=$Root repos_scanned=$count local_overrides=$overrides" "${count}:${overrides}"
