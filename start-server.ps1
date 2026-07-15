Set-Location "$PSScriptRoot\server"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
# DATABASE_URL may be provided by the host. When it is unset, the backend uses
# the value saved in the settings center, then falls back to knowledge.db.
if (-not $env:FILE_STORAGE_ROOT) { $env:FILE_STORAGE_ROOT = "./storage" }
python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
