Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "Starting Snapp Bot API on http://localhost:8000"
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd `"$root\Dashboard`"; python -m uvicorn api_server:app --host 0.0.0.0 --port 8000"
)

Start-Sleep -Seconds 1

Write-Host "Starting Streamlit dashboard on http://localhost:8501"
Start-Process -WindowStyle Normal -FilePath "powershell" -ArgumentList @(
  "-NoExit",
  "-Command",
  "cd `"$root\Dashboard`"; `$env:SNAPP_BOT_API_URL='http://localhost:8000'; python -m streamlit run App.py --server.port 8501"
)

Write-Host "Done. If you don't see the bot, refresh the dashboard page."

