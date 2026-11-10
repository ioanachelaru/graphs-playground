# graphs-playground

This repository extracts a **control flow graph (CFG)** and a **data dependence graph (DDG)** for every function of several versions of two open-source projects. The graphs come from [Joern](https://joern.io), a widely used static-analysis tool. They are meant as features for defect prediction, to compare against the doc2vec, CodeBERT and SonarQube features used earlier in `doc2vec-experiments`.

- A **CFG** shows the order in which a function's parts can run: an edge A → B means B can run right after A. Branches (`if`, loops, `try`) create nodes with several successors.
- A **DDG** shows where values come from: an edge A → B labelled `x` means the value of `x` computed at A can be used at B. These are reaching definitions.

## Projects and scope

| Project | Language | Versions | Files analysed | Notes |
|---|---|---|---|---|
| Django | Python | `1.0`–`1.9`, `2.0`–`2.2`, `3.0`–`3.2`, `4.0`–`4.2`, `5.0`–`5.2` (22 versions; 1.10 and 1.11 are not included) | `django/` package only (no tests, docs or extras) | 1.0–1.9 are Python 2 code and are converted with 2to3 before parsing (see below) |
| ActiveMQ | Java | `5.0.0`, `5.1.0`, `5.2.0`, `5.3.0`, `5.8.0` | `<module>/src/main/java/**` of every Maven module (production code; tests excluded) | |

Versions, GitHub tags and scopes are defined in `src/codegraphs/projects.py`.

## How the graphs are built

For each project version, `python -m codegraphs run` does:

1. **Download.** The release-tag archive (`https://codeload.github.com/<repo>/zip/refs/tags/<tag>`) is saved as `sources/<project>-<version>.zip` (gitignored). Files are read straight from the zip.
2. **Stage.** The in-scope files are copied into a work directory outside the repository (default: the system temp folder, `codegraphs-work/`).
   - **Python 2 (Django 1.0–1.9):** Joern's Python frontend only understands Python 3. The staged copies are therefore converted with Python's `lib2to3` (all standard fixers, e.g. `print x` → `print(x)`, `except E, e` → `except E as e`).
   - **Line numbers:** for every file 2to3 changes, a line map (difflib alignment of the original and converted text) translates line numbers back to the original file. Unchanged lines map exactly. A rewritten line keeps its own number. In the rare case 2to3 splits or joins lines, the extra lines map to the nearest original line, so line numbers inside such a statement can be off by one.
3. **Parse.** `joern-parse <stage> --language pythonsrc|javasrc` builds Joern's code property graph (`cpg.bin`). The CFG and data-dependence edges come from Joern's default analyses.
4. **Export.** The Joern script `src/codegraphs/joern_scripts/export.sc` writes one JSON record per method, containing:
   - name, full name with signature, file, start/end line, modifiers and control-structure counts;
   - the method's CFG nodes and edges;
   - its data-dependence (`REACHING_DEF`) edges.
5. **Convert.** `src/codegraphs/extract.py` selects the real functions, renumbers the nodes, maps lines back (2to3 versions) and writes the outputs below. Joern's synthetic methods are skipped:
   - **Python:** `<module>`, `<body>`, `<metaClassAdapter>`, `<metaClassCallHandler>`, `<fakeNew>`, `<lambda>N`, and anything else whose name contains `<`.
   - **Java:** `<clinit>` (static initializers), compiler-generated default constructors (no end line) and abstract/interface methods (no body). Explicit constructors are kept, named `<init>`.

## How Joern's parser works

Joern builds a **code property graph (CPG)**: one graph that combines a program's abstract syntax tree (AST), its control flow graph and its program dependence graph (data and control dependences). The idea comes from Yamaguchi et al., *Modeling and Discovering Vulnerabilities with Code Property Graphs* (IEEE S&P 2014). Building it takes two stages:

1. **Language frontend** (source → AST). Each language has its own frontend, which parses every file without compiling or running it.
   - `pysrc2cpg` (`--language pythonsrc`) is a Python 3 parser.
   - `javasrc2cpg` (`--language javasrc`) parses Java source and resolves types where it can. Missing dependencies (ActiveMQ's third-party jars are not downloaded) only make some types unknown; they do not stop parsing.
   - A file that cannot be parsed is left out of the CPG. It shows up as `in_cpg = 0` in `files.csv`.
2. **Overlays** (AST → CFG → data flow). `joern-parse` then applies its default analysis passes (the log line "Applying default overlays"):
   - a control-flow pass orders the AST's expressions in evaluation order (operands before the operator, the condition before its branches, loop back-edges, jumps) and adds `CFG` edges;
   - a data-flow pass runs a **reaching-definitions** analysis over that CFG and adds `REACHING_DEF` edges from each node that defines or produces a value to the nodes that may use it. These edges are what `dfg_edges` contains.

The result is saved as `cpg.bin`. The export script then queries it with Joern's query language: for each method, its CFG nodes, CFG edges and `REACHING_DEF` edges.

## What a graph contains

Nodes are Joern's own CFG nodes. These are **expressions, not statements**: `x = a + 1` gives one node for `a + 1` and one for the assignment, plus nodes for `a` and `1`. Node `kind` values:

| kind | meaning |
|---|---|
| `METHOD` / `METHOD_RETURN` | entry and exit of the function |
| `METHOD_PARAMETER_IN` | a parameter |
| `CALL` | a call, including operators: `<operator>.assignment`, `<operator>.addition`, … |
| `IDENTIFIER`, `FIELD_IDENTIFIER`, `LITERAL` | a variable or field name, or a constant |
| `RETURN` | a `return` statement |
| `CONTROL_STRUCTURE`, `JUMP_TARGET`, `UNKNOWN` | `break`/`continue`/`raise` points, `case` labels, Joern-internal nodes |

Python `for` loops and comprehensions are desugared by Joern into iterator calls with temporaries (`tmp0 = xs.__iter__()`, `x = tmp0.__next__()`), so they appear as several nodes.


### Worked example

This function (from `tests/data/joern_export_sample.jsonl`, the recorded Joern export used by the tests):

```python
def f():                 # line 1
    try:
        x = load()       # line 3
        y = parse(x)     # line 4
    except Exception:
        log(x)           # line 6
```

becomes a record with 15 nodes:

| id | kind | line | text | | id | kind | line | text |
|---|---|---|---|---|---|---|---|---|
| 0 | METHOD | 1 | `f` | | 8 | IDENTIFIER | 3 | `load` |
| 1 | CALL | 3 | `x = load()` | | 9 | IDENTIFIER | 4 | `parse` |
| 2 | CALL | 4 | `y = parse(x)` | | 10 | IDENTIFIER | 4 | `x` |
| 3 | IDENTIFIER | 3 | `x` | | 11 | CALL | 6 | `log(x)` |
| 4 | CALL | 3 | `load()` | | 12 | IDENTIFIER | 6 | `log` |
| 5 | IDENTIFIER | 4 | `y` | | 13 | IDENTIFIER | 6 | `x` |
| 6 | CALL | 4 | `parse(x)` | | 14 | METHOD_RETURN | 1 | `RETURN` |
| 7 | BLOCK | 5 | `log(x)` (the `except` block) | | | | | |

How to read it:

- **CFG, in evaluation order:**
  - `0 → 3 → 8 → 4 → 1` evaluates `x`, `load`, `load()`, then the assignment `x = load()`;
  - `1 → 5 → 9 → 10 → 6 → 2` does the same for `y = parse(x)`;
  - from `2` there are two edges: `2 → 14` (normal exit) and `2 → 12` (into the `except` code: `log`, `x`, `log(x)`, then `7 → 14`).
  - This is the "exception only at the end of the try block" behaviour described under limitations.
- **DDG, for example:**
  - `3 → 10` labelled `x`: the `x` assigned on line 3 is the `x` read on line 4;
  - `10 → 13` labelled `x`: it is also the `x` read in `log(x)` on line 6;
  - `4 → 1` labelled `load()`: the call's value flows into the assignment;
  - edges into node 14 (`METHOD_RETURN`) mean "this value is still live at the exit".
- **Metrics row** for this function: `loc` 6, `cfg_nodes` 15, `cfg_edges` 15, `cyclomatic` 2 (one branch: normal path vs. `except`), `dfg_edges` 23, `n_calls` 5 (`x = load()`, `load()`, `y = parse(x)`, `parse(x)`, `log(x)`: the two assignments count as `<operator>.assignment` calls), `n_try` 1, `n_catch` 1.

## Outputs

Each version has a folder `output/<project>-<version>/`:

- **`graphs.jsonl.gz`**: gzip-compressed, one JSON object per function, in file and line order:
  - identity: `filepath`, `method_name`, `qualname` (`Class.method`; Java nested/anonymous types as `Outer$Inner`, `Runnable$0`), `signature` (Java parameter types), `full_name` (Joern's), `line_start`, `line_end`;
  - `nodes`: list of `{id, kind, line, text, vars_in, vars_out}`. `id` is the position in the list. `text` is the first line of the node's code. `vars_in` / `vars_out` are the labels of the DDG edges entering / leaving the node;
  - `cfg_edges`: `[src_id, dst_id, ""]` (Joern's CFG edges carry no labels);
  - `dfg_edges`: `[src_id, dst_id, label]`, the DDG edges. The label is usually the variable name. Joern also emits labels that are expressions (`n = len(zs)`), `<RET>` (value flowing to the return) or empty; they are kept unchanged.
- **`metrics.csv`**: one row per function, with the same identity columns plus:

  | column | meaning |
  |---|---|
  | `loc` | `line_end − line_start + 1` |
  | `cfg_nodes`, `cfg_edges` | size of the CFG: nodes with at least one CFG edge, and CFG edges. Parameters (which only carry DDG edges) and the entry nodes of nested function definitions are in `nodes` but not counted here |
  | `cyclomatic` | `cfg_edges − cfg_nodes + 2`. Short-circuit `and`/`or`/`&&`/`\|\|` create branches in Joern's CFG, so this is close to McCabe complexity. Against the independent tool lizard it gives Spearman ρ 0.986–0.996 and equal values for 91–97% of functions (see [Results](#results)) |
  | `dfg_edges`, `n_dfg_vars` | number of DDG edges and of distinct DDG labels |
  | `n_params` | parameters, including `self` (Python methods) and the implicit `this` (Java instance methods) |
  | `n_calls` | `CALL` nodes, **including operators** (assignments, arithmetic, comparisons), not just function calls |
  | `n_return` | explicit `return` statements |
  | `n_if`, `n_while`, `n_do`, `n_for`, `n_switch`, `n_try`, `n_catch`, `n_finally`, `n_throw`, `n_break`, `n_continue` | control structures of that type in the function itself (not in nested functions) |

- **`files.csv`**: one row per in-scope file:
  - `in_cpg`: 1 if Joern included the file in its graph; 0 means the frontend could not parse it, so it has no functions;
  - `n_functions`, `bytes`;
  - `py2to3_changed`: 1 if 2to3 modified the file.
- **`manifest.json`**: project, version, tag, scope, Joern frontend, whether 2to3 was used, and counts. The counts are files, files not in the CPG, files changed by 2to3, functions, and skipped synthetic/abstract methods. It also records the Joern, Java and Python versions and the build time.
- **`viewer.html`**: the graph viewer page (next section).

**Identifying a function:** use `filepath` + `line_start`, plus `signature` for Java overloads that start on the same line. `line_start` is where Joern places the function: the `def` line in Python and the line of the method name in Java, i.e. **after decorators and annotations**. Python `line_end` usually extends 1–2 lines past the body (Joern includes trailing blank lines); Java `line_end` is exact. Joining these to the method-level bug labels from `doc2vec-experiments` has not been checked yet.

## Viewing the graphs

- **Start page:** https://ioanachelaru.github.io/graphs-playground/. This needs GitHub Pages enabled for branch `main`, folder `/ (root)`; `.nojekyll` makes Pages serve the files as they are. The page lists every project and version with file and function counts, files Joern could not parse, and whether 2to3 was used.
- **Viewer:** each version's `viewer.html` (0.3–3.9 MB) embeds only the list of functions. When you open the first function, it downloads that version's `graphs.jsonl.gz` (6–13 MB) and decompresses it in the browser. This requires:
  - **HTTP.** Browsers do not let a local `file://` page read other files, so locally run `python -m codegraphs serve` and open http://localhost:8000/.
  - **A recent browser** with `DecompressionStream`: Chrome/Edge 80+, Firefox 113+, Safari 16.4+.
  - **Internet access** for the graph-drawing libraries (Cytoscape.js, dagre) loaded from unpkg.com.
- **Using the viewer:**
  - Filter the function list by file path or name (e.g. `models/base.py save`).
  - Switch between CFG + DDG, CFG only and DDG only. CFG edges are solid; DDG edges are dashed orange and labelled.
  - Hover a node for its kind, line and variables.
  - Use the version dropdown and the "all projects" link to move between viewers.
  - `viewer.html#123` opens function 123 directly.
  - Very large functions (over 1,000 nodes) take a few seconds to lay out.

## Reproducing everything

Requirements:

- Python 3.10–3.12 (`lib2to3` no longer exists in 3.13);
- a JDK 21, e.g. `conda install -c conda-forge openjdk=21`;
- Joern v4.0.679 (about 1.8 GB download; installed by the script below);
- about 8 GB of free RAM (Joern's default heap) and a few GB of disk for the work directory.

```powershell
python -m pip install -r requirements.txt
python scripts/install_joern.py                 # downloads Joern v4.0.679, checks its SHA-512, installs to tools/joern-cli (gitignored)
$env:JAVA_HOME = "C:\path\to\jdk-21"
.\run_pipeline.ps1 -Project django   -All       # or -Versions 1.0,1.1
.\run_pipeline.ps1 -Project activemq -All
```

`run_pipeline.ps1` sets `PYTHONPATH=src`, uses `tools/joern-cli` unless `JOERN_HOME` is set, and runs `python -m codegraphs run`. A full rebuild of all 27 versions took about 1 hour on a 14-core Windows laptop (Django 46 min, ActiveMQ 14 min).

Rebuilding gives byte-identical `graphs.jsonl.gz`, `metrics.csv` and `files.csv`: this was checked by building Django 1.0 and ActiveMQ 5.0.0 twice. Joern's output is deterministic, and the gzip files are written without timestamps.

Single steps, from the repository root:

```powershell
$env:PYTHONPATH = "src"
python -m codegraphs download --project django --versions 1.0     # --force re-downloads; --all = every version in projects.py
python -m codegraphs build    --project django --versions 1.0     # Joern; options --joern-home, --java-home, --work-dir, --keep-work
python -m codegraphs view     --project django --versions 1.0     # viewer.html, then refreshes index.html and output/versions.js
python -m codegraphs metrics  --project django --all              # recompute metrics.csv from graphs.jsonl.gz (no Joern)
python -m codegraphs index                                        # only index.html and output/versions.js
python -m codegraphs serve                                        # local web server for the viewers
python -m pytest                                                  # tests (Joern tests run only if JOERN_HOME and JAVA_HOME are set)
python scripts/crosscheck_lizard.py --project django --version 5.2   # compare `cyclomatic` with lizard (pip install lizard)
```

## Results

All 27 versions were built with Joern v4.0.679 (Java 21, Python 3.11). Joern parsed every in-scope file, so no file has `in_cpg = 0`; this includes the non-Python `app_template` files of Django 1.9.

| Project | Version | Files | Functions | Files not parsed | Files changed by 2to3 | Abstract methods skipped | `graphs.jsonl.gz` |
|---|---|---|---|---|---|---|---|
| django | 1.0 | 592 | 4,378 | 0 | 286 | – | 6.0 MB |
| django | 1.1 | 637 | 4,941 | 0 | 312 | – | 6.9 MB |
| django | 1.2 | 842 | 5,422 | 0 | 332 | – | 7.5 MB |
| django | 1.3 | 907 | 6,262 | 0 | 366 | – | 8.6 MB |
| django | 1.4 | 996 | 6,986 | 0 | 437 | – | 9.5 MB |
| django | 1.5 | 1,001 | 7,257 | 0 | 372 | – | 9.8 MB |
| django | 1.6 | 857 | 7,223 | 0 | 339 | – | 9.7 MB |
| django | 1.7 | 943 | 7,850 | 0 | 379 | – | 11.1 MB |
| django | 1.8 | 838 | 7,071 | 0 | 329 | – | 9.5 MB |
| django | 1.9 | 857 | 7,238 | 0 | 334 | – | 9.6 MB |
| django | 2.0 | 838 | 7,569 | 0 | – | – | 9.8 MB |
| django | 2.1 | 828 | 7,637 | 0 | – | – | 9.9 MB |
| django | 2.2 | 839 | 7,859 | 0 | – | – | 10.3 MB |
| django | 3.0 | 831 | 7,908 | 0 | – | – | 10.5 MB |
| django | 3.1 | 842 | 8,049 | 0 | – | – | 10.8 MB |
| django | 3.2 | 858 | 8,242 | 0 | – | – | 11.1 MB |
| django | 4.0 | 861 | 8,423 | 0 | – | – | 11.3 MB |
| django | 4.1 | 863 | 8,618 | 0 | – | – | 11.6 MB |
| django | 4.2 | 871 | 8,817 | 0 | – | – | 11.9 MB |
| django | 5.0 | 879 | 8,918 | 0 | – | – | 12.1 MB |
| django | 5.1 | 879 | 9,077 | 0 | – | – | 12.2 MB |
| django | 5.2 | 883 | 9,266 | 0 | – | – | 12.5 MB |
| activemq | 5.0.0 | 1,236 | 12,450 | 0 | – | 1071 | 7.0 MB |
| activemq | 5.1.0 | 1,280 | 13,070 | 0 | – | 1170 | 7.6 MB |
| activemq | 5.2.0 | 1,315 | 14,622 | 0 | – | 1233 | 8.3 MB |
| activemq | 5.3.0 | 1,480 | 15,712 | 0 | – | 1275 | 9.4 MB |
| activemq | 5.8.0 | 1,919 | 20,474 | 0 | – | 1609 | 12.8 MB |

**Cross-check of `cyclomatic` against lizard** (`scripts/crosscheck_lizard.py`; functions matched on file, start line and name):

| Version | Matched | Spearman ρ | Equal | Joern lower | Joern higher |
|---|---|---|---|---|---|
| Django 1.0 (2to3) | 4,328 / 4,378 (99%) | 0.996 | 94% | 2% | 4% |
| Django 5.2 | 9,266 / 9,266 (100%) | 0.986 | 91% | 4% | 5% |
| ActiveMQ 5.0.0 | 12,435 / 12,450 (100%) | 0.996 | 97% | 1% | 3% |
| ActiveMQ 5.8.0 | 19,135 / 20,474 (93%) | 0.992 | 96% | 1% | 3% |

Java constructors are matched on their class name, since lizard does not use `<init>`. Why 7% of ActiveMQ 5.8.0's methods find no lizard counterpart has not been investigated.

## Known limitations

These are Joern behaviours, checked on small examples (re-checked by `tests/test_graphs.py` when Joern is installed) and on the pilot versions:

- **`finally` is bypassed by jumps:** a `return` or `break` inside `try … finally` goes straight to the function exit or loop exit, so the `finally` code is not on that path. This applies to both languages.
- **Exceptions are modelled only at the end of the `try` block:** the only CFG edge into an `except`/`catch` handler comes from the last node of the try body, as if the exception were always raised after the whole body ran. Definitions made inside the try body therefore always reach the handler. A definition made *before* the try block does not reach it when the try body redefines the variable, even though at run time an early exception would make it reach (e.g. in `int x = 0; try { x = load(); … } catch (…) { log(x); }`, the `x = 0` does not reach `log(x)`).
- **Java static initializers:** anonymous classes declared inside `static { … }` blocks get no methods (41 methods in 4 files of ActiveMQ 5.0.0).
- **Python details:**
  - `line_end` usually runs 1–2 lines past the function body;
  - loops and comprehensions add desugared iterator nodes;
  - Django 1.x graphs describe the 2to3-converted code, not the exact original text.
- **Not followed:** calls into other functions. All graphs are intra-procedural.

Constructs Joern handles that matter for comparability:

- `match` statements;
- comprehension, lambda and `:=` scoping;
- labelled `break` out of Java blocks;
- Java overloads and multiple anonymous classes, which get distinct names.

## Repository files

| Path | What it is |
|---|---|
| `README.md` | this document |
| `index.html` | start page (GitHub Pages root): projects, versions, counts, links to the viewers. Generated by `codegraphs index` |
| `.nojekyll` | empty marker telling GitHub Pages to serve files as they are |
| `output/versions.js` | list of built versions and their counts, read by every viewer's version dropdown. Generated |
| `output/<project>-<version>/` | results for one version: `graphs.jsonl.gz`, `metrics.csv`, `files.csv`, `manifest.json`, `viewer.html` (see [Outputs](#outputs)). Generated, committed |
| `sources/` | downloaded release zips (`<project>-<version>.zip`). Not committed |
| `tools/joern-cli/` | Joern installation from `scripts/install_joern.py` (`VERSION` records the release). Not committed |
| `run_pipeline.ps1` | one-command run for a project: sets paths and calls `python -m codegraphs run` |
| `requirements.txt` | exact Python package versions used for the outputs |
| `pyproject.toml` | package definition for `pip install -e .` |
| `scripts/install_joern.py` | downloads the pinned Joern release, verifies its SHA-512 and installs it |
| `scripts/crosscheck_lizard.py` | compares `metrics.csv` `cyclomatic` with the independent tool lizard |
| `src/codegraphs/projects.py` | the projects: GitHub repo, tag format, versions, language, which files are in scope, which versions are Python 2 |
| `src/codegraphs/download.py` | downloads the release zips; `SourceTree` reads files from a zip in a fixed, OS-independent order |
| `src/codegraphs/joern.py` | finds Joern and Java; stages the in-scope files (and runs 2to3 with line maps); runs `joern-parse` and the export script |
| `src/codegraphs/joern_scripts/export.sc` | the Joern script (Scala) that writes one JSON record per method from `cpg.bin` |
| `src/codegraphs/extract.py` | turns the export into the outputs: which methods to keep, `qualname`, node renumbering, line mapping, metrics, `files.csv`, `manifest.json` |
| `src/codegraphs/graphio.py` | reading and writing the output files (deterministic gzip, CSV, JSON) |
| `src/codegraphs/viewer.py`, `templates/viewer.html` | builds each version's `viewer.html` (function list plus graph drawing) |
| `src/codegraphs/site.py` | builds `index.html` and `output/versions.js` |
| `src/codegraphs/cli.py`, `__main__.py` | the `python -m codegraphs download\|build\|view\|run\|metrics\|index\|serve` commands |
| `tests/test_graphs.py` | tests: conversion and naming on a recorded Joern export, scope rules, line maps, navigation; Joern integration tests for the review examples |
| `tests/data/joern_export_sample.jsonl` | the recorded Joern export used by the unit tests |
