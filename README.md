# graphs-playground

Extracting control flow graphs (CFG) and data flow graphs (DFG) from source code for defect prediction. The graph-based features will be compared against the earlier doc2vec, CodeBERT and SonarQube features from `doc2vec-experiments`.

Projects:

| Project | Language | Versions | Code used for graphs |
|---|---|---|---|
| Django | Python | `1.0`–`1.9`, `2.0`–`2.2`, `3.0`–`3.2`, `4.0`–`4.2`, `5.0`–`5.2` (22 versions; 1.10 and 1.11 not included) | `django/` package only (no tests or docs) |
| ActiveMQ | Java | `5.0.0`, `5.1.0`, `5.2.0`, `5.3.0`, `5.8.0` | `<module>/src/main/java` of every module (production code; tests excluded) |

## Approach

- **Source:** GitHub release-tag archives kept as zips in `sources/<project>-<version>.zip` (gitignored) and read directly, without extraction. Folders extracted by earlier runs (`sources/<project>-<version>/`) are still read.
  - Django tags are `1.0`, `1.1`, … `4.2`; ActiveMQ tags are `activemq-<version>`.
  - Archives come from `https://codeload.github.com/<repo>/zip/refs/tags/<tag>`, because `git clone` was not usable in the sandbox.
- **Parsers:** [tree-sitter](https://tree-sitter.github.io/) with the Python and Java grammars.
  - Django 1.x is Python 2 code (`print x`, `except E, e:`), which Python 3-only parsers (Joern's `pythonsrc`, Python's `ast`) cannot parse.
  - Tree-sitter keeps exact line numbers and needs no compilation or JDK.
- **Graphs (per function/method):**
  - CFG: statement-level nodes.
  - DFG: variable definition → use edges from reaching definitions over the CFG.
  - Both languages share the same model, data-flow code and output format.
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
- **Refactor:** the per-language scripts became the `codegraphs` package (shared core plus one module per language) with unit tests. Re-running it gave the same outputs; only line endings changed (now LF everywhere).
- **ActiveMQ 5.1.0–5.8.0:** 1,280–1,919 files and 13,107–20,500 methods; no parse errors.
- **All Django versions (22):** built in about 6 minutes.
  - Size grows from 592 files / 4,378 functions (1.0) to 883 files / 9,266 functions (5.2).
  - Parse errors in 1.1–1.4: 2 functions, both in bundled Python 2 code (`django/test/_doctest.py` `DocTestRunner.__run` and `django/utils/simplejson/encoder.py` `_make_iterencode`).
  - 1.9: one file error in `django/conf/app_template/apps.py`. This is a project template with `{{ }}` placeholders, not valid Python, and contains no functions.
  - Versions 1.5–5.2 otherwise have no errors.
- **Downloader:** sources are no longer extracted. On the sandboxed Windows machine, creating thousands of folders hit transient file-system errors (a just-created folder was briefly invisible) and became very slow. Reading straight from the zip gives byte-identical outputs.

## Reproduce

```powershell
python -m pip install -r requirements.txt                 # Python 3.11; exact versions used for output/
.\run_pipeline.ps1 -Project django   -Versions 1.0        # or -Versions 1.0,1.1,... or -All
.\run_pipeline.ps1 -Project activemq -Versions 5.0.0
```

`run_pipeline.ps1` runs `python -m codegraphs run`, which does three steps for each version: **download**, then **build**, then **view**. Each step can also be run on its own, from the repo root:

```powershell
$env:PYTHONPATH = "src"        # or: pip install -e .[dev]  (then just `codegraphs ...`)
python -m codegraphs download --project django --versions 1.0     # --force to re-download, --all for every version
python -m codegraphs build    --project django --versions 1.0
python -m codegraphs view     --project django --versions 1.0     # also refreshes index.html + output/versions.js
python -m codegraphs index                                        # navigation only
python -m pytest              # graph-construction tests
```

`build` writes `output/<project>-<version>/`:

- `graphs.jsonl`: nodes, `cfg_edges`, `dfg_edges` and `free_vars` per function;
- `metrics.csv`: per-function metrics. Java adds `n_switch`, `n_case` and `n_sync`;
- `files.csv`: parse status per file;
- `manifest.json`: scope, counts and tool versions.

`view` writes `viewer.html` into the same folder. Text outputs use LF line endings on every OS, so runs on different machines give identical files.

## Code structure

```
src/codegraphs/
  projects.py       project registry: GitHub repo, tag format, versions, language, source scope
  download.py       release-tag archive download
  languages/
    base.py         Language interface (parser, iter_functions, build_cfg, metric columns)
    python.py       Python front-end (CFG builder + def/use rules)
    java.py         Java front-end
  cfg.py            CFG builder base class (node/edge storage, ENTRY/EXIT)
  dataflow.py       reaching definitions -> DFG edges (shared by all languages)
  metrics.py        per-function metrics
  extract.py        per-version driver: files -> graphs -> output files
  viewer.py         HTML viewer (template in templates/viewer.html)
  site.py           start page index.html + output/versions.js (navigation between viewers)
  cli.py            `python -m codegraphs download|build|view|run|index`
tests/test_graphs.py  expected CFG/DFG for one sample function per language, project scopes
```

**Adding a project:** add a `Project` entry in `projects.py`. **Adding a language:** implement `Language` in `languages/<lang>.py` and register it in `languages/__init__.py`.

## Viewing the graphs

**Start page:** https://ioanachelaru.github.io/graphs-playground/ (GitHub Pages, branch `main`, folder `/ (root)`), or `index.html` locally. It lists every project and version with file, function and parse-error counts, and links to each viewer.

Each viewer has a **version** dropdown (switch to another version of the same project) and an **all projects** link back to the start page. The navigation comes from `output/versions.js`, which every viewer loads, so adding a version only needs `python -m codegraphs index` (run automatically by `view` and `run`), not a rebuild of the existing viewers.

A single viewer is at `output/<project>-<version>/viewer.html`. The page needs internet access to load Cytoscape.js and dagre from unpkg.com.

- **Left panel:** all functions of that version. Filter by file path or qualified name (space-separated terms, e.g. `models/base.py save`).
- **Right panel:** the selected function's graph.
  - CFG edges are solid; the layout is a top-down flowchart.
  - DFG edges are dashed orange and labelled with the variable.
  - Toggle between CFG + DFG, CFG only and DFG only. Node positions stay fixed across modes.
  - Hover a node to see its defs and uses.
- **Links:** the URL hash (`viewer.html#123`) links to a function.
- Outputs (including the viewers) are committed; `run_pipeline.ps1` can always regenerate them.

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
