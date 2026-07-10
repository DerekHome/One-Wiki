Set-Location "$PSScriptRoot\web"
if (-not (Test-Path "node_modules")) { npm install }
$env:NEXT_PUBLIC_API_BASE = "http://127.0.0.1:8000/api/v1"
npm run dev
