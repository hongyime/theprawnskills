# check-resolved-config.ps1 — live resolved configuration. READ ONLY.
# Transport: scp to host, run, delete (see check-host-herdr.ps1 header).
# Env: $env:EXPECTED_HOST, $env:MACHINE. Emits JSON lines, same schema as check-resolved-config.py.
# Only allow-listed fields are emitted — never file contents, never secrets.
$Machine = if ($env:MACHINE) { $env:MACHINE } else { $env:COMPUTERNAME }
$ExpectedHost = $env:EXPECTED_HOST
$Hostname = $env:COMPUTERNAME
$IdOk = ($ExpectedHost -and ($Hostname -eq $ExpectedHost))
function Emit($Check, $Field, $Status, $Evidence, $Value) {
  if (-not $IdOk -and $Status -ne "unproven") { $Status = "unproven" }
  $rec = [ordered]@{ machine = $Machine; check = $Check; field = $Field; type = "resolved"; status = $Status; evidence = $Evidence; value = $Value }
  Write-Output ($rec | ConvertTo-Json -Compress)
}
function Strip-Jsonc($Text) {
  $out = New-Object System.Text.StringBuilder
  $inStr = $false; $esc = $false; $i = 0
  while ($i -lt $Text.Length) {
    $c = $Text[$i]
    if ($inStr) {
      [void]$out.Append($c)
      if ($esc) { $esc = $false } elseif ($c -eq '\') { $esc = $true } elseif ($c -eq '"') { $inStr = $false }
      $i++; continue
    }
    if ($c -eq '"') { $inStr = $true; [void]$out.Append($c); $i++; continue }
    if ($c -eq '/' -and ($i + 1) -lt $Text.Length -and $Text[$i + 1] -eq '/') { while ($i -lt $Text.Length -and $Text[$i] -ne "`n") { $i++ }; continue }
    if ($c -eq '/' -and ($i + 1) -lt $Text.Length -and $Text[$i + 1] -eq '*') { $i += 2; while (($i + 1) -lt $Text.Length -and -not ($Text[$i] -eq '*' -and $Text[$i + 1] -eq '/')) { $i++ }; $i += 2; continue }
    [void]$out.Append($c); $i++
  }
  return ($out.ToString() -replace ",\s*([}\]])", '$1')
}
try { $TsIp = (tailscale ip -4 2>$null | Select-Object -First 1) } catch { $TsIp = $null }
if (-not $TsIp) { $TsIp = "UNAVAILABLE" }
if ($IdOk) { $IdSt = "pass" } else { $IdSt = "unproven" }
Emit "host-identity" "hostname" $IdSt "hostname=$Hostname tailscale_ip=$TsIp expected_host=$(if ($ExpectedHost) { $ExpectedHost } else { 'unset' })" $Hostname

# --- Codex ---
$codexCfg = "$env:USERPROFILE\.codex\config.toml"
$model = $null; $reasoning = $null
if (Test-Path $codexCfg) {
  foreach ($line in (Get-Content $codexCfg)) {
    if ($line -match '^\s*model\s*=\s*"([^"]+)"') { $model = $Matches[1] }
    if ($line -match '^\s*model_reasoning_effort\s*=\s*"([^"]+)"') { $reasoning = $Matches[1] }
  }
  if ($model) { Emit "resolved" "codex.model" "pass" "codex config model=$model" $model } else { Emit "resolved" "codex.model" "unavailable" "codex config has no model line" $null }
  if ($reasoning) { Emit "resolved" "codex.reasoning" "pass" "codex config reasoning=$reasoning" $reasoning } else { Emit "resolved" "codex.reasoning" "unavailable" "codex config has no reasoning line" $null }
} else {
  Emit "resolved" "codex.model" "not-covered" "codex config.toml missing" $null
  Emit "resolved" "codex.reasoning" "not-covered" "codex config.toml missing" $null
}
$cache = "$env:USERPROFILE\.codex\models_cache.json"
if (Test-Path $cache) {
  try {
    $d = Get-Content $cache -Raw | ConvertFrom-Json
    $slugs = @($d.models | ForEach-Object { $_.slug } | Where-Object { $_ } | Sort-Object -Unique)
    Emit "resolved" "codex.catalog_slugs" "pass" "models_cache slugs=$($slugs -join ',') fetched_at=$($d.fetched_at)" ($slugs -join ",")
    if ($model) {
      if ($slugs -contains $model) { Emit "resolved" "codex.model_in_catalog" "pass" "configured model $model in live catalog: True" "True" }
      else { Emit "resolved" "codex.model_in_catalog" "fail" "configured model $model in live catalog: False" "False" }
    }
  } catch { Emit "resolved" "codex.catalog_slugs" "unavailable" "models_cache.json unreadable: $($_.Exception.Message)" $null }
} else {
  Emit "resolved" "codex.catalog_slugs" "not-covered" "models_cache.json missing (path not verified on this machine)" $null
}

# --- opencode ---
$oc = "$env:USERPROFILE\.config\opencode\opencode.jsonc"
if (Test-Path $oc) {
  try {
    $c = (Strip-Jsonc (Get-Content $oc -Raw)) | ConvertFrom-Json
    Emit "resolved" "opencode.model" "pass" "opencode model=$($c.model)" $c.model
    Emit "resolved" "opencode.small_model" "pass" "opencode small_model=$($c.small_model)" $c.small_model
    $dp = @($c.disabled_providers)
    Emit "resolved" "opencode.disabled_providers" "pass" "disabled_providers=$($dp -join ',')" (($dp | Sort-Object) -join ",")
    $provModels = @{}
    foreach ($p in $c.provider.PSObject.Properties) { $provModels[$p.Name] = @($p.Value.models.PSObject.Properties.Name | Sort-Object) }
    Emit "resolved" "opencode.provider_models" "pass" "provider models=$(($provModels.GetEnumerator() | ForEach-Object { "$($_.Key)=[$($_.Value -join ',')]" }) -join '; ')" $null
    $agentModels = @($c.agent.PSObject.Properties | ForEach-Object { $_.Value.model } | Where-Object { $_ })
    $deep = @($agentModels | Where-Object { $_ -like "deepseek/*" }).Count
    $other = @($agentModels | Where-Object { $_ -notlike "deepseek/*" } | Sort-Object -Unique)
    Emit "resolved" "opencode.primary_slots" "pass" "agent slots=$($agentModels.Count) deepseek=$deep other=$(if ($other) { $other -join ',' } else { 'none' })" "$deep/$($agentModels.Count)"
    if ($other) { Emit "resolved" "opencode.primary_other_models" "fail" "non-deepseek primary models=$($other -join ',')" ($other -join ",") }
    else { Emit "resolved" "opencode.primary_other_models" "pass" "non-deepseek primary models=none" "none" }
  } catch { Emit "resolved" "opencode.model" "unavailable" "opencode.jsonc unreadable: $($_.Exception.Message)" $null }
} else {
  foreach ($f in @("opencode.model","opencode.small_model","opencode.disabled_providers","opencode.provider_models","opencode.primary_slots","opencode.primary_other_models")) {
    Emit "resolved" $f "not-covered" "opencode.jsonc missing (opencode not installed)" $null
  }
}
$fb = "$env:USERPROFILE\.config\opencode\model-fallback.json"
if (Test-Path $fb) {
  try {
    $d = Get-Content $fb -Raw | ConvertFrom-Json
    $allFb = @(); foreach ($a in $d.agents.PSObject.Properties) { $allFb += @($a.Value.fallbackModels) }
    $allFb = @($allFb | Sort-Object -Unique)
    Emit "resolved" "opencode.fallback_enabled" "pass" "fallback enabled=$($d.enabled)" "$($d.enabled)"
    Emit "resolved" "opencode.fallback_models" "pass" "fallback models=$($allFb -join ',')" ($allFb -join ",")
    Emit "resolved" "opencode.fallback_depth" "pass" "maxFallbackDepth=$($d.defaults.maxFallbackDepth)" "$($d.defaults.maxFallbackDepth)"
    Emit "resolved" "opencode.fallback_triggers" "pass" "fallbackOn=$(($d.defaults.fallbackOn) -join ',')" (($d.defaults.fallbackOn) -join ",")
    $otherFb = @($allFb | Where-Object { $_ -notlike "opencode/deepseek*" })
    $otherFbStr = if ($otherFb) { $otherFb -join ',' } else { 'none' }
    Emit "resolved" "opencode.fallback_other_models" "pass" "non-deepseek fallback models=$otherFbStr" $otherFbStr
  } catch { Emit "resolved" "opencode.fallback_models" "unavailable" "model-fallback.json unreadable: $($_.Exception.Message)" $null }
} else {
  Emit "resolved" "opencode.fallback_models" "not-covered" "model-fallback.json missing" $null
}

# --- omo.jsonc ---
$omo = "$env:USERPROFILE\.omo\omo.jsonc"
if (Test-Path $omo) {
  try {
    $d = (Strip-Jsonc (Get-Content $omo -Raw)) | ConvertFrom-Json
    $models = @(); $fallbacks = @(); $disabled = @()
    function Collect($Obj, $Key, $Acc) {
      if ($Obj -is [PSCustomObject]) {
        foreach ($p in $Obj.PSObject.Properties) {
          if ($p.Name -eq $Key -and $p.Value -is [Array]) { $Acc += @($p.Value) }
          Collect $p.Value $Key $Acc
        }
      } elseif ($Obj -is [Array]) { foreach ($v in $Obj) { Collect $v $Key $Acc } }
      return $Acc
    }
    $models = @(Collect $d "models" @() | Sort-Object -Unique)
    $fallbacks = @(Collect $d "fallback_models" @() | Sort-Object -Unique)
    $disabled = @(Collect $d "disabled_providers" @() | Sort-Object -Unique)
    Emit "resolved" "omo.models" "pass" "omo models=$($models -join ',')" ($models -join ",")
    Emit "resolved" "omo.fallback_models" "pass" "omo fallback_models=$($fallbacks -join ',')" ($fallbacks -join ",")
    Emit "resolved" "omo.disabled_providers" "pass" "omo disabled_providers=$($disabled -join ',')" ($disabled -join ",")
  } catch { Emit "resolved" "omo.models" "unavailable" "omo.jsonc unreadable: $($_.Exception.Message)" $null }
} else {
  foreach ($f in @("omo.models","omo.fallback_models","omo.disabled_providers")) {
    Emit "resolved" $f "not-covered" "omo.jsonc missing" $null
  }
}
