Set-Location "$PSScriptRoot\server"
if (-not (Test-Path ".venv")) { python -m venv .venv }
& ".\.venv\Scripts\Activate.ps1"
pip install -r requirements.txt
$env:DATABASE_URL = "sqlite:///$($PSScriptRoot.Replace('\\','/'))/knowledge.db"
$env:FILE_STORAGE_ROOT = "./storage"
python -m uvicorn app.main:app --reload --reload-dir app --host 127.0.0.1 --port 8000
