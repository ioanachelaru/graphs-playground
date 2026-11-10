"""Build per-method control flow graphs (CFG) and data flow graphs (DFG) for a Java project.

Same graph model and output format as build_graphs.py (Django), using tree-sitter-java.
Scope: every `<module>/src/main/java/**/*.java` file (production code of all modules; tests,
examples outside src/main/java and generated sources are excluded).

Usage:
    python src/build_graphs_java.py --project activemq --versions 5.0.0

Outputs (output/<project>-<version>/): graphs.jsonl, metrics.csv, files.csv, manifest.json

Java specifics
--------------
* Graph units: method and constructor bodies, including methods of nested, local and anonymous
  classes (qualname e.g. `BrokerService.start`, `Outer.method.<anon>.run`). Abstract/interface
  methods without a body have no graph and are only counted in the manifest.
* CFG: as for Python, plus do-while, classic for (init -> condition -> body -> update -> condition),
  switch (header -> each case group, fall-through between groups, break -> after switch, header ->
  after switch when there is no default), synchronized, labeled break/continue, throw (-> EXIT).
* DFG: definitions = local variable declarators, plain-name assignment targets (`x = ..`, `x += ..`,
  `x++`), parameters (at ENTRY), loop/catch/resource variables. `this.x = ..` / `a[i] = ..` are
  uses, not definitions. Plain names without a reaching definition (mostly fields) go to
  free_vars. Bodies of anonymous classes are not part of the enclosing method's defs/uses.
"""
import argparse
import csv
import datetime as dt
import json
import sys
from importlib.metadata import version as pkg_version
from pathlib import Path

import tree_sitter_java as tsj
from tree_sitter import Language, Parser

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_graphs import count_errors, def_use_edges  # noqa: E402  (shared reaching-definitions)

ROOT = Path(__file__).resolve().parents[1]
SOURCES = ROOT / "sources"
OUTPUT = ROOT / "output"
PARSER = Parser(Language(tsj.language()))

METHOD_TYPES = {"method_declaration", "constructor_declaration", "compact_constructor_declaration"}
TYPE_DECLS = {"class_declaration", "interface_declaration", "enum_declaration",
              "annotation_type_declaration", "record_declaration"}
LOOP_TYPES = {"for_statement", "enhanced_for_statement", "while_statement", "do_statement"}


# ----------------------------------------------------------------------------------------------
# defs / uses
# ----------------------------------------------------------------------------------------------
def du(*nodes):
    """(defs, uses) identifier nodes inside the given expression/statement subtrees."""
    defs, uses = [], []
    stack = [n for n in nodes if n is not None]
    while stack:
        n = stack.pop()
        t = n.type
        if t == "identifier":
            uses.append(n)
        elif t == "class_body":
            continue  # anonymous class body: separate graphs
        elif t == "field_access":
            stack.append(n.child_by_field_name("object"))
        elif t == "method_invocation":
            for f in ("object", "arguments"):
                c = n.child_by_field_name(f)
                if c is not None:
                    stack.append(c)
        elif t == "assignment_expression":
            left, right = n.child_by_field_name("left"), n.child_by_field_name("right")
            op = n.child_by_field_name("operator")
            if left is not None and left.type == "identifier":
                defs.append(left)
                if op is not None and op.type != "=":
                    uses.append(left)
            elif left is not None:
                stack.append(left)
            if right is not None:
                stack.append(right)
        elif t == "update_expression":
            ids = [c for c in n.named_children if c.type == "identifier"]
            if ids:
                defs.append(ids[0])
                uses.append(ids[0])
            else:
                stack.extend(n.named_children)
        elif t == "variable_declarator":
            nm = n.child_by_field_name("name")
            if nm is not None:
                defs.append(nm)
            v = n.child_by_field_name("value")
            if v is not None:
                stack.append(v)
        elif t in ("annotation", "marker_annotation", "type_identifier", "scoped_type_identifier",
                   "generic_type", "array_type", "integral_type", "floating_point_type",
                   "boolean_type", "void_type", "type_arguments", "dimensions"):
            continue
        elif t == "object_creation_expression":
            for c in n.named_children:  # arguments / outer object, skip the type and class body
                if c.type not in ("class_body", "type_identifier", "scoped_type_identifier",
                                  "generic_type", "type_arguments"):
                    stack.append(c)
        else:
            stack.extend(n.children)
    return defs, uses


def names(nodes):
    return sorted({n.text.decode("utf8", "replace") for n in nodes})


def first_line(node, limit=120):
    return node.text.decode("utf8", "replace").split("\n", 1)[0].strip()[:limit]


# ----------------------------------------------------------------------------------------------
# CFG construction
# ----------------------------------------------------------------------------------------------
class MethodGraph:
    def __init__(self, m):
        self.nodes, self.edges = [], set()
        self.loops = []       # continue targets: {"target": id, "label": str|None}
        self.breakables = []  # {"label": str|None, "breaks": [(id, lab)]}
        self.pending_label = None
        self.entry = self._node("ENTRY", m, self._params(m), [], text="ENTRY")
        self.exit = self._node("EXIT", m, [], [], text="EXIT")
        outs = self.block(m.child_by_field_name("body"), [(self.entry, "")], 0)
        self.connect(outs, self.exit)

    def _node(self, kind, ts, defs, uses, text=None, depth=0):
        nid = len(self.nodes)
        self.nodes.append({"id": nid, "kind": kind, "line": ts.start_point[0] + 1,
                           "end_line": ts.end_point[0] + 1,
                           "text": text if text is not None else first_line(ts),
                           "defs": defs, "uses": uses, "depth": depth})
        return nid

    def connect(self, preds, nid):
        for p, lab in preds:
            self.edges.add((p, nid, lab))

    @staticmethod
    def _params(m):
        ps = m.child_by_field_name("parameters")
        out = []
        if ps is not None:
            for p in ps.named_children:
                if p.type == "formal_parameter":
                    nm = p.child_by_field_name("name")
                    out += [nm] if nm is not None else []
                elif p.type == "spread_parameter":
                    for c in p.named_children:
                        if c.type == "variable_declarator":
                            nm = c.child_by_field_name("name")
                            out += [nm] if nm is not None else []
        return names(out)

    def simple(self, s, preds, depth, defs_uses=None, kind=None, text=None):
        d, u = defs_uses if defs_uses is not None else du(s)
        n = self._node(kind or s.type, s, names(d), names(u), text=text, depth=depth)
        self.connect(preds, n)
        return n

    # -- statements ----------------------------------------------------------------------------
    def block(self, b, preds, depth):
        if b is None:
            return preds
        if b.type in ("block", "constructor_body"):
            for s in b.named_children:
                if s.type not in ("line_comment", "block_comment"):
                    preds = self.stmt(s, preds, depth)
            return preds
        return self.stmt(b, preds, depth)  # single-statement body

    def stmt(self, s, preds, depth):
        t = s.type
        label, self.pending_label = self.pending_label, None
        if t == "block":
            return self.block(s, preds, depth)
        if t == "labeled_statement":
            lab = next((c for c in s.named_children if c.type == "identifier"), None)
            inner = [c for c in s.named_children if c.type != "identifier"]
            self.pending_label = lab.text.decode() if lab is not None else None
            return self.stmt(inner[0], preds, depth) if inner else preds
        if t == "return_statement":
            n = self.simple(s, preds, depth)
            self.edges.add((n, self.exit, "return"))
            return []
        if t == "throw_statement":
            n = self.simple(s, preds, depth)
            self.edges.add((n, self.exit, "raise"))
            return []
        if t == "break_statement":
            n = self.simple(s, preds, depth, defs_uses=([], []))
            tgt = self._find(self.breakables, s)
            if tgt is not None:
                tgt["breaks"].append((n, ""))
            return []
        if t == "continue_statement":
            n = self.simple(s, preds, depth, defs_uses=([], []))
            tgt = self._find(self.loops, s)
            if tgt is not None:
                self.edges.add((n, tgt["target"], "continue"))
            return []
        if t == "if_statement":
            return self.if_stmt(s, preds, depth)
        if t in LOOP_TYPES:
            return self.loop_stmt(s, preds, depth, label)
        if t in ("switch_expression", "switch_statement"):
            return self.switch_stmt(s, preds, depth, label)
        if t in ("try_statement", "try_with_resources_statement"):
            return self.try_stmt(s, preds, depth)
        if t == "synchronized_statement":
            expr = next((c for c in s.named_children if c.type == "parenthesized_expression"), None)
            h = self.simple(s, preds, depth, defs_uses=du(expr), kind="synchronized")
            body = s.child_by_field_name("body") or next(
                (c for c in s.named_children if c.type == "block"), None)
            return self.block(body, [(h, "")], depth + 1)
        if t in TYPE_DECLS:  # local class: one node, its methods get their own graphs
            return [(self.simple(s, preds, depth, defs_uses=([], [])), "")]
        if t in (";", "empty_statement"):
            return preds
        return [(self.simple(s, preds, depth), "")]

    @staticmethod
    def _find(stack, s):
        lab = next((c for c in s.named_children if c.type == "identifier"), None)
        if lab is None:
            return stack[-1] if stack else None
        lab = lab.text.decode()
        for e in reversed(stack):
            if e["label"] == lab:
                return e
        return stack[-1] if stack else None

    def if_stmt(self, s, preds, depth):
        c = self.simple(s, preds, depth, defs_uses=du(s.child_by_field_name("condition")), kind="if")
        outs = self.block(s.child_by_field_name("consequence"), [(c, "T")], depth + 1)
        alt = s.child_by_field_name("alternative")
        if alt is None:
            return outs + [(c, "F")]
        return outs + self.block(alt, [(c, "F")], depth + 1)

    def loop_stmt(self, s, preds, depth, label):
        t = s.type
        brk = {"label": label, "breaks": []}
        self.breakables.append(brk)
        body = s.child_by_field_name("body")
        if t == "while_statement":
            h = self.simple(s, preds, depth, defs_uses=du(s.child_by_field_name("condition")), kind="while")
            self.loops.append({"target": h, "label": label})
            outs = self.block(body, [(h, "T")], depth + 1)
            self.connect([(p, "back") for p, _ in outs], h)
            exits = [(h, "F")]
        elif t == "enhanced_for_statement":
            nm, val = s.child_by_field_name("name"), s.child_by_field_name("value")
            _, u = du(val)
            h = self.simple(s, preds, depth, defs_uses=([nm] if nm is not None else [], u), kind="for")
            self.loops.append({"target": h, "label": label})
            outs = self.block(body, [(h, "T")], depth + 1)
            self.connect([(p, "back") for p, _ in outs], h)
            exits = [(h, "F")]
        elif t == "for_statement":
            inits = s.children_by_field_name("init")
            if inits:
                i = self._node("for_init", s, *map(names, du(*inits)),
                               text="init: " + "; ".join(first_line(x, 60) for x in inits), depth=depth)
                self.connect(preds, i)
                preds = [(i, "")]
            cond = s.child_by_field_name("condition")
            h = self.simple(s, preds, depth, defs_uses=du(cond), kind="for")
            ups = s.children_by_field_name("update")
            upd = None
            if ups:
                upd = self._node("for_update", ups[0], *map(names, du(*ups)),
                                 text="update: " + ", ".join(first_line(x, 60) for x in ups), depth=depth)
                self.edges.add((upd, h, "back"))
            self.loops.append({"target": upd if upd is not None else h, "label": label})
            outs = self.block(body, [(h, "T")], depth + 1)
            if upd is not None:
                self.connect(outs, upd)
            else:
                self.connect([(p, "back") for p, _ in outs], h)
            exits = [(h, "F")] if cond is not None else []
        else:  # do_statement: body first, then condition
            d = self._node("do", s, [], [], text="do", depth=depth)
            self.connect(preds, d)
            cond = s.child_by_field_name("condition")
            c = self._node("while", cond if cond is not None else s,
                           *map(names, du(cond)), text="while " + (first_line(cond) if cond is not None else ""),
                           depth=depth)
            self.loops.append({"target": c, "label": label})
            outs = self.block(body, [(d, "")], depth + 1)
            self.connect(outs, c)
            self.edges.add((c, d, "T"))
            exits = [(c, "F")]
        self.loops.pop()
        self.breakables.pop()
        return exits + brk["breaks"]

    def switch_stmt(self, s, preds, depth, label):
        cond = s.child_by_field_name("condition")
        h = self.simple(s, preds, depth, defs_uses=du(cond), kind="switch")
        brk = {"label": label, "breaks": []}
        self.breakables.append(brk)
        body = s.child_by_field_name("body")
        carry, has_default = [], False
        groups = [g for g in (body.named_children if body is not None else [])
                  if g.type in ("switch_block_statement_group", "switch_rule")]
        for g in groups:
            labels = [c for c in g.named_children if c.type == "switch_label"]
            if any(l.text.decode().startswith("default") for l in labels):
                has_default = True
            lab_text = " / ".join(first_line(l, 40) for l in labels) or "case"
            cs = self._node("case", g, [], names(du(*labels)[1]), text=lab_text, depth=depth + 1)
            self.connect([(h, "case")] + carry, cs)
            preds_g = [(cs, "")]
            for st in g.named_children:
                if st.type in ("switch_label", "line_comment", "block_comment"):
                    continue
                preds_g = self.stmt(st, preds_g, depth + 1)
            # switch_rule (`case X ->`) never falls through
            carry = [] if g.type == "switch_rule" else preds_g
            if g.type == "switch_rule":
                brk["breaks"] += preds_g
        self.breakables.pop()
        outs = carry + brk["breaks"]
        if not has_default:
            outs.append((h, "no-match"))
        return outs

    def try_stmt(self, s, preds, depth):
        d, u = [], []
        res = s.child_by_field_name("resources")
        if res is not None:
            d, u = du(res)
            for r in res.named_children:
                nm = r.child_by_field_name("name")
                if nm is not None:
                    d.append(nm)
        t = self._node("try", s, names(d), names([x for x in u if x not in d]),
                       text="try" + (" (resources)" if res is not None else ""), depth=depth)
        self.connect(preds, t)
        outs = self.block(s.child_by_field_name("body"), [(t, "")], depth + 1)
        handler_outs, fin = [], None
        for c in s.named_children:
            if c.type == "catch_clause":
                p = next((x for x in c.named_children if x.type == "catch_formal_parameter"), None)
                nm = p.child_by_field_name("name") if p is not None else None
                h = self._node("except", c, names([nm] if nm is not None else []), [],
                               text=first_line(c).rstrip("{").strip(), depth=depth)
                self.edges.add((t, h, "exception"))
                handler_outs += self.block(c.child_by_field_name("body"), [(h, "")], depth + 1)
            elif c.type == "finally_clause":
                fin = c
        outs += handler_outs
        if fin is not None:
            f = self._node("finally", fin, [], [], text="finally", depth=depth)
            self.connect(outs, f)
            if not outs:
                self.edges.add((t, f, "exception"))
            body = next((x for x in fin.named_children if x.type == "block"), None)
            outs = self.block(body, [(f, "")], depth + 1)
        return outs


# ----------------------------------------------------------------------------------------------
# driver
# ----------------------------------------------------------------------------------------------
def iter_methods(root):
    """Yield (method_node, qualname) for every method/constructor, incl. nested/anonymous classes."""
    stack = [(root, [])]
    while stack:
        n, scope = stack.pop()
        for c in reversed(n.children):
            t = c.type
            if t in METHOD_TYPES:
                nm = c.child_by_field_name("name")
                name = nm.text.decode("utf8", "replace") if nm is not None else "<init>"
                yield c, ".".join(scope + [name])
                stack.append((c, scope + [name]))
            elif t in TYPE_DECLS:
                nm = c.child_by_field_name("name")
                stack.append((c, scope + [nm.text.decode("utf8", "replace") if nm is not None else "<anon>"]))
            elif t == "object_creation_expression" and any(x.type == "class_body" for x in c.children):
                stack.append((c, scope + ["<anon>"]))
            else:
                stack.append((c, scope))


def metrics(g, dfg, free, m):
    kinds = [x["kind"] for x in g.nodes]
    n_nodes, n_edges = len(g.nodes), len(g.edges)
    return {
        "loc": m.end_point[0] - m.start_point[0] + 1,
        "cfg_nodes": n_nodes, "cfg_edges": n_edges, "cyclomatic": n_edges - n_nodes + 2,
        "n_if": kinds.count("if"),
        "n_loops": kinds.count("for") + kinds.count("while"),  # do-while counted via its while node
        "n_switch": kinds.count("switch"), "n_case": kinds.count("case"),
        "n_try": kinds.count("try"), "n_except": kinds.count("except"),
        "n_sync": kinds.count("synchronized"),
        "n_return": kinds.count("return_statement"), "n_raise": kinds.count("throw_statement"),
        "max_depth": max(x["depth"] for x in g.nodes),
        "dfg_edges": len(dfg),
        "n_defs": sum(len(x["defs"]) for x in g.nodes),
        "n_uses": sum(len(x["uses"]) for x in g.nodes),
        "n_vars": len({v for x in g.nodes for v in x["defs"]}),
        "n_free_vars": len(free), "n_params": len(g.nodes[0]["defs"]),
        "has_parse_error": int(m.has_error),
    }


def source_files(vroot):
    return sorted(p for p in vroot.rglob("*.java")
                  if "/src/main/java/" in "/" + p.relative_to(vroot).as_posix())


def process(project, version):
    vroot = SOURCES / f"{project}-{version}"
    if not vroot.is_dir():
        sys.exit(f"missing {vroot}; run src/download_sources.py --project {project} --versions {version}")
    out = OUTPUT / f"{project}-{version}"
    out.mkdir(parents=True, exist_ok=True)
    files = source_files(vroot)
    mrows, frows, n_abstract = [], [], 0
    with open(out / "graphs.jsonl", "w", encoding="utf8") as gj:
        for f in files:
            rel = f.relative_to(vroot).as_posix()  # e.g. activemq-core/src/main/java/org/...
            src = f.read_bytes()
            tree = PARSER.parse(src)
            nf = 0
            for m, qual in iter_methods(tree.root_node):
                if m.child_by_field_name("body") is None:
                    n_abstract += 1
                    continue
                g = MethodGraph(m)
                dfg, free = def_use_edges(g)
                ident = {"version": version, "filepath": rel, "method_name": qual.split(".")[-1],
                         "qualname": qual, "line_start": m.start_point[0] + 1,
                         "line_end": m.end_point[0] + 1}
                gj.write(json.dumps({**ident, "has_parse_error": bool(m.has_error), "nodes": g.nodes,
                                     "cfg_edges": sorted(g.edges), "dfg_edges": dfg,
                                     "free_vars": free}) + "\n")
                mrows.append({**ident, **metrics(g, dfg, free, m)})
                nf += 1
            frows.append({"version": version, "filepath": rel, "n_functions": nf,
                          "n_error_nodes": count_errors(tree.root_node), "bytes": len(src)})
    for name, rows in (("metrics.csv", mrows), ("files.csv", frows)):
        with open(out / name, "w", newline="", encoding="utf8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    manifest = {
        "project": project, "version": version,
        "source_dir": f"sources/{project}-{version}/**/src/main/java",
        "n_files": len(files),
        "n_files_with_parse_errors": sum(r["n_error_nodes"] > 0 for r in frows),
        "n_functions": len(mrows),
        "n_functions_with_parse_errors": sum(r["has_parse_error"] for r in mrows),
        "n_bodiless_methods_skipped": n_abstract,
        "python": sys.version.split()[0],
        "tree_sitter": pkg_version("tree-sitter"),
        "tree_sitter_java": pkg_version("tree-sitter-java"),
        "created_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print(json.dumps(manifest))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--versions", nargs="+", required=True)
    a = ap.parse_args()
    for v in a.versions:
        process(a.project, v)


if __name__ == "__main__":
    main()
