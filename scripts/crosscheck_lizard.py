"""Cross-check the Joern-based cyclomatic complexity against lizard (an independent tool).

    pip install lizard
    python scripts/crosscheck_lizard.py --project django --version 5.2
    python scripts/crosscheck_lizard.py --project activemq --version 5.8.0 --csv crosscheck.csv

Functions are matched on (file, start line, name); start lines follow Joern (the `def` line /
the line of the method name, i.e. after decorators and annotations). Prints the match rate,
Spearman correlation and how often the two values agree. metrics.csv `cyclomatic` is
E - N + 2 over Joern's CFG, which also branches on short-circuit && / || / and / or.
Run from the repository root with PYTHONPATH=src.
"""
import argparse
import csv
import sys
from pathlib import Path

import lizard

from codegraphs.download import SourceTree
from codegraphs.projects import get_project


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(a, b):
    ra, rb = _rank(a), _rank(b)
    n = len(a)
    ma, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--version", required=True)
    ap.add_argument("--sources-dir", type=Path, default=Path("sources"))
    ap.add_argument("--output-dir", type=Path, default=Path("output"))
    ap.add_argument("--csv", type=Path, help="write the matched pairs here")
    a = ap.parse_args()
    project = get_project(a.project)
    with open(a.output_dir / f"{project.name}-{a.version}" / "metrics.csv", encoding="utf8") as fh:
        ours = list(csv.DictReader(fh))
    ext = ".py" if project.language == "python" else ".java"
    liz = {}
    with SourceTree(a.sources_dir, project, a.version) as tree:
        for rel in sorted({r["filepath"] for r in ours}):
            code = tree.read(rel).decode("utf8", "replace")
            for fn in lizard.analyze_file.analyze_source_code(rel if rel.endswith(ext) else rel + ext,
                                                               code).function_list:
                name = fn.name.split("::")[-1].split(".")[-1]
                liz.setdefault((rel, fn.start_line, name), fn.cyclomatic_complexity)
    pairs = []
    for r in ours:
        if r["method_name"] == "<init>":  # Java constructor: lizard uses the (simple) class name
            name = r["qualname"].rsplit(".", 1)[0].split(".")[-1].split("$")[-1]
        else:
            name = r["method_name"]
        k = (r["filepath"], int(r["line_start"]), name)
        if k in liz:
            pairs.append((r["filepath"], r["qualname"], r["signature"], int(r["line_start"]),
                          int(r["cyclomatic"]), liz[k]))
    if not pairs:
        print("no matched functions")
        return 1
    a_, b_ = [p[4] for p in pairs], [p[5] for p in pairs]
    d = [x - y for x, y in zip(a_, b_)]
    n = len(pairs)
    print(f"{project.name} {a.version}: functions {len(ours)}, lizard {len(liz)}, matched {n} "
          f"({n / len(ours):.0%}); spearman {spearman(a_, b_):.3f}; equal {sum(x == 0 for x in d) / n:.0%}, "
          f"joern lower {sum(x < 0 for x in d) / n:.0%}, joern higher {sum(x > 0 for x in d) / n:.0%}")
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf8") as fh:
            w = csv.writer(fh)
            w.writerow(["filepath", "qualname", "signature", "line_start", "joern_cyclomatic", "lizard_ccn"])
            w.writerows(pairs)
    return 0


if __name__ == "__main__":
    sys.exit(main())
