# PowerShell helper to run the AI Triage Dashboard locally
# Usage: Open PowerShell in repository root and run: .\run_local.ps1

Write-Host "Starting AI Triage Dashboard..." -ForegroundColor Green
python -m streamlit run triage_ai.py
