# Re-playable pipeline: download sources, build Joern CFG/DDG graphs, build the HTML viewers.
# Usage (from anywhere):
#   .\run_pipeline.ps1 -Project django   -Versions 1.0        (or -Versions 1.0,1.1 ; or -All)
#   .\run_pipeline.ps1 -Project activemq -All
# One-time setup:  python -m pip install -r requirements.txt ; python scripts/install_joern.py
# Needs JAVA_HOME pointing to a JDK 21; JOERN_HOME defaults to tools\joern-cli.
param(
    [ValidateSet("django", "activemq")][string]$Project = "django",
    [string[]]$Versions = @("1.0"),
    [switch]$All
)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
$env:PYTHONPATH = "$PSScriptRoot\src" + $(if ($env:PYTHONPATH) { ";$env:PYTHONPATH" } else { "" })
if (-not $env:JOERN_HOME) { $env:JOERN_HOME = "$PSScriptRoot\tools\joern-cli" }
if (-not $env:JAVA_HOME)  { throw "Set JAVA_HOME to a JDK 21 installation" }
if ($All) { python -m codegraphs run --project $Project --all }
else      { python -m codegraphs run --project $Project --versions @Versions }
exit $LASTEXITCODE
