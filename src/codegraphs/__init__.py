"""codegraphs: per-function control flow and data dependence graphs extracted with Joern.

Package layout
--------------
projects.py        registry of supported projects (repo, tags, language, source scope, py2 versions)
download.py        fetch release-tag source archives from GitHub; SourceTree reads them
joern.py           stage sources (+ 2to3 for Python 2), joern-parse, export via joern_scripts/
extract.py         convert Joern's export into graphs.jsonl.gz / metrics.csv / files.csv
graphio.py         reading/writing the output files (deterministic gzip, CSV, JSON)
viewer.py          per-version HTML viewer (templates/viewer.html), loads graphs.jsonl.gz
site.py            start page index.html + output/versions.js (navigation between viewers)
cli.py             command line: download | build | view | run | index | serve
"""

__version__ = "0.3.0"
