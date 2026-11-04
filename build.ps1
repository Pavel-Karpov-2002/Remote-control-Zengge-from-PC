$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
& ./.venv/Scripts/python.exe -m unittest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed' }
& ./.venv/Scripts/python.exe -m PyInstaller --noconfirm --onefile --windowed --name ZenggeMusic --collect-all pyaudiowpatch --hidden-import proctap._native app.py
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
