Set-Location "$PSScriptRoot\web"
if (-not (Test-Path "node_modules")) { npm install }

if (-not (Test-Path ".env.local")) {
  @"
NEXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
"@ | Set-Content -Path ".env.local" -Encoding utf8
}

$env:NEXT_PUBLIC_API_BASE = "http://localhost:8000/api/v1"
Write-Host "Starting One Wiki Web on http://localhost:3000"
npm run dev
