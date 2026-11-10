"""Tests for the Joern-based pipeline.

Unit tests run without Joern, on tests/data/joern_export_sample.jsonl (records exported by
joern_scripts/export.sc from small Python and Java examples). Integration tests run Joern on
the examples from the code review and record how it models each construct; they are skipped
unless JOERN_HOME and JAVA_HOME point to an installation (see scripts/install_joern.py).
"""
import collections
import gzip
import json
import os
import zipfile
from pathlib import Path

import pytest

from codegraphs.download import SourceTree, path_order
from codegraphs.extract import classify, convert_method, metrics_row, qualname
from codegraphs.graphio import write_jsonl_gz
from codegraphs.joern import _line_map
from codegraphs.projects import PROJECTS

DATA = Path(__file__).parent / "data"
SAMPLE = [json.loads(l) for l in (DATA / "joern_export_sample.jsonl").read_text(encoding="utf8").splitlines()]


def _methods(lang):
    return [r for r in SAMPLE if r["type"] == "method" and r["_language"] == lang]


# ----------------------------------------------------------------------------------------------
# method selection / naming
# ----------------------------------------------------------------------------------------------
def test_python_synthetic_methods_are_skipped():
    kinds = {r["name"]: classify("python", r) for r in _methods("python")}
    assert kinds["<module>"] == "synthetic"
    assert kinds["f"] == "keep"


def test_java_selection_and_signatures():
    kept = [r for r in _methods("java") if classify("java", r) == "keep"]
    names = sorted((qualname("java", r), r["signature"]) for r in kept)
    # overloads are distinguished by signature, anonymous classes are numbered by Joern
    assert ("Overloads.f", "void(int)") in names and ("Overloads.f", "void(java.lang.String)") in names
    assert ("Overloads.g.Runnable$0.run", "void()") in names and ("Overloads.g.Runnable$1.run", "void()") in names
    # compiler-default constructors (no end line) are synthetic
    assert all(r["line_end"] is not None for r in kept)
    assert not any(r["name"] == "<init>" for r in kept)


def test_convert_method_reindexes_nodes_and_edges():
    rec = next(r for r in _methods("python") if r["name"] == "f")
    g = convert_method(rec, "python", "t")
    n = len(g["nodes"])
    assert [x["id"] for x in g["nodes"]] == list(range(n))
    assert g["nodes"][0]["kind"] == "METHOD" and g["nodes"][-1]["kind"] == "METHOD_RETURN"
    assert all(0 <= a < n and 0 <= b < n and lab == "" for a, b, lab in g["cfg_edges"])
    assert len(g["cfg_edges"]) == len(rec["cfg_edges"]) and len(g["dfg_edges"]) == len(rec["ddg_edges"])
    # vars_in / vars_out are the DDG edge variables
    assert {v for x in g["nodes"] for v in x["vars_out"]} == {e[2] for e in g["dfg_edges"]}


def test_metrics_row():
    g = convert_method(next(r for r in _methods("python") if r["name"] == "f"), "python", "t")
    m = metrics_row(g)
    assert m["cyclomatic"] == m["cfg_edges"] - m["cfg_nodes"] + 2 == 2  # one branch: normal vs except
    assert m["n_try"] == 1 and m["n_catch"] == 1


def test_parameters_do_not_count_as_cfg_nodes():
    # Overloads.f(int a) has a parameter node that carries no CFG edge
    rec = next(r for r in _methods("java") if r["full_name"].endswith("Overloads.f:void(int)"))
    g = convert_method(rec, "java", "t")
    m = metrics_row(g)
    assert m["n_params"] >= 1
    assert m["cfg_nodes"] < len(g["nodes"]) and m["cyclomatic"] == 1  # straight-line method


def test_line_map_back_to_original():
    original = "a\nprint x\nb\nc\n"
    converted = "a\nprint(x)\nb\nnew\nc\n"
    m = _line_map(original, converted)
    assert m[1:6] == [1, 2, 3, 3, 4]  # changed line keeps its number; inserted line -> line before


def test_jsonl_gz_is_deterministic(tmp_path):
    recs = [{"a": 1}, {"b": [1, 2]}]
    write_jsonl_gz(tmp_path / "x.gz", recs)
    write_jsonl_gz(tmp_path / "y.gz", recs)
    assert (tmp_path / "x.gz").read_bytes() == (tmp_path / "y.gz").read_bytes()
    assert gzip.decompress((tmp_path / "x.gz").read_bytes()) == b'{"a":1}\n{"b":[1,2]}\n'


# ----------------------------------------------------------------------------------------------
# sources, scope, navigation
# ----------------------------------------------------------------------------------------------
@pytest.mark.parametrize("project,rel,expected", [
    ("django", "django/db/models/base.py", True),
    ("django", "tests/regressiontests/foo.py", False),
    ("django", "docs/conf.py", False),
    ("activemq", "activemq-core/src/main/java/org/apache/activemq/Foo.java", True),
    ("activemq", "activemq-core/src/test/java/org/apache/activemq/FooTest.java", False),
    ("activemq", "assembly/src/release/example/src/Foo.java", False),
])
def test_project_scope(project, rel, expected):
    assert PROJECTS[project].include(rel) is expected


def test_py2_versions_are_django_1x():
    assert PROJECTS["django"].py2_versions == tuple(v for v in PROJECTS["django"].versions if v.startswith("1."))
    assert PROJECTS["activemq"].py2_versions == ()


def test_source_tree_reads_zip_without_top_folder(tmp_path):
    with zipfile.ZipFile(tmp_path / "django-9.9.zip", "w") as z:
        z.writestr("django-9.9/", "")
        z.writestr("django-9.9/django/Utils.py", "a = 1\n")
        z.writestr("django-9.9/django/db/base.py", "b = 2\n")
    with SourceTree(tmp_path, PROJECTS["django"], "9.9") as tree:
        assert tree.paths() == ["django/db/base.py", "django/Utils.py"]  # case-insensitive order
        assert tree.read("django/db/base.py") == b"b = 2\n"


def test_version_order_is_natural():
    from codegraphs.site import version_key
    assert sorted(["1.10", "1.2", "2.0", "1.0"], key=version_key) == ["1.0", "1.2", "1.10", "2.0"]


def test_index_lists_only_versions_with_viewers(tmp_path):
    from codegraphs.site import build_index
    out = tmp_path / "output"
    for name, version, viewer in (("activemq", "5.8.0", True), ("activemq", "5.0.0", True),
                                  ("django", "1.0", False)):
        d = out / f"{name}-{version}"
        d.mkdir(parents=True)
        (d / "manifest.json").write_text(json.dumps({"project": name, "version": version,
                                                     "n_files": 1, "n_functions": 2}))
        if viewer:
            (d / "viewer.html").write_text("<html></html>")
    index = build_index(out)
    assert [e["version"] for e in index["activemq"]] == ["5.0.0", "5.8.0"]
    assert "django" not in index
    assert 'href="output/activemq-5.8.0/viewer.html"' in (tmp_path / "index.html").read_text(encoding="utf8")


# ----------------------------------------------------------------------------------------------
# integration: how Joern models the constructs from the code review
# ----------------------------------------------------------------------------------------------
REVIEW_PY = {
    "finally_return.py": "def f(a):\n    try:\n        return a\n    finally:\n        cleanup()\n",
    "match_stmt.py": "def f(c):\n    match c:\n        case 1:\n            return 'a'\n        case _:\n            return 'b'\n",
    "scoping.py": "def f(ys):\n    zs = [y*2 for y in ys]\n    if (n := len(zs)) > 0:\n        return n\n",
    "try_dfg.py": "def f():\n    try:\n        x = load()\n        y = parse(x)\n    except Exception:\n        log(x)\n",
}
REVIEW_JAVA = {
    "FinallyReturn.java": "class FinallyReturn { int f(int a) { try { return a; } finally { x(); } } void x(){} }\n",
    "LabeledBlock.java": "class LabeledBlock { void f(int a) {\n while (a > 0) {\n blk: {\n if (a == 1) break blk;\n a--;\n }\n a++;\n }\n } }\n",
    "TryDfg.java": "class TryDfg { void f() { int x = 0; try { x = load(); parse(x); } catch (Exception e) { log(x); } } int load(){return 1;} void parse(int v){} void log(int v){} }\n",
}
needs_joern = pytest.mark.skipif(not (os.environ.get("JOERN_HOME") and os.environ.get("JAVA_HOME")),
                                 reason="JOERN_HOME / JAVA_HOME not set")


def _joern_graphs(tmp_path, lang, cases):
    from codegraphs import joern
    root = tmp_path / lang / "src"
    root.mkdir(parents=True)
    for name, src in cases.items():
        (root / name).write_text(src, encoding="utf8", newline="\n")
    st = joern.Stage(root=root, files=list(cases), sizes={})
    export = joern.parse_and_export(joern.JoernConfig.resolve(), lang, st)
    return {(g["filepath"], g["qualname"]): g for g in
            (convert_method(r, lang, "t") for r in joern.read_export(export)
             if r["type"] == "method" and classify(lang, r) == "keep")}


def _reachable(g, src_pred, dst_pred):
    adj = collections.defaultdict(list)
    for a, b, _ in g["cfg_edges"]:
        adj[a].append(b)
    start = [n["id"] for n in g["nodes"] if src_pred(n)]
    seen, stack = set(start), list(start)
    while stack:
        for y in adj[stack.pop()]:
            if y not in seen:
                seen.add(y)
                stack.append(y)
    return any(dst_pred(n) for n in g["nodes"] if n["id"] in seen and n["id"] not in start)


@needs_joern
def test_joern_python_review_cases(tmp_path):
    gs = _joern_graphs(tmp_path, "python", REVIEW_PY)
    starts = lambda s: (lambda n: n["text"].startswith(s))
    # KNOWN LIMITATION: `return` inside try/finally goes straight to METHOD_RETURN
    g = gs[("finally_return.py", "f")]
    assert not _reachable(g, lambda n: n["kind"] == "RETURN", starts("cleanup()"))
    # match: one control structure, both returns present
    g = gs[("match_stmt.py", "f")]
    assert g["control"].get("MATCH") == 1 and sum(n["kind"] == "RETURN" for n in g["nodes"]) == 2
    # walrus defines n, which reaches `return n`
    g = gs[("scoping.py", "f")]
    assert any(v == "n" and g["nodes"][b]["text"] == "return n" for a, b, v in g["dfg_edges"])
    # a definition in the try body reaches the except handler
    g = gs[("try_dfg.py", "f")]
    assert any(v == "x" and g["nodes"][b]["text"].startswith("log(x)") for a, b, v in g["dfg_edges"])


@needs_joern
def test_joern_java_review_cases(tmp_path):
    gs = _joern_graphs(tmp_path, "java", REVIEW_JAVA)
    starts = lambda s: (lambda n: n["text"].startswith(s))
    # KNOWN LIMITATION: `return` inside try/finally goes straight to METHOD_RETURN
    g = gs[("FinallyReturn.java", "FinallyReturn.f")]
    assert not _reachable(g, lambda n: n["kind"] == "RETURN", starts("this.x()"))
    # labelled break leaves the block, not the loop
    g = gs[("LabeledBlock.java", "LabeledBlock.f")]
    assert _reachable(g, starts("break blk"), starts("a++"))
    g = gs[("TryDfg.java", "TryDfg.f")]
    assert any(v == "x" and g["nodes"][b]["text"].startswith("this.log(x)") for a, b, v in g["dfg_edges"])
