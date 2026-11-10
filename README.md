# graphs-playground

Extracting control flow graphs (CFG) and data flow graphs (DFG) from Django source code (versions 1.0 to 4.2) for defect prediction. The graph-based features will be compared against the earlier doc2vec, CodeBERT and SonarQube features from `doc2vec-experiments`.

## Approach

- **Source:** Django release tags (`1.0`, `1.1`, … `4.2`), downloaded as GitHub archives into `sources/`.
- **Parser:** [tree-sitter-python](https://github.com/tree-sitter/tree-sitter-python). It was chosen because Django 1.x is Python 2 code (`print x`, `except E, e:`), which Python 3-only parsers (Joern's `pythonsrc` frontend, Python's `ast` module) cannot parse. Tree-sitter also keeps exact line numbers.
- **Graphs (per method):**
  - CFG: statement-level nodes, with edges for sequence, if/else, loops, try/except and return/raise.
  - DFG: variable definition → use edges (GraphCodeBERT-style).
- **Outputs (`output/django-<version>/`):**
  - graphs as JSON, keyed by `filepath`, `method_name`, `line_start` and `line_end`, so they can be joined to the method-level bug labels (`ast_level/django-<version>.csv`, column `has_bugs`);
  - a CSV of per-method graph metrics (node/edge counts, branches, loops, def-use edges).
- **Environment:** conda env with `tree-sitter`, `tree-sitter-python`, `networkx` and `pandas`.

## Log

- Started with Django 1.0 only. The plan is to extend to the remaining versions with the same script once 1.0 is validated.
- Django 1.0 source downloaded to `sources/django-1.0/` (956 `.py` files in the whole archive). It comes from `https://codeload.github.com/django/django/zip/refs/tags/1.0`; `git clone` was not usable in the sandbox.
- Graphs are built **only from the `django/` package subfolder** (tests, docs and extras are excluded). File paths are relative to the version root, e.g. `django/db/models/base.py`.
- Django 1.0 run: 592 files, 4,378 functions/methods (nested functions included, qualified as `Class.method`). One function failed to parse (`django/test/_doctest.py`, `DocTestRunner.__run`); it is kept and flagged with `has_parse_error=1`. The median function has 5 CFG nodes, cyclomatic complexity 1 and 4 def-use edges. `graphs.jsonl` is 8.4 MB.

## Reproduce

```powershell
python -m pip install -r requirements.txt     # Python 3.11; pinned versions
.\run_pipeline.ps1 -Versions 1.0              # or -Versions 1.0,1.1,...
```

`run_pipeline.ps1` runs three scripts:

1. `src/download_sources.py` downloads the tag archives. It skips versions that are already present; use `--force` to re-download, or `--all` for 1.0–4.2.
2. `src/build_graphs.py` writes `output/django-<version>/`:
   - `graphs.jsonl`: nodes, `cfg_edges`, `dfg_edges` and `free_vars` per function;
   - `metrics.csv`: per-function metrics;
   - `files.csv`: parse status per file;
   - `manifest.json`: counts and tool versions.

3. `src/build_viewer.py` writes `output/django-<version>/viewer.html`.

## Viewing the graphs

Open `output/django-<version>/viewer.html` in a browser. It needs internet access to load Cytoscape.js and dagre from unpkg.com.

- **Left panel:** all functions of that version. Filter by file path or qualified name (space-separated terms, e.g. `models/base.py save`).
- **Right panel:** the selected function's graph.
  - CFG edges are solid; the layout is a top-down flowchart.
  - DFG edges are dashed orange and labelled with the variable.
  - Toggle between CFG + DFG, CFG only and DFG only. Node positions stay fixed across modes.
  - Hover a node to see its defs and uses.
- **Links:** the URL hash (`viewer.html#123`) links to a function.
- Outputs (including the viewer) are committed; they can always be regenerated with `run_pipeline.ps1`.

## Graph details and limitations

- **CFG edge labels:** sequence `""`, `T`/`F` (branches), `back` (loop back-edge), `continue`, `exception` (try → handler), `return`/`raise` (→ EXIT).
- **Exceptions:** exception edges start at the `try` node, not at every statement in the try body (approximation).
- **DFG:** def-use edges from reaching definitions over the CFG. Parameters are defined at ENTRY. `self.x = ...` counts as a use of `self`, not a definition. Names with no reaching definition (globals, builtins, closure variables) are listed in `free_vars` instead of getting edges.
- **Scope:** intra-procedural only; calls are not followed.