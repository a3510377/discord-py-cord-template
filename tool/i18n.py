from __future__ import annotations

import ast
from pathlib import Path


class ContentExtractor(ast.NodeVisitor):
    def __init__(self, source: str) -> None:
        self.source = source
        self.translator_comments: dict[int, str] = {}

    @classmethod
    def from_file(cls, path: Path | str) -> ContentExtractor:
        source = Path(path).read_text(encoding="utf-8")
        self = cls(source)

        self.visit(ast.parse(source))

        return self

    def visit_Call(self, node: ast.Call):
        # if isinstance(node.func, ast.Name):
        if isinstance(node.func, (ast.Name, ast.Attribute)):
            ...
        print(type(node.func))
        ast.Attribute


if __name__ == "__main__":
    ContentExtractor.from_file(Path("./tool/test.py"))
