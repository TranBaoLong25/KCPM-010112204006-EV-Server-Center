# Run black-box tests
Write-Host "Running black-box tests..."
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -vv tests -m blackbox

# Run white-box tests
Write-Host "Running white-box tests..."
C:/Users/ADMIN/AppData/Local/Programs/Python/Python313/python.exe -m pytest -vv tests -m whitebox
