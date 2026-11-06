$ErrorActionPreference = 'Stop'
$appPython = Join-Path $PSScriptRoot '.venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $appPython)) {
    $appPython = Join-Path $PSScriptRoot '../.runtime/python.exe'
}
if (-not (Test-Path -LiteralPath $appPython)) {
    $appPython = Join-Path $PSScriptRoot '../DGRag/.runtime/python.exe'
}
if (-not (Test-Path -LiteralPath $appPython)) {
    throw 'Create a virtual environment and install requirements.txt first. See README.md.'
}
& $appPython (Join-Path $PSScriptRoot 'app.py')
