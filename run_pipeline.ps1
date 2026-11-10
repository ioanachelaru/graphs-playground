# Re-playable pipeline: download sources, build CFG/DFG graphs, build the HTML viewer.
# Usage (from repo root):
#   .\run_pipeline.ps1 -Project django   -Versions 1.0        (or -Versions 1.0,1.1)
#   .\run_pipeline.ps1 -Project activemq -Versions 5.0.0
# One-time setup (Python 3.11):  python -m pip install -r requirements.txt
param([string]$Project = "django", [string[]]$Versions = @("1.0"))
$ErrorActionPreference = "Stop"
python src/download_sources.py --project $Project --versions @Versions
if ($Project -eq "django") { python src/build_graphs.py --versions @Versions }
else                       { python src/build_graphs_java.py --project $Project --versions @Versions }
python src/build_viewer.py --project $Project --versions @Versions
