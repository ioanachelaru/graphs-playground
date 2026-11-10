"""Command line interface.

    python -m codegraphs download --project django   --versions 1.0 1.1
    python -m codegraphs build    --project activemq --versions 5.0.0     # Joern parse + export
    python -m codegraphs view     --project django   --all
    python -m codegraphs run      --project django   --versions 1.0       # download + build + view
    python -m codegraphs metrics  --project django   --all                # metrics.csv from graphs.jsonl.gz
    python -m codegraphs index                                            # start page + navigation
    python -m codegraphs serve                                            # http://localhost:8000/

`view` and `run` also refresh the navigation (index.html + output/versions.js).
Joern: --joern-home / JOERN_HOME (default tools/joern-cli) and --java-home / JAVA_HOME (JDK 21).
Paths default to ./sources, ./output and a temporary work directory.
"""
import argparse
import functools
import http.server
import tempfile
from pathlib import Path

from codegraphs import download, extract, joern, site, viewer
from codegraphs.projects import PROJECTS, get_project


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="codegraphs", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    for name, help_ in (("download", "download release sources"),
                        ("build", "build Joern CFG/DDG graphs and metrics"),
                        ("view", "build the HTML viewer (and refresh navigation)"),
                        ("run", "download + build + view"),
                        ("metrics", "recompute metrics.csv from graphs.jsonl.gz (no Joern)")):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--project", required=True, choices=sorted(PROJECTS))
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--versions", nargs="+")
        g.add_argument("--all", action="store_true", help="every version in the project registry")
        p.add_argument("--sources-dir", type=Path, default=Path("sources"))
        p.add_argument("--output-dir", type=Path, default=Path("output"))
        if name in ("download", "run"):
            p.add_argument("--force", action="store_true", help="re-download even if present")
        if name in ("build", "run"):
            p.add_argument("--joern-home", type=Path, default=None)
            p.add_argument("--java-home", type=Path, default=None)
            p.add_argument("--work-dir", type=Path,
                           default=Path(tempfile.gettempdir()) / "codegraphs-work",
                           help="staging + CPG files (outside the repository)")
            p.add_argument("--keep-work", action="store_true", help="keep staged sources and cpg.bin")
    p = sub.add_parser("index", help="write index.html + output/versions.js from existing outputs")
    p.add_argument("--output-dir", type=Path, default=Path("output"))
    p = sub.add_parser("serve", help="serve the repository over HTTP (viewers need HTTP)")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--root", type=Path, default=Path("."))
    return ap


def main(argv=None) -> int:
    a = _parser().parse_args(argv)
    if a.command == "index":
        site.build_index(a.output_dir)
        return 0
    if a.command == "serve":
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(a.root))
        print(f"serving {a.root.resolve()} at http://localhost:{a.port}/  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler).serve_forever()
        return 0
    project = get_project(a.project)
    versions = list(project.versions) if a.all else a.versions
    cfg = joern.JoernConfig.resolve(a.joern_home, a.java_home) if a.command in ("build", "run") else None
    for v in versions:
        if a.command in ("download", "run"):
            download.download(project, v, a.sources_dir, a.force)
        if a.command in ("build", "run"):
            extract.build(project, v, a.sources_dir, a.output_dir, cfg, a.work_dir, a.keep_work)
        if a.command == "metrics":
            extract.rewrite_metrics(a.output_dir, project, v)
        if a.command in ("view", "run"):
            viewer.build(project, v, a.output_dir)
    if a.command in ("view", "run"):
        site.build_index(a.output_dir)
    return 0
