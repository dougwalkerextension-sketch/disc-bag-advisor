$ErrorActionPreference = 'Stop'
$appPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $appPython)) {
    $appPython = Join-Path $PSScriptRoot '.runtime/python.exe'
}
if (-not (Test-Path -LiteralPath $appPython)) {
    throw 'No local Python environment found. Create .venv and install requirements.txt. See README.md.'
}
& $appPython (Join-Path $PSScriptRoot 'app.py')
exit $LASTEXITCODE
