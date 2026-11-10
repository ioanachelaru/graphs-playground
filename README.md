# graphs-playground

Extracting control flow graphs (CFG) and data flow graphs (DFG) from source code for defect prediction. The graph-based features will be compared against the earlier doc2vec, CodeBERT and SonarQube features from `doc2vec-experiments`.

Projects:

| Project | Language | Versions | Code used for graphs |
|---|---|---|---|
| Django | Python | `1.0` … `4.2` (done: 1.0) | `django/` package only (no tests or docs) |
| ActiveMQ | Java | `5.0.0` (done) | `<module>/src/main/java` of every module (production code; tests excluded) |

## Approach

- **Source:** GitHub release-tag archives downloaded into `sources/<project>-<version>/` (gitignored).
  - Django tags are `1.0`, `1.1`, … `4.2`; ActiveMQ tags are `activemq-<version>`.
  - Archives come from `https://codeload.github.com/<repo>/zip/refs/tags/<tag>`, because `git clone` was not usable in the sandbox.
- **Parsers:** [tree-sitter](https://tree-sitter.github.io/) with the Python and Java grammars.
  - Django 1.x is Python 2 code (`print x`, `except E, e:`), which Python 3-only parsers (Joern's `pythonsrc`, Python's `ast`) cannot parse.
  - Tree-sitter keeps exact line numbers and needs no compilation or JDK.
- **Graphs (per function/method):**
  - CFG: statement-level nodes.
  - DFG: variable definition → use edges from reaching definitions over the CFG.
  - Both languages share the same model and output format (`build_graphs_java.py` reuses the reaching-definitions code).
- **Outputs (`output/<project>-<version>/`):** graphs and metrics, keyed by `filepath`, `method_name`, `qualname`, `line_start` and `line_end`, so they can be joined to method-level bug labels (or pooled per file for file-level labels).

## Log

- **Django 1.0:** 592 files, 4,378 functions/methods (nested functions included, qualified as `Class.method`).
  - One function failed to parse (`django/test/_doctest.py`, `DocTestRunner.__run`); it is kept and flagged with `has_parse_error=1`.
  - The median function has 5 CFG nodes, cyclomatic complexity 1 and 4 def-use edges.
  - `graphs.jsonl` is 8.4 MB.
- **ActiveMQ 5.0.0:** 1,236 files from 15 modules' `src/main/java`, giving 12,485 methods/constructors (including nested, local and anonymous classes, e.g. `Outer.method.<anon>.run`). There were no parse errors.
  - 1,071 abstract/interface methods have no body; they get no graph and are counted in the manifest.
  - The median method has 3 CFG nodes, because there are many getters and setters.
  - `graphs.jsonl` is 17.3 MB.
- Calcite was considered but dropped.

## Reproduce

```powershell
python -m pip install -r requirements.txt                 # Python 3.11; pinned versions
.\run_pipeline.ps1 -Project django   -Versions 1.0        # or -Versions 1.0,1.1,...
.\run_pipeline.ps1 -Project activemq -Versions 5.0.0
```

`run_pipeline.ps1` runs three steps:

1. `src/download_sources.py --project <p> --versions ...` downloads the tag archives. It skips versions that are already present; use `--force` to re-download, or `--all` for every known version.
2. The graph builder writes `output/<project>-<version>/`:
   - `src/build_graphs.py` for Django; `src/build_graphs_java.py --project activemq` for Java.
   - `graphs.jsonl`: nodes, `cfg_edges`, `dfg_edges` and `free_vars` per function.
   - `metrics.csv`: per-function metrics. Java adds `n_switch`, `n_case` and `n_sync` columns.
   - `files.csv`: parse status per file.
   - `manifest.json`: counts and tool versions.
3. `src/build_viewer.py --project <p> --versions ...` writes `output/<project>-<version>/viewer.html`.

## Viewing the graphs

Open `output/<project>-<version>/viewer.html` in a browser, or via GitHub Pages: `https://ioanachelaru.github.io/graphs-playground/output/<project>-<version>/viewer.html`. The page needs internet access to load Cytoscape.js and dagre from unpkg.com.

- **Left panel:** all functions of that version. Filter by file path or qualified name (space-separated terms, e.g. `models/base.py save`).
- **Right panel:** the selected function's graph.
  - CFG edges are solid; the layout is a top-down flowchart.
  - DFG edges are dashed orange and labelled with the variable.
  - Toggle between CFG + DFG, CFG only and DFG only. Node positions stay fixed across modes.
  - Hover a node to see its defs and uses.
- **Links:** the URL hash (`viewer.html#123`) links to a function.
- Outputs (including the viewers) are committed; they can always be regenerated with `run_pipeline.ps1`.

## Graph details and limitations

- **CFG edge labels:** sequence `""`, `T`/`F` (branches), `back` (loop back-edge), `continue`, `exception` (try → handler), `return`/`raise` (→ EXIT; Java `throw` uses `raise`).
  - Java adds `case` (switch → case group) and `no-match` (switch without `default`).
- **Java control flow:**
  - Classic `for` runs init → condition → body → update → condition.
  - `do-while` runs the body before the condition.
  - Switch cases fall through until a `break`.
  - Labelled `break`/`continue` jump to the labelled loop.
- **Exceptions:** exception edges start at the `try` node, not at every statement in the try body (approximation).
- **DFG:**
  - Parameters are defined at ENTRY.
  - `self.x = ...` / `this.x = ...` / `a[i] = ...` count as uses, not definitions.
  - Names with no reaching definition (globals, builtins, Java fields, closure variables) are listed in `free_vars` instead of getting edges.
  - Anonymous-class bodies are not part of the enclosing method's DFG; they are separate graphs.
- **Scope:** intra-procedural only; calls are not followed.
