"""Language-independent part of the statement-level control flow graph.

A concrete builder (one per language) subclasses `CFGBuilder` and implements `param_names`
and `block`; the base class owns the node/edge storage and the ENTRY/EXIT skeleton.

Node dict:  id, kind, line, end_line, text, defs, uses, depth
Edge tuple: (src_id, dst_id, label)   labels: "" T F back continue exception return raise
                                                case no-match (Java switch)
"""
from abc import ABC, abstractmethod

from codegraphs.syntax import first_line


class CFGBuilder(ABC):
    def __init__(self, fn):
        self.nodes: list = []
        self.edges: set = set()
        self.entry = self._node("ENTRY", fn, self.param_names(fn), [], text="ENTRY")
        self.exit = self._node("EXIT", fn, [], [], text="EXIT")
        outs = self.block(fn.child_by_field_name("body"), [(self.entry, "")], 0)
        self.connect(outs, self.exit)

    # -- to implement per language ------------------------------------------------------------
    @abstractmethod
    def param_names(self, fn) -> list:
        """Sorted parameter names of the function (defined at ENTRY)."""

    @abstractmethod
    def block(self, body, preds, depth) -> list:
        """Add the statements of `body`; return the dangling (node_id, label) exits."""

    # -- shared bookkeeping -------------------------------------------------------------------
    def _node(self, kind, ts, defs, uses, text=None, depth=0) -> int:
        nid = len(self.nodes)
        self.nodes.append({
            "id": nid, "kind": kind,
            "line": ts.start_point[0] + 1, "end_line": ts.end_point[0] + 1,
            "text": text if text is not None else first_line(ts),
            "defs": defs, "uses": uses, "depth": depth,
        })
        return nid

    def connect(self, preds, nid) -> None:
        for p, lab in preds:
            self.edges.add((p, nid, lab))
