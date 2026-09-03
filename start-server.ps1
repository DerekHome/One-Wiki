Set-Location "$PSScriptRoot\server"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt

# Local Windows default: SQLite. Override with DATABASE_URL for MySQL.
if (-not $env:DATABASE_URL) {
  $env:DATABASE_URL = "sqlite:///./knowledge.db"
}
if (-not $env:FILE_STORAGE_ROOT) {
  $env:FILE_STORAGE_ROOT = "./storage"
}

Write-Host "Starting One Wiki API on http://127.0.0.1:8000"
Write-Host "DATABASE_URL=$env:DATABASE_URL"
python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
