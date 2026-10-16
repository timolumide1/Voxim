# One-time install on Windows: a private Python 3.13 environment with the `voxim` command.
# Usage: powershell -ExecutionPolicy Bypass -File install.ps1 [-Screen]
param([switch]$Screen)
$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$HomeDir = if ($env:VOXIM_HOME) { $env:VOXIM_HOME } else { Join-Path $HOME ".voxim" }
$Venv = Join-Path $HomeDir "venv"
New-Item -ItemType Directory -Force -Path $HomeDir | Out-Null
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
  powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
  $env:Path = "$HOME\.local\bin;$env:Path"
}
if (-not (Test-Path "$Venv\Scripts\python.exe")) { uv venv -q --python 3.13 $Venv }
uv pip install -q --python "$Venv\Scripts\python.exe" --reinstall-package voxim $Here
if ($Screen) { uv pip install -q --python "$Venv\Scripts\python.exe" playwright; & "$Venv\Scripts\voxim.exe" setup --screen }
else { & "$Venv\Scripts\voxim.exe" setup }
Write-Host "Installed. The command is: $Venv\Scripts\voxim.exe"
