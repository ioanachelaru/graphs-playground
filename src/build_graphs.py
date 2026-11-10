"""Build per-function control flow graphs (CFG) and data flow graphs (DFG) for a Django version.

Only files under sources/django-<version>/django/ are processed (tests, docs, extras are excluded).

Usage:
    python src/build_graphs.py --versions 1.0

Outputs (output/django-<version>/):
    graphs.jsonl   one JSON object per function: nodes, cfg_edges, dfg_edges + identifiers
    metrics.csv    one row per function with graph metrics
    files.csv      one row per file: n_functions, parse errors
    manifest.json  versions of tools, counts, timestamp

Graph model
-----------
CFG: statement-level. Nodes = ENTRY, EXIT, one node per simple statement, one header node per
compound statement (if/elif condition, for/while header, try, except clause, with header).
Edge labels: "" (sequence), T/F (branch), back (loop back-edge), continue, exception
(try -> handler), return/raise (-> EXIT). Nested defs/classes are one node in the parent and get
their own graph record.
DFG: def-use edges computed with reaching definitions over the CFG. Edge (d, u, var) means the
value of `var` defined at node d may be read at node u. Parameters are defined at ENTRY.
Attribute targets (self.x = ...) count as uses of `self`, not definitions.
"""
import argparse
import csv
import datetime as dt
import json
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

import tree_sitter_python as tsp
from tree_sitter import Language, Parser

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
OUTPUT = ROOT / "output"
PARSER = Parser(Language(tsp.language()))

FUNC_TYPES = {"function_definition"}
SIMPLE_KINDS = {  # statements with no internal control flow
    "expression_statement", "print_statement", "exec_statement", "assert_statement",
    "import_statement", "import_from_statement", "future_import_statement", "global_statement",
    "nonlocal_statement", "delete_statement", "pass_statement", "function_definition",
    "class_definition", "decorated_definition", "type_alias_statement",
}
SEQ_TARGETS = {"pattern_list", "tuple_pattern", "list_pattern", "tuple", "list",
               "parenthesized_expression", "expression_list"}


# ----------------------------------------------------------------------------------------------
# identifier helpers
# ----------------------------------------------------------------------------------------------
def idents(node):
    """Identifier nodes read inside `node` (skips attribute names after '.', kwarg names,
    and nested function/class/lambda bodies are included as reads of free variables)."""
    out = []
    stack = [node]
    while stack:
        n = stack.pop()
        if n.type == "identifier":
            out.append(n)
            continue
        if n.type == "attribute":
            obj = n.child_by_field_name("object")
            if obj is not None:
                stack.append(obj)
            continue
        if n.type == "keyword_argument":
            val = n.child_by_field_name("value")
            if val is not None:
                stack.append(val)
            continue
        stack.extend(n.children)
    return out


def target_defs(node):
    """Split an assignment target into (defined identifier nodes, read identifier nodes)."""
    if node is None:
        return [], []
    t = node.type
    if t == "identifier":
        return [node], []
    if t in SEQ_TARGETS or t in ("list_splat_pattern", "list_splat", "as_pattern_target"):
        d, u = [], []
        for c in node.named_children:
            dd, uu = target_defs(c)
            d += dd
            u += uu
        return d, u
    # attribute / subscript / anything else: no plain-name definition, only reads
    return [], idents(node)


def names(nodes):
    return sorted({n.text.decode("utf8", "replace") for n in nodes})


def first_line(node, limit=120):
    s = node.text.decode("utf8", "replace").split("\n", 1)[0].strip()
    return s[:limit]


# ----------------------------------------------------------------------------------------------
# CFG construction
# ----------------------------------------------------------------------------------------------
class FunctionGraph:
    def __init__(self, fn):
        self.fn = fn
        self.nodes = []  # dicts
        self.edges = set()  # (src, dst, label)
        self.loops = []  # stack of {"header": id, "breaks": [(id,label)]}
        self.entry = self._node("ENTRY", fn, defs=self._param_names(fn), uses=[], text="ENTRY")
        self.exit = self._node("EXIT", fn, defs=[], uses=[], text="EXIT")
        body = fn.child_by_field_name("body")
        outs = self.block(body, [(self.entry, "")], depth=0)
        self.connect(outs, self.exit)

    # -- bookkeeping ---------------------------------------------------------------------------
    def _node(self, kind, ts, defs, uses, text=None, depth=0):
        nid = len(self.nodes)
        self.nodes.append({
            "id": nid, "kind": kind,
            "line": ts.start_point[0] + 1, "end_line": ts.end_point[0] + 1,
            "text": text if text is not None else first_line(ts),
            "defs": defs, "uses": uses, "depth": depth,
        })
        return nid

    def connect(self, preds, nid):
        for p, lab in preds:
            self.edges.add((p, nid, lab))

    @staticmethod
    def _param_names(fn):
        params = fn.child_by_field_name("parameters")
        if params is None:
            return []
        out = []
        for p in params.named_children:
            if p.type in ("default_parameter", "typed_default_parameter"):
                nm = p.child_by_field_name("name")
                out += [nm] if nm is not None else []
            elif p.type == "typed_parameter":
                out += [c for c in p.named_children if c.type == "identifier"][:1] or \
                       [c for c in p.named_children if c.type in ("list_splat_pattern", "dictionary_splat_pattern")]
            else:  # identifier, *args, **kw, py2 tuple parameters
                out += idents(p)
        flat = []
        for n in out:
            flat += [n] if n.type == "identifier" else idents(n)
        return names(flat)

    # -- statements ----------------------------------------------------------------------------
    def block(self, block, preds, depth):
        if block is None:
            return preds
        stmts = [c for c in block.named_children if c.type != "comment"]
        if block.type != "block":  # single statement body (e.g. `if x: y`)
            stmts = [block]
        for s in stmts:
            preds = self.stmt(s, preds, depth)
        return preds

    def simple(self, s, preds, depth, kind=None):
        defs, uses = self.simple_defs_uses(s)
        n = self._node(kind or s.type, s, names(defs), names(uses), depth=depth)
        self.connect(preds, n)
        return n

    def stmt(self, s, preds, depth):
        t = s.type
        if t in ("return_statement", "raise_statement"):
            n = self.simple(s, preds, depth)
            self.edges.add((n, self.exit, "return" if t == "return_statement" else "raise"))
            return []
        if t == "break_statement":
            n = self.simple(s, preds, depth)
            if self.loops:
                self.loops[-1]["breaks"].append((n, ""))
            return []
        if t == "continue_statement":
            n = self.simple(s, preds, depth)
            if self.loops:
                self.edges.add((n, self.loops[-1]["header"], "continue"))
            return []
        if t == "if_statement":
            return self.if_stmt(s, preds, depth)
        if t in ("for_statement", "while_statement"):
            return self.loop_stmt(s, preds, depth)
        if t == "try_statement":
            return self.try_stmt(s, preds, depth)
        if t == "with_statement":
            return self.with_stmt(s, preds, depth)
        # simple statements, match_statement, ERROR nodes: one node
        return [(self.simple(s, preds, depth), "")]

    def if_stmt(self, s, preds, depth):
        cond = s.child_by_field_name("condition")
        c = self._node("if", s, [], names(idents(cond)) if cond else [], depth=depth)
        self.connect(preds, c)
        outs = self.block(s.child_by_field_name("consequence"), [(c, "T")], depth + 1)
        false_pred = (c, "F")
        has_else = False
        for alt in s.children_by_field_name("alternative"):
            if alt.type == "elif_clause":
                ec = alt.child_by_field_name("condition")
                e = self._node("elif", alt, [], names(idents(ec)) if ec else [], depth=depth)
                self.connect([false_pred], e)
                outs += self.block(alt.child_by_field_name("consequence"), [(e, "T")], depth + 1)
                false_pred = (e, "F")
            elif alt.type == "else_clause":
                outs += self.block(alt.child_by_field_name("body"), [false_pred], depth + 1)
                has_else = True
        if not has_else:
            outs.append(false_pred)
        return outs

    def loop_stmt(self, s, preds, depth):
        if s.type == "for_statement":
            d, u = target_defs(s.child_by_field_name("left"))
            right = s.child_by_field_name("right")
            u = u + (idents(right) if right else [])
            h = self._node("for", s, names(d), names(u), depth=depth)
        else:
            cond = s.child_by_field_name("condition")
            h = self._node("while", s, [], names(idents(cond)) if cond else [], depth=depth)
        self.connect(preds, h)
        self.loops.append({"header": h, "breaks": []})
        body_out = self.block(s.child_by_field_name("body"), [(h, "T")], depth + 1)
        for p, _ in body_out:
            self.edges.add((p, h, "back"))
        loop = self.loops.pop()
        outs = [(h, "F")]
        alt = s.child_by_field_name("alternative")
        if alt is not None:  # for/while ... else
            outs = self.block(alt.child_by_field_name("body"), outs, depth + 1)
        return outs + loop["breaks"]

    def try_stmt(self, s, preds, depth):
        t = self._node("try", s, [], [], text="try:", depth=depth)
        self.connect(preds, t)
        outs = self.block(s.child_by_field_name("body"), [(t, "")], depth + 1)
        handler_outs, finally_clause = [], None
        for c in s.named_children:
            if c.type in ("except_clause", "except_group_clause"):
                d, u = self.except_defs_uses(c)
                h = self._node("except", c, names(d), names(u), depth=depth)
                self.edges.add((t, h, "exception"))
                body = next((x for x in c.named_children if x.type == "block"), None)
                handler_outs += self.block(body, [(h, "")], depth + 1)
            elif c.type == "else_clause":
                outs = self.block(c.child_by_field_name("body"), outs, depth + 1)
            elif c.type == "finally_clause":
                finally_clause = c
        outs += handler_outs
        if finally_clause is not None:
            f = self._node("finally", finally_clause, [], [], text="finally:", depth=depth)
            self.connect(outs, f)
            if not outs:  # every path returned/raised: finally still runs on the way out
                self.edges.add((t, f, "exception"))
            body = next((x for x in finally_clause.named_children if x.type == "block"), None)
            outs = self.block(body, [(f, "")], depth + 1)
        return outs

    def with_stmt(self, s, preds, depth):
        d, u = [], []
        for c in s.named_children:
            if c.type == "with_clause":
                for item in c.named_children:
                    val = item.child_by_field_name("value") or item
                    if val.type == "as_pattern":
                        kids = val.named_children
                        u += idents(kids[0])
                        dd, uu = target_defs(kids[-1])
                        d += dd
                        u += uu
                    else:
                        u += idents(val)
        h = self._node("with", s, names(d), names(u), depth=depth)
        self.connect(preds, h)
        return self.block(s.child_by_field_name("body"), [(h, "")], depth + 1)

    # -- defs / uses ---------------------------------------------------------------------------
    @staticmethod
    def except_defs_uses(c):
        header = [x for x in c.named_children if x.type != "block"]
        d, u = [], []
        # py3: except E as e  -> as_pattern ; py2: except E, e -> identifier ',' identifier
        has_comma = any(x.type == "," for x in c.children)
        for i, x in enumerate(header):
            if x.type == "as_pattern":
                u += idents(x.named_children[0])
                dd, uu = target_defs(x.named_children[-1])
                d += dd
                u += uu
            elif has_comma and i == len(header) - 1 and len(header) >= 2:
                dd, uu = target_defs(x)
                d += dd
                u += uu
            else:
                u += idents(x)
        return d, u

    @staticmethod
    def simple_defs_uses(s):
        t = s.type
        if t == "expression_statement" and s.named_children:
            e = s.named_children[0]
            if e.type == "assignment":
                d, u = [], []
                while e is not None and e.type == "assignment":  # chained a = b = expr
                    dd, uu = target_defs(e.child_by_field_name("left"))
                    d += dd
                    u += uu
                    e = e.child_by_field_name("right")
                if e is not None:
                    u += idents(e)
                return d, u
            if e.type == "augmented_assignment":
                left = e.child_by_field_name("left")
                dd, uu = target_defs(left)
                right = e.child_by_field_name("right")
                return dd, dd + uu + (idents(right) if right else [])
            return [], idents(s)
        if t in ("import_statement", "import_from_statement"):
            d = []
            module = s.child_by_field_name("module_name")
            for c in s.named_children:
                if c is module or (module is not None and c.id == module.id):
                    continue
                if c.type == "aliased_import":
                    a = c.child_by_field_name("alias")
                    d += [a] if a is not None else []
                elif c.type == "dotted_name" and c.named_children:
                    d.append(c.named_children[0])
            return d, []
        if t in ("function_definition", "class_definition"):
            nm = s.child_by_field_name("name")
            return ([nm] if nm is not None else []), []
        if t == "decorated_definition":
            inner = s.child_by_field_name("definition")
            nm = inner.child_by_field_name("name") if inner is not None else None
            decos = [c for c in s.named_children if c.type == "decorator"]
            return ([nm] if nm is not None else []), [i for dcr in decos for i in idents(dcr)]
        if t in ("global_statement", "nonlocal_statement", "pass_statement"):
            return [], []
        if t == "delete_statement":
            return [], idents(s)
        return [], idents(s)


# ----------------------------------------------------------------------------------------------
# data flow: reaching definitions
# ----------------------------------------------------------------------------------------------
def def_use_edges(g: FunctionGraph):
    n = len(g.nodes)
    preds = [[] for _ in range(n)]
    for a, b, _ in g.edges:
        preds[b].append(a)
    gen = [{(v, i) for v in g.nodes[i]["defs"]} for i in range(n)]
    killed_vars = [set(g.nodes[i]["defs"]) for i in range(n)]
    IN = [set() for _ in range(n)]
    OUT = [set(gen[i]) for i in range(n)]
    changed = True
    while changed:
        changed = False
        for i in range(n):
            new_in = set().union(*(OUT[p] for p in preds[i])) if preds[i] else set()
            new_out = gen[i] | {(v, d) for (v, d) in new_in if v not in killed_vars[i]}
            if new_in != IN[i] or new_out != OUT[i]:
                IN[i], OUT[i] = new_in, new_out
                changed = True
    edges, free = set(), set()
    for i in range(n):
        for v in g.nodes[i]["uses"]:
            ds = [d for (vv, d) in IN[i] if vv == v]
            if not ds:
                free.add(v)
            for d in ds:
                edges.add((d, i, v))
    return sorted(edges), sorted(free)


# ----------------------------------------------------------------------------------------------
# per-file driver
# ----------------------------------------------------------------------------------------------
def iter_functions(root):
    """Yield (function_node, qualified_name, start_node) for every function, incl. nested."""
    stack = [(root, [])]
    while stack:
        n, scope = stack.pop()
        for c in reversed(n.children):
            target, start = c, c
            if c.type == "decorated_definition":
                target = c.child_by_field_name("definition") or c
            if target.type in FUNC_TYPES:
                nm = target.child_by_field_name("name")
                name = nm.text.decode("utf8", "replace") if nm is not None else "<anon>"
                yield target, ".".join(scope + [name]), start
                stack.append((target, scope + [name]))
            elif target.type == "class_definition":
                nm = target.child_by_field_name("name")
                name = nm.text.decode("utf8", "replace") if nm is not None else "<anon>"
                stack.append((target, scope + [name]))
            else:
                stack.append((c, scope))


def count_errors(node):
    if not node.has_error:
        return 0
    k, stack = 0, [node]
    while stack:
        n = stack.pop()
        if n.type == "ERROR" or n.is_missing:
            k += 1
        elif n.has_error:
            stack.extend(n.children)
    return k


def metrics(g, dfg, free, fn, start, has_err):
    kinds = [x["kind"] for x in g.nodes]
    n_nodes, n_edges = len(g.nodes), len(g.edges)
    return {
        "loc": fn.end_point[0] - start.start_point[0] + 1,
        "cfg_nodes": n_nodes,
        "cfg_edges": n_edges,
        "cyclomatic": n_edges - n_nodes + 2,
        "n_if": kinds.count("if") + kinds.count("elif"),
        "n_loops": kinds.count("for") + kinds.count("while"),
        "n_try": kinds.count("try"),
        "n_except": kinds.count("except"),
        "n_with": kinds.count("with"),
        "n_return": kinds.count("return_statement"),
        "n_raise": kinds.count("raise_statement"),
        "max_depth": max(x["depth"] for x in g.nodes),
        "dfg_edges": len(dfg),
        "n_defs": sum(len(x["defs"]) for x in g.nodes),
        "n_uses": sum(len(x["uses"]) for x in g.nodes),
        "n_vars": len({v for x in g.nodes for v in x["defs"]}),
        "n_free_vars": len(free),
        "n_params": len(g.nodes[0]["defs"]),
        "has_parse_error": int(has_err),
    }


def process_version(version):
    vroot = SOURCES / f"django-{version}"
    pkg = vroot / "django"
    if not pkg.is_dir():
        sys.exit(f"missing {pkg}; run src/download_sources.py --versions {version} first")
    out = OUTPUT / f"django-{version}"
    out.mkdir(parents=True, exist_ok=True)
    files = sorted(pkg.rglob("*.py"))
    mrows, frows = [], []
    with open(out / "graphs.jsonl", "w", encoding="utf8") as gj:
        for f in files:
            rel = f.relative_to(vroot).as_posix()  # e.g. django/db/models/base.py
            src = f.read_bytes()
            tree = PARSER.parse(src)
            n_err = count_errors(tree.root_node)
            nf = 0
            for fn, qual, start in iter_functions(tree.root_node):
                g = FunctionGraph(fn)
                dfg, free = def_use_edges(g)
                ident = {
                    "version": version, "filepath": rel,
                    "method_name": qual.split(".")[-1], "qualname": qual,
                    "line_start": start.start_point[0] + 1, "line_end": fn.end_point[0] + 1,
                }
                m = metrics(g, dfg, free, fn, start, fn.has_error)
                gj.write(json.dumps({
                    **ident, "has_parse_error": bool(fn.has_error),
                    "nodes": g.nodes,
                    "cfg_edges": sorted(g.edges),
                    "dfg_edges": dfg, "free_vars": free,
                }) + "\n")
                mrows.append({**ident, **m})
                nf += 1
            frows.append({"version": version, "filepath": rel, "n_functions": nf,
                          "n_error_nodes": n_err, "bytes": len(src)})
    for name, rows in (("metrics.csv", mrows), ("files.csv", frows)):
        with open(out / name, "w", newline="", encoding="utf8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    manifest = {
        "version": version,
        "source_dir": f"sources/django-{version}/django",
        "n_files": len(files),
        "n_files_with_parse_errors": sum(r["n_error_nodes"] > 0 for r in frows),
        "n_functions": len(mrows),
        "n_functions_with_parse_errors": sum(r["has_parse_error"] for r in mrows),
        "python": sys.version.split()[0],
        "tree_sitter": pkg_version("tree-sitter"),
        "tree_sitter_python": pkg_version("tree-sitter-python"),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest))
    return manifest


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--versions", nargs="+", required=True)
    a = ap.parse_args()
    for v in a.versions:
        process_version(v)


if __name__ == "__main__":
    main()
