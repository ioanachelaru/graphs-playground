"""Build graphs for one project version and write output/<project>-<version>/.

graphs.jsonl   one JSON object per function: identifiers, nodes, cfg_edges, dfg_edges, free_vars
metrics.csv    one row per function (see codegraphs.metrics)
files.csv      one row per source file: n_functions, n_error_nodes, bytes
manifest.json  scope, counts, tool versions, timestamp

Text outputs use "\\n" line endings on every OS (CSV files use the csv module's standard "\\r\\n"),
so runs on different machines produce identical files.
"""
import csv
import datetime as dt
import json
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

from codegraphs import dataflow, metrics
from codegraphs.download import SourceTree
from codegraphs.languages import get_language
from codegraphs.projects import Project
from codegraphs.syntax import count_errors


def path_order(rel: str):
    """Sort key for source paths: case-insensitive per path component, identical on every OS
    (matches Windows Path ordering used for the first outputs)."""
    return [part.lower() for part in rel.split("/")]


def source_files(tree: SourceTree, project: Project) -> list:
    return sorted((rel for rel in tree.paths() if project.include(rel)), key=path_order)


def _write_csv(path: Path, rows: list) -> None:
    with open(path, "w", newline="", encoding="utf8") as fh:
        if not rows:
            return
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def build(project: Project, version: str, sources_dir: Path, output_dir: Path) -> dict:
    lang = get_language(project.language)
    try:
        sources = SourceTree(sources_dir, project, version)
    except FileNotFoundError as e:
        raise SystemExit(f"{e}; run: python -m codegraphs download "
                         f"--project {project.name} --versions {version}")
    out = Path(output_dir) / f"{project.name}-{version}"
    out.mkdir(parents=True, exist_ok=True)

    files = source_files(sources, project)
    mrows, frows, n_bodiless = [], [], 0
    with sources, open(out / "graphs.jsonl", "w", encoding="utf8", newline="\n") as gj:
        for rel in files:
            src = sources.read(rel)
            tree = lang.parse(src)
            nf = 0
            for fn, qual, start in lang.iter_functions(tree.root_node):
                g = lang.build_cfg(fn)
                if g is None:
                    n_bodiless += 1
                    continue
                dfg, free = dataflow.def_use_edges(g)
                ident = {
                    "version": version, "filepath": rel,
                    "method_name": qual.split(".")[-1], "qualname": qual,
                    "line_start": start.start_point[0] + 1, "line_end": fn.end_point[0] + 1,
                }
                gj.write(json.dumps({
                    **ident, "has_parse_error": bool(fn.has_error),
                    "nodes": g.nodes, "cfg_edges": sorted(g.edges),
                    "dfg_edges": dfg, "free_vars": free,
                }) + "\n")
                mrows.append({**ident, **metrics.compute(g, dfg, free, fn, start, lang.kind_counts)})
                nf += 1
            frows.append({"version": version, "filepath": rel, "n_functions": nf,
                          "n_error_nodes": count_errors(tree.root_node), "bytes": len(src)})

    _write_csv(out / "metrics.csv", mrows)
    _write_csv(out / "files.csv", frows)
    manifest = {
        "project": project.name,
        "version": version,
        "tag": project.tag(version),
        "language": lang.name,
        "scope": project.scope,
        "n_files": len(files),
        "n_files_with_parse_errors": sum(r["n_error_nodes"] > 0 for r in frows),
        "n_functions": len(mrows),
        "n_functions_with_parse_errors": sum(r["has_parse_error"] for r in mrows),
        "n_bodiless_functions_skipped": n_bodiless,
        "python": sys.version.split()[0],
        "tree_sitter": pkg_version("tree-sitter"),
        lang.grammar_package.replace("-", "_"): pkg_version(lang.grammar_package),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    with open(out / "manifest.json", "w", encoding="utf8", newline="\n") as fh:
        fh.write(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest))
    return manifest
