"""Build Joern graphs for one project version and write output/<project>-<version>/.

graphs.jsonl.gz  one JSON object per function (gzip, deterministic bytes):
                 version, filepath, method_name, qualname, signature, full_name, line_start,
                 line_end, nodes [{id, kind, line, text, vars_in, vars_out}],
                 cfg_edges [[src, dst, ""]], dfg_edges [[src, dst, variable]]
metrics.csv      one row per function (columns below)
files.csv        one row per in-scope source file: in_cpg, n_functions, bytes, py2to3_changed
manifest.json    scope, counts, skipped synthetic/abstract methods, tool versions, timestamp

Which Joern methods become graph units
  Python  every method whose name has no "<": Joern's synthetic <module>, <body>,
          <metaClassAdapter>, <metaClassCallHandler>, <fakeNew>, <lambda>N are skipped
  Java    every method except <clinit>, compiler-default constructors (no end line) and
          abstract/interface methods (ABSTRACT modifier); explicit constructors are <init>
Line numbers are those of the original source; for 2to3-converted files they are mapped back.
"""
import datetime as dt
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

from codegraphs import joern
from codegraphs.download import path_order
from codegraphs.graphio import read_jsonl_gz, write_csv, write_json, write_jsonl_gz
from codegraphs.projects import Project

CONTROL_COLUMNS = (("n_if", "IF"), ("n_while", "WHILE"), ("n_do", "DO"), ("n_for", "FOR"),
                   ("n_switch", "SWITCH"), ("n_try", "TRY"), ("n_catch", "CATCH"),
                   ("n_finally", "FINALLY"), ("n_throw", "THROW"), ("n_break", "BREAK"),
                   ("n_continue", "CONTINUE"))


# ----------------------------------------------------------------------------------------------
# method selection and naming
# ----------------------------------------------------------------------------------------------
def classify(language: str, rec: dict) -> str:
    """'keep', 'synthetic' or 'abstract' for one exported Joern method."""
    name = rec["name"]
    if language == "python":
        return "synthetic" if "<" in name else "keep"
    if name == "<clinit>" or rec["line_end"] is None:
        return "synthetic"
    if "ABSTRACT" in rec["modifiers"]:
        return "abstract"
    return "keep"


def qualname(language: str, rec: dict) -> str:
    """Python: Class.method / outer.inner; Java: Type.method (nested types as Outer$Inner)."""
    if language == "python":
        q = rec["full_name"].split(":", 1)[-1]
        return q[len("<module>."):] if q.startswith("<module>.") else q
    td, ns = rec["type_decl"], rec["namespace"]
    if ns and ns != "<global>" and td.startswith(ns + "."):
        td = td[len(ns) + 1:]
    return f"{td}.{rec['name']}"


# ----------------------------------------------------------------------------------------------
# conversion of one exported method
# ----------------------------------------------------------------------------------------------
def convert_method(rec: dict, language: str, version: str, line_map=None) -> dict:
    def orig(line):
        if line is None or not line_map:
            return line
        return line_map[line] if 0 < line < len(line_map) else line

    index = {n["id"]: i for i, n in enumerate(rec["nodes"])}
    vin, vout = [set() for _ in index], [set() for _ in index]
    dfg = []
    for a, b, var in rec["ddg_edges"]:
        ia, ib = index[a], index[b]
        dfg.append([ia, ib, var])
        vout[ia].add(var)
        vin[ib].add(var)
    nodes = [{"id": i, "kind": n["label"], "line": orig(n["line"]),
              "text": n["code"].split("\n", 1)[0].strip()[:120],
              "vars_in": sorted(vin[i]), "vars_out": sorted(vout[i])}
             for i, n in enumerate(rec["nodes"])]
    return {
        "version": version,
        "filepath": rec["filename"].replace("\\", "/"),
        "method_name": rec["name"],
        "qualname": qualname(language, rec),
        "signature": rec["signature"],
        "full_name": rec["full_name"],
        "line_start": orig(rec["line_start"]),
        "line_end": orig(rec["line_end"]),
        "nodes": nodes,
        "cfg_edges": sorted([index[a], index[b], ""] for a, b in rec["cfg_edges"]),
        "dfg_edges": sorted(dfg),
        "control": rec["control"],
    }


def metrics_row(g: dict) -> dict:
    """Metrics of one converted graph.

    cfg_nodes counts only nodes with at least one CFG edge: parameters (which carry DDG edges
    only) and the entry nodes of nested function definitions are in `nodes` but not in the CFG.
    cyclomatic = cfg_edges - cfg_nodes + 2 over that CFG.
    """
    kinds = Counter(n["kind"] for n in g["nodes"])
    in_cfg = {a for a, _, _ in g["cfg_edges"]} | {b for _, b, _ in g["cfg_edges"]}
    n_nodes, n_edges = len(in_cfg), len(g["cfg_edges"])
    row = {k: g[k] for k in ("version", "filepath", "method_name", "qualname", "signature",
                             "line_start", "line_end")}
    row.update({
        "loc": (g["line_end"] - g["line_start"] + 1) if g["line_end"] and g["line_start"] else None,
        "cfg_nodes": n_nodes,
        "cfg_edges": n_edges,
        "cyclomatic": n_edges - n_nodes + 2,
        "dfg_edges": len(g["dfg_edges"]),
        "n_dfg_vars": len({e[2] for e in g["dfg_edges"]}),
        "n_params": kinds.get("METHOD_PARAMETER_IN", 0),
        "n_calls": kinds.get("CALL", 0),
        "n_return": kinds.get("RETURN", 0),
    })
    for col, ctype in CONTROL_COLUMNS:
        row[col] = g["control"].get(ctype, 0)
    return row


def rewrite_metrics(output_dir: Path, project: Project, version: str) -> int:
    """Recompute metrics.csv from an existing graphs.jsonl.gz (no Joern needed)."""
    out = Path(output_dir) / f"{project.name}-{version}"
    rows = [metrics_row(g) for g in read_jsonl_gz(out / "graphs.jsonl.gz")]
    write_csv(out / "metrics.csv", rows)
    print(f"[done] {out / 'metrics.csv'} ({len(rows)} functions)")
    return len(rows)


def _java_version(cfg: joern.JoernConfig) -> str:
    exe = cfg.java_home / "bin" / "java"
    try:
        r = subprocess.run([str(exe), "-version"], capture_output=True, text=True, timeout=60)
        return (r.stderr or r.stdout).splitlines()[0].strip()
    except Exception:
        return "unknown"


# ----------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------
def build(project: Project, version: str, sources_dir: Path, output_dir: Path,
          cfg: joern.JoernConfig, work_dir: Path, keep_work: bool = False) -> dict:
    lang = project.language
    st = joern.stage(project, version, sources_dir, work_dir)
    export = joern.parse_and_export(cfg, lang, st)

    out = Path(output_dir) / f"{project.name}-{version}"
    out.mkdir(parents=True, exist_ok=True)
    cpg_files, graphs, skipped = set(), [], Counter()
    for rec in joern.read_export(export):
        if rec["type"] == "file":
            cpg_files.add(rec["name"].replace("\\", "/"))
            continue
        kind = classify(lang, rec)
        if kind != "keep":
            skipped[kind] += 1
            continue
        fp = rec["filename"].replace("\\", "/")
        graphs.append(convert_method(rec, lang, version, st.line_maps.get(fp)))
    graphs.sort(key=lambda g: (path_order(g["filepath"]), g["line_start"] or 0, g["full_name"]))

    write_jsonl_gz(out / "graphs.jsonl.gz", graphs)
    write_csv(out / "metrics.csv", [metrics_row(g) for g in graphs])
    per_file = Counter(g["filepath"] for g in graphs)
    frows = [{"version": version, "filepath": rel, "in_cpg": int(rel in cpg_files),
              "n_functions": per_file.get(rel, 0), "bytes": st.sizes[rel],
              "py2to3_changed": int(rel in st.line_maps)}
             for rel in st.files]
    write_csv(out / "files.csv", frows)
    manifest = {
        "project": project.name, "version": version, "tag": project.tag(version),
        "language": lang, "scope": project.scope, "extractor": "joern",
        "joern_frontend": joern.FRONTENDS[lang],
        "py2to3": st.converted,
        "n_files": len(st.files),
        "n_files_not_in_cpg": sum(1 for r in frows if not r["in_cpg"]),
        "n_files_changed_by_2to3": len(st.line_maps),
        "n_functions": len(graphs),
        "n_synthetic_methods_skipped": skipped["synthetic"],
        "n_abstract_methods_skipped": skipped["abstract"],
        "joern": cfg.version(),
        "java": _java_version(cfg),
        "python": sys.version.split()[0],
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    write_json(out / "manifest.json", manifest)
    if not keep_work:
        shutil.rmtree(st.root.parent, ignore_errors=True)
    print(json.dumps(manifest))
    return manifest
