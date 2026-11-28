# check-versions-hashes.ps1 — tool versions + config-file hashes. READ ONLY.
# Transport: scp to host, run, delete (see check-host-herdr.ps1 header).
# Env: $env:EXPECTED_HOST, $env:MACHINE. Emits JSON lines, same schema as the .sh version.
# Versions use FileVersion, never --version: some tools hang on --version over SSH.
$Machine = if ($env:MACHINE) { $env:MACHINE } else { $env:COMPUTERNAME }
$ExpectedHost = $env:EXPECTED_HOST
$IdOk = ($ExpectedHost -and ($env:COMPUTERNAME -eq $ExpectedHost))
function Emit($Check, $Field, $Type, $Status, $Evidence, $Value) {
  if (-not $IdOk -and $Status -ne "unproven") { $Status = "unproven" }
  $rec = [ordered]@{ machine = $Machine; check = $Check; field = $Field; type = $Type; status = $Status; evidence = $Evidence; value = $Value }
  Write-Output ($rec | ConvertTo-Json -Compress)
}
foreach ($t in @("codex","agy","opencode","hc","herdr","strix","kiro","gh")) {
  $c = Get-Command $t -ErrorAction SilentlyContinue
  if (-not $c) { Emit "version" $t "version" "not-covered" "$t not installed" $null; continue }
  $fv = (Get-Item $c.Source -ErrorAction SilentlyContinue).VersionInfo.FileVersion
  if ($fv) { Emit "version" $t "version" "pass" "$($c.Source) | fileversion=$fv" $fv }
  # Wrapper (.ps1/.cmd) has no FileVersion: report present, value null so the
  # differ skips it instead of diffing a path against a version string.
  else { Emit "version" $t "version" "pass" "$($c.Source) | present (wrapper, version not probed)" $null }
}
function HashFile($Field, $Path) {
  if (-not (Test-Path $Path)) { Emit "file" $Field "file" "not-covered" "$Path missing" $null; return }
  $h = (Get-FileHash $Path -Algorithm SHA256).Hash
  $b = (Get-Item $Path).Length
  Emit "file" $Field "file" "pass" "$Path sha256=$h bytes=$b" $h
}
HashFile "opencode_jsonc" "$env:USERPROFILE\.config\opencode\opencode.jsonc"
HashFile "model_fallback" "$env:USERPROFILE\.config\opencode\model-fallback.json"
HashFile "codex_config" "$env:USERPROFILE\.codex\config.toml"
HashFile "omo_jsonc" "$env:USERPROFILE\.omo\omo.jsonc"
HashFile "library_json" "$env:USERPROFILE\.config\theprawnskills\library.json"
HashFile "forge_agents" "$env:USERPROFILE\Projects\forge\AGENTS.md"
$skillsDir = "$env:USERPROFILE\.agents\skills"
if (Test-Path $skillsDir) {
  $n = (Get-ChildItem $skillsDir -ErrorAction SilentlyContinue | Measure-Object).Count
  Emit "file" "skills_dir_entries" "file" "pass" "$skillsDir entries=$n" "$n"
} else {
  Emit "file" "skills_dir_entries" "file" "not-covered" "$skillsDir missing" $null
}
