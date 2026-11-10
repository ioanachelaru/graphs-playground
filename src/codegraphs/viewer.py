"""Single-page HTML viewer for all graphs of one project version.

Reads output/<project>-<version>/graphs.jsonl and writes viewer.html next to it. The page embeds
the graphs as JSON and renders them with Cytoscape.js + dagre (loaded from unpkg.com).
"""
import json
from importlib.resources import files
from pathlib import Path

from codegraphs.projects import Project

KEEP = ("filepath", "qualname", "line_start", "line_end", "has_parse_error",
        "cfg_edges", "dfg_edges", "free_vars")
NODE_KEEP = ("id", "kind", "line", "text", "defs", "uses")


def _template() -> str:
    return files("codegraphs").joinpath("templates/viewer.html").read_text(encoding="utf8")


def build(project: Project, version: str, output_dir: Path) -> Path:
    out = Path(output_dir) / f"{project.name}-{version}"
    src = out / "graphs.jsonl"
    if not src.exists():
        raise SystemExit(f"missing {src}; run: python -m codegraphs build "
                         f"--project {project.name} --versions {version}")
    graphs = []
    with open(src, encoding="utf8") as fh:
        for line in fh:
            g = json.loads(line)
            rec = {k: g[k] for k in KEEP}
            rec["nodes"] = [{k: n[k] for k in NODE_KEEP} for n in g["nodes"]]
            graphs.append(rec)
    graphs.sort(key=lambda g: (g["filepath"], g["line_start"]))
    data = json.dumps(graphs, separators=(",", ":")).replace("</", "<\\/")
    html = (_template().replace("__PROJECT__", project.name)
            .replace("__VERSION__", version).replace("__DATA__", data))
    path = out / "viewer.html"
    with open(path, "w", encoding="utf8", newline="\n") as fh:
        fh.write(html)
    print(f"[done] {path} ({len(graphs)} functions, {len(html) / 1e6:.1f} MB)")
    return path
