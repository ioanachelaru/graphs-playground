"""Command line interface.

    python -m codegraphs download --project django   --versions 1.0 1.1
    python -m codegraphs build    --project activemq --versions 5.0.0
    python -m codegraphs view     --project django   --all
    python -m codegraphs run      --project django   --versions 1.0     # download + build + view

Paths default to ./sources and ./output (run from the repository root, or pass
--sources-dir / --output-dir).
"""
import argparse
from pathlib import Path

from codegraphs import download, extract, viewer
from codegraphs.projects import PROJECTS, get_project


def _parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="codegraphs", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    for name, help_ in (("download", "download release sources"),
                        ("build", "build CFG/DFG graphs and metrics"),
                        ("view", "build the HTML viewer"),
                        ("run", "download + build + view")):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--project", required=True, choices=sorted(PROJECTS))
        g = p.add_mutually_exclusive_group(required=True)
        g.add_argument("--versions", nargs="+")
        g.add_argument("--all", action="store_true", help="every version in the project registry")
        p.add_argument("--sources-dir", type=Path, default=Path("sources"))
        p.add_argument("--output-dir", type=Path, default=Path("output"))
        if name in ("download", "run"):
            p.add_argument("--force", action="store_true", help="re-download even if present")
    return ap


def main(argv=None) -> int:
    a = _parser().parse_args(argv)
    project = get_project(a.project)
    versions = list(project.versions) if a.all else a.versions
    for v in versions:
        if a.command in ("download", "run"):
            download.download(project, v, a.sources_dir, a.force)
        if a.command in ("build", "run"):
            extract.build(project, v, a.sources_dir, a.output_dir)
        if a.command in ("view", "run"):
            viewer.build(project, v, a.output_dir)
    return 0
