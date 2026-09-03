# One-click local start for Windows: API (8000) + Web (3000)
$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot

Write-Host "==> Checking prerequisites..." -ForegroundColor Cyan
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
  throw "Python not found. Install Python 3.10+ and reopen PowerShell."
}
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
  throw "Node.js not found. Install Node.js 18+ and reopen PowerShell."
}
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
  throw "npm not found. Reinstall Node.js 18+."
}

Write-Host "Python: $(python --version)"
Write-Host "Node:   $(node -v) / npm $(npm -v)"

# Free stale listeners if previous runs crashed
foreach ($port in 3000, 8000) {
  $conns = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
  foreach ($c in $conns) {
    try {
      Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue
      Write-Host "Freed port $port (PID $($c.OwningProcess))"
    } catch {}
  }
}

Write-Host "==> Starting API on http://127.0.0.1:8000" -ForegroundColor Cyan
$api = Start-Process powershell -PassThru -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", (Join-Path $Root "start-server.ps1")
)

Write-Host "==> Waiting for API..." -ForegroundColor Cyan
$apiReady = $false
for ($i = 0; $i -lt 60; $i++) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/v1/settings/public" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $apiReady = $true; break }
  } catch {}
  Start-Sleep -Seconds 1
}
if (-not $apiReady) {
  throw "API did not become ready on :8000. Check the API PowerShell window."
}
Write-Host "API ready." -ForegroundColor Green

Write-Host "==> Starting Web on http://localhost:3000" -ForegroundColor Cyan
$web = Start-Process powershell -PassThru -ArgumentList @(
  "-NoExit",
  "-ExecutionPolicy", "Bypass",
  "-File", (Join-Path $Root "start-web.ps1")
)

Write-Host "==> Waiting for Web..." -ForegroundColor Cyan
$webReady = $false
for ($i = 0; $i -lt 90; $i++) {
  try {
    $r = Invoke-WebRequest -Uri "http://127.0.0.1:3000/" -UseBasicParsing -TimeoutSec 2
    if ($r.StatusCode -eq 200) { $webReady = $true; break }
  } catch {}
  Start-Sleep -Seconds 1
}
if (-not $webReady) {
  throw "Web did not become ready on :3000. Check the Web PowerShell window."
}

Write-Host "Web ready." -ForegroundColor Green
Write-Host ""
Write-Host "Open: http://localhost:3000" -ForegroundColor Yellow
Write-Host "Login: 系统管理员 / ChangeMe123!" -ForegroundColor Yellow
Start-Process "http://localhost:3000/login"

Write-Host ""
Write-Host "API PID=$($api.Id)  Web PID=$($web.Id)"
Write-Host "Keep those two PowerShell windows open while using the app."
