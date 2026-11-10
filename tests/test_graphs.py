"""Graph-construction regression tests.

Each sample function exercises every control construct of its language; the expected CFG
edges, DFG edges, free variables and node kinds are in tests/data/expected_graphs.json
(checked by hand when the builders were written).
"""
import json
from pathlib import Path

import pytest

from codegraphs import dataflow
from codegraphs.languages import get_language
from codegraphs.projects import PROJECTS

EXPECTED = json.loads((Path(__file__).parent / "data" / "expected_graphs.json").read_text())

PY_SRC = b"""def f(a, b=1, *args, **kw):
    print a, b
    try:
        x = a + 1
    except ValueError, e:
        raise e
    for i, j in kw.items():
        if i: break
        elif j: continue
        else: x += i
    with open(a) as fh: y = fh.read()
    return x, y
"""

JAVA_SRC = b"""class A { A(int x){ super(x); }
 int f(int a, String... rest) throws Exception {
  int i = 0, j; j = a; i += j; i++;
  outer: for (int k = 0; k < a; k++) { if (k == 2) continue outer; else break; }
  for (String s : rest) { System.out.println(s); }
  do { i--; } while (i > 0);
  switch (a) { case 1: i = 1; case 2: i = 2; break; default: i = 3; }
  try { this.x = foo(i); } catch (IOException e) { throw e; } finally { i = 0; }
  synchronized (this) { new Runnable() { public void run() { int z = 1; } }; }
  while ((j = read()) != -1) j--;
  return i;
 } abstract void g(); }"""


def _graph(lang_name, src, qualname):
    lang = get_language(lang_name)
    funcs = list(lang.iter_functions(lang.parse(src).root_node))
    fn = next(fn for fn, q, _ in funcs if q == qualname)
    g = lang.build_cfg(fn)
    dfg, free = dataflow.def_use_edges(g)
    return g, dfg, free, [q for _, q, _ in funcs]


@pytest.mark.parametrize("lang_name,src,qualname", [
    ("python", PY_SRC, "f"),
    ("java", JAVA_SRC, "A.f"),
])
def test_graph_matches_expected(lang_name, src, qualname):
    exp = EXPECTED[lang_name]
    g, dfg, free, _ = _graph(lang_name, src, qualname)
    assert [n["kind"] for n in g.nodes] == exp["kinds"]
    assert sorted(g.edges) == [tuple(e) for e in exp["cfg"]]
    assert dfg == [tuple(e) for e in exp["dfg"]]
    assert free == exp["free"]


def test_java_units_and_bodiless_methods():
    _, _, _, quals = _graph("java", JAVA_SRC, "A.f")
    assert quals == EXPECTED["java"]["qualnames"]  # nested anonymous class method included
    lang = get_language("java")
    abstract = next(fn for fn, q, _ in lang.iter_functions(lang.parse(JAVA_SRC).root_node) if q == "A.g")
    assert lang.build_cfg(abstract) is None


def test_loop_carried_definition_reaches_itself():
    g, dfg, _, _ = _graph("python", PY_SRC, "f")
    aug = next(n["id"] for n in g.nodes if n["text"] == "else: x += i" or n["text"] == "x += i")
    assert (aug, aug, "x") in dfg  # x += i inside the loop reaches its own next iteration


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
