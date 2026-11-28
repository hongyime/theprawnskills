# check-host-herdr.ps1 — host identity + Herdr live state. READ ONLY.
# Usage: scp to the Windows host, run, delete. Do NOT pipe via stdin (unreliable).
#   scp check-host-herdr.ps1 <host>:C:\Users\bryan\check-host-herdr.ps1
#   ssh <host> "powershell -NoProfile -ExecutionPolicy Bypass -File C:\Users\bryan\check-host-herdr.ps1"
#   ssh <host> "del C:\Users\bryan\check-host-herdr.ps1"
# Env: $env:EXPECTED_HOST, $env:MACHINE. Emits JSON lines, same schema as the .sh version.
# Status: pass | fail | unproven | not-covered | unavailable.
$Machine = if ($env:MACHINE) { $env:MACHINE } else { $env:COMPUTERNAME }
$ExpectedHost = $env:EXPECTED_HOST
$Hostname = $env:COMPUTERNAME
try { $TsIp = (tailscale ip -4 2>$null | Select-Object -First 1) } catch { $TsIp = $null }
if (-not $TsIp) { $TsIp = "UNAVAILABLE" }
$IdOk = ($ExpectedHost -and ($Hostname -eq $ExpectedHost))
function Emit($Check, $Field, $Type, $Status, $Evidence, $Value) {
  if (-not $IdOk -and $Status -ne "unproven") { $Status = "unproven" }
  $rec = [ordered]@{ machine = $Machine; check = $Check; field = $Field; type = $Type; status = $Status; evidence = $Evidence; value = $Value }
  Write-Output ($rec | ConvertTo-Json -Compress)
}
if ($IdOk) { $IdSt = "pass" } else { $IdSt = "unproven" }
Emit "host-identity" "hostname" "host" $IdSt "hostname=$Hostname tailscale_ip=$TsIp expected_host=$(if ($ExpectedHost) { $ExpectedHost } else { 'unset' })" $Hostname
Emit "host-identity" "tailscale_ip" "host" "pass" "tailscale_ip=$TsIp" $TsIp
$hc = Get-Command hc -ErrorAction SilentlyContinue
if (-not $hc) {
  Emit "herdr" "hc-present" "resolved" "not-covered" "hc.exe not installed on this machine" $null
  exit 0
}
try {
  $HcOut = hc ls --json 2>&1 | Out-String
  $d = $HcOut | ConvertFrom-Json
} catch {
  Emit "herdr" "hc-ls" "resolved" "unavailable" "hc ls failed or not JSON: $($_.Exception.Message.Substring(0, [Math]::Min(120, $_.Exception.Message.Length)))" $null
  exit 0
}
$conn = @($d.machines | Where-Object { $_.state -eq "connected" } | ForEach-Object { $_.name })
$live = @($d.terminals | Where-Object { $_.state -eq "live" })
$statuses = @{}
foreach ($t in $live) { $s = if ($t.status) { $t.status } else { "no-status" }; $statuses[$s] = ($statuses[$s] + 1) }
Emit "herdr" "machines_connected" "resolved" "pass" "connected=$($conn -join ',') hidden_finished=$($d.hidden_finished)" (($conn | Sort-Object) -join ",")
Emit "herdr" "terminals_live" "resolved" "pass" "live_terminals=$($live.Count) statuses=$(($statuses.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ',')" "$($live.Count)"
foreach ($t in $live) {
  Emit "herdr" "terminal" "resolved" "pass" "address=$($t.address) agent=$($t.agent) cwd=$($t.cwd) state=$($t.state) status=$($t.status) turn=$($t.turn) where=$($t.where)" $t.address
}
