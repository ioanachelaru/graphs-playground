"""Viewer page for one project version: output/<project>-<version>/viewer.html.

The page embeds only an index of the functions (file, name, signature, lines, node count). The
graphs themselves are downloaded on first use from graphs.jsonl.gz next to the page and
decompressed in the browser (fetch + DecompressionStream), so the page must be served over
HTTP: GitHub Pages, or `python -m codegraphs serve` locally. Line i of graphs.jsonl.gz is the
function at index i.
"""
import json
from importlib.resources import files
from pathlib import Path

from codegraphs.graphio import read_jsonl_gz
from codegraphs.projects import Project


def _template() -> str:
    return files("codegraphs").joinpath("templates/viewer.html").read_text(encoding="utf8")


def build(project: Project, version: str, output_dir: Path) -> Path:
    out = Path(output_dir) / f"{project.name}-{version}"
    src = out / "graphs.jsonl.gz"
    if not src.exists():
        raise SystemExit(f"missing {src}; run: python -m codegraphs build "
                         f"--project {project.name} --versions {version}")
    index = [[g["filepath"], g["qualname"], g["signature"], g["line_start"], g["line_end"],
              len(g["nodes"])] for g in read_jsonl_gz(src)]
    data = json.dumps(index, separators=(",", ":")).replace("</", "<\\/")
    html = (_template().replace("__PROJECT__", project.name)
            .replace("__VERSION__", version).replace("__INDEX__", data))
    path = out / "viewer.html"
    with open(path, "w", encoding="utf8", newline="\n") as fh:
        fh.write(html)
    print(f"[done] {path} ({len(index)} functions, {len(html) / 1e6:.1f} MB)")
    return path
