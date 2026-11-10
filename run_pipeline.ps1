# Re-playable pipeline: download sources, build CFG/DFG graphs, build the HTML viewer.
# Usage (from anywhere):
#   .\run_pipeline.ps1 -Project django   -Versions 1.0        (or -Versions 1.0,1.1 ; or -All)
#   .\run_pipeline.ps1 -Project activemq -Versions 5.0.0
# One-time setup (Python 3.11):  python -m pip install -r requirements.txt
param(
    [ValidateSet("django", "activemq")][string]$Project = "django",
    [string[]]$Versions = @("1.0"),
    [switch]$All
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = "$PSScriptRoot\src" + $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" } else { "" })
if ($All) { python -m codegraphs run --project $Project --all }
else      { python -m codegraphs run --project $Project --versions @Versions }
exit $LASTEXITCODE
