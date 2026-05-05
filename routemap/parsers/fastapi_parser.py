"""FastAPI route parser — extracts routes from Python FastAPI source files."""

import ast
import os
from pathlib import Path

from routemap.parsers.base import BaseParser, RouteEntry

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


class FastAPIParser(BaseParser):
    """Parses FastAPI/APIRouter decorated route definitions."""

    def supports_file(self, filename: str) -> bool:
        return filename.endswith(".py")

    def parse(self) -> list[RouteEntry]:
        routes: list[RouteEntry] = []
        for py_file in Path(self.root_dir).rglob("*.py"):
            try:
                routes.extend(self._parse_file(str(py_file)))
            except SyntaxError:
                pass
        return routes

    def _parse_file(self, filepath: str) -> list[RouteEntry]:
        routes: list[RouteEntry] = []
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()

        tree = ast.parse(source, filename=filepath)
        rel_path = os.path.relpath(filepath, self.root_dir)

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                route = self._extract_route(decorator, node.name, rel_path, node.lineno)
                if route:
                    routes.append(route)
        return routes

    def _extract_route(self, decorator: ast.expr, handler: str, filepath: str, line: int) -> RouteEntry | None:
        if not isinstance(decorator, ast.Call):
            return None
        func = decorator.func
        if not isinstance(func, ast.Attribute):
            return None
        method = func.attr.lower()
        if method not in HTTP_METHODS:
            return None

        path = "/"
        if decorator.args:
            first_arg = decorator.args[0]
            if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                path = first_arg.value

        tags: list[str] = []
        summary: str | None = None
        for kw in decorator.keywords:
            if kw.arg == "tags" and isinstance(kw.value, ast.List):
                tags = [elt.value for elt in kw.value.elts if isinstance(elt, ast.Constant)]
            if kw.arg == "summary" and isinstance(kw.value, ast.Constant):
                summary = kw.value.value

        return RouteEntry(method=method, path=path, handler=handler,
                          file=filepath, line=line, tags=tags, summary=summary)
