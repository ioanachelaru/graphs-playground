"""codegraphs: per-function control flow and data flow graphs from source code (tree-sitter).

Package layout
--------------
projects.py        registry of supported projects (repo, tags, language, source scope)
download.py        fetch release-tag source archives from GitHub
syntax.py          small tree-sitter helpers shared by all languages
cfg.py             language-independent CFG builder base class
dataflow.py        reaching definitions -> def-use (DFG) edges
metrics.py         per-function graph metrics
languages/         one module per language (python, java) + the Language interface
extract.py         per-version driver: parse files, build graphs, write outputs
viewer.py          single-page HTML viewer (templates/viewer.html)
cli.py             command line: download | build | view | run
"""

__version__ = "0.2.0"
