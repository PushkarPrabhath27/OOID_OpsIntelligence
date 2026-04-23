# OOID Native Startup Script for Windows
# Uses the specified Python 3.10 installation

Write-Host "🚀 Initializing OOID Native Environment..." -ForegroundColor Cyan

$PYTHON_EXE = "C:\Users\pushk\python310\python.exe"

# 1. Install Dependencies
Write-Host "📦 Installing dependencies from requirements.txt..." -ForegroundColor Yellow
& $PYTHON_EXE -m pip install -r requirements.txt --user

# 2. Set Python Path
$env:PYTHONPATH = ".;$PWD\src"

# 3. Check for .env
if (-not (Test-Path .env)) {
    Write-Host "⚠️ .env not found. Creating from example..." -ForegroundColor Gray
    Copy-Item .env.example .env
}

# 4. Run Dashboard
Write-Host "🔥 Launching OOID Dashboard..." -ForegroundColor Green
& $PYTHON_EXE -m streamlit run src/dashboard/app.py
