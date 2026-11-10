# Re-playable pipeline: download Django sources and build CFG/DFG graphs.
# Usage (from repo root):  .\run_pipeline.ps1 -Versions 1.0      or  .\run_pipeline.ps1 -Versions 1.0,1.1
param([string[]]$Versions = @("1.0"))
$ErrorActionPreference = "Stop"
# One-time setup (Python 3.11):  python -m pip install -r requirements.txt
python src/download_sources.py --versions @Versions
python src/build_graphs.py --versions @Versions
python src/build_viewer.py --versions @Versions
