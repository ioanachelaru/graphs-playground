"""Interface every language front-end implements."""
from abc import ABC, abstractmethod
from functools import cached_property
from typing import Iterator, Optional, Tuple

from tree_sitter import Language as TSLanguage
from tree_sitter import Parser


class Language(ABC):
    name: str                 # e.g. "python"
    grammar_package: str      # PyPI name of the tree-sitter grammar (recorded in manifests)
    kind_counts: tuple        # ((metrics column, (CFG node kinds, ...)), ...)

    @abstractmethod
    def ts_language(self):
        """Return the grammar's language pointer (e.g. tree_sitter_python.language())."""

    @cached_property
    def parser(self) -> Parser:
        return Parser(TSLanguage(self.ts_language()))

    def parse(self, src: bytes):
        return self.parser.parse(src)

    @abstractmethod
    def iter_functions(self, root) -> Iterator[Tuple[object, str, object]]:
        """Yield (function_node, qualified_name, start_node) for every graph unit in a file.

        start_node is where the unit starts in the source (e.g. the decorator for decorated
        Python functions); it defines line_start.
        """

    @abstractmethod
    def build_cfg(self, fn) -> Optional[object]:
        """Return the built CFG (a CFGBuilder) for `fn`, or None if it has no body."""
