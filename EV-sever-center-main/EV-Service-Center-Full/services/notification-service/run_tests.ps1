$ErrorActionPreference = 'Stop'

$pythonExe = "C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Host "Python interpreter not found at $pythonExe"
    exit 1
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    & $pythonExe -m venv .venv
}

$venvPython = ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Virtual environment was not created successfully."
    exit 1
}

Write-Host "Installing requirements..."
& $venvPython -m pip install --upgrade pip

# Install runtime deps except the PostgreSQL driver, which is unnecessary for sqlite-backed tests on Windows.
$reqs = Get-Content requirements.txt | Where-Object {
    $_ -and $_.Trim() -and $_.Trim() -notmatch '^#' -and $_ -notmatch 'psycopg2-binary'
}

foreach ($req in $reqs) {
    Write-Host "Installing $req"
    & $venvPython -m pip install $req
}

& $venvPython -m pip install pytest

Write-Host "Running notification tests..."
New-Item -ItemType Directory -Path "test_results" -Force | Out-Null
$logPath = Join-Path "test_results" "pytest-output.txt"
$xmlReportPath = Join-Path "test_results" "notification-results.xml"

& $venvPython -m pytest -vv tests/test_notification_service.py --junitxml=$xmlReportPath 2>&1 | Tee-Object -FilePath $logPath
$exitCode = $LASTEXITCODE

$reportPath = Join-Path "test_results" "test_summary.txt"
$status = if ($exitCode -eq 0) { "SUCCESS" } else { "FAILED" }
@"
Notification Service Test Summary
Generated: $(Get-Date -Format o)
Exit code: $exitCode
Status: $status
JUnit XML: $xmlReportPath
Pytest log: $logPath
"@ | Set-Content -Path $reportPath
Write-Host "Saved test summary to $reportPath"
Write-Host "Saved pytest output to $logPath"

if ($exitCode -ne 0) {
    exit $exitCode
}
