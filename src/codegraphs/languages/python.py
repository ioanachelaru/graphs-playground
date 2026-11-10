"""Python front-end (tree-sitter-python; parses Python 2 and 3 syntax).

Graph units: every `def` (methods and nested functions included; qualname `Class.method`,
`outer.inner`). line_start is the first decorator line for decorated functions.

CFG: if/elif/else, for/while (+ else), try/except/else/finally, with, return/raise -> EXIT,
break/continue. Nested defs/classes are a single node in the enclosing graph.
DFG defs: assignment targets (incl. tuple unpacking, chained and augmented assignment), for/with/
except targets (py2 `except E, e` too), import names, nested def/class names, parameters.
`self.x = ...` is a use of `self`, not a definition.
"""
import tree_sitter_python as tsp

from codegraphs.cfg import CFGBuilder
from codegraphs.languages.base import Language
from codegraphs.syntax import names

SEQ_TARGETS = {"pattern_list", "tuple_pattern", "list_pattern", "tuple", "list",
               "parenthesized_expression", "expression_list"}


# ----------------------------------------------------------------------------------------------
# identifier helpers
# ----------------------------------------------------------------------------------------------
def idents(node):
    """Identifier nodes read inside `node` (skips attribute names after '.' and kwarg names;
    nested lambda/comprehension bodies are included as reads)."""
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


# ----------------------------------------------------------------------------------------------
# CFG
# ----------------------------------------------------------------------------------------------
class PythonCFG(CFGBuilder):
    def __init__(self, fn):
        self.loops = []  # stack of {"header": id, "breaks": [(id, label)]}
        super().__init__(fn)

    def param_names(self, fn):
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
        defs, uses = simple_defs_uses(s)
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
                d, u = except_defs_uses(c)
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


# ----------------------------------------------------------------------------------------------
# defs / uses of single statements
# ----------------------------------------------------------------------------------------------
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
    return [], idents(s)  # delete_statement, print/exec/assert, ERROR, ...


# ----------------------------------------------------------------------------------------------
# Language implementation
# ----------------------------------------------------------------------------------------------
class PythonLanguage(Language):
    name = "python"
    grammar_package = "tree-sitter-python"
    kind_counts = (
        ("n_if", ("if", "elif")),
        ("n_loops", ("for", "while")),
        ("n_try", ("try",)),
        ("n_except", ("except",)),
        ("n_with", ("with",)),
        ("n_return", ("return_statement",)),
        ("n_raise", ("raise_statement",)),
    )

    def ts_language(self):
        return tsp.language()

    def iter_functions(self, root):
        stack = [(root, [])]
        while stack:
            n, scope = stack.pop()
            for c in reversed(n.children):
                target, start = c, c
                if c.type == "decorated_definition":
                    target = c.child_by_field_name("definition") or c
                if target.type == "function_definition":
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

    def build_cfg(self, fn):
        return PythonCFG(fn)
