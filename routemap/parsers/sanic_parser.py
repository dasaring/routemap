import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options"}

ROUTE_PATTERN = re.compile(
    r"@(?:\w+\.)?(?:route|add_route)\s*\(\s*['\"]([^'\"]+)['\"](?:.*?methods=\[([^\]]+)\])?",
    re.DOTALL,
)
DECORATOR_PATTERN = re.compile(
    r"@(?:\w+\.)(get|post|put|patch|delete|head|options)\s*\(\s*['\"]([^'\"]+)['\"]",
    re.IGNORECASE,
)
ADD_ROUTE_PATTERN = re.compile(
    r"\.add_route\s*\(\s*\w+\s*,\s*['\"]([^'\"]+)['\"](?:.*?methods=\[([^\]]+)\])?",
    re.DOTALL,
)
SANIC_IMPORT = re.compile(r"from sanic|import sanic", re.IGNORECASE)


class SanicParser(BaseParser):
    """Parser for Sanic (Python async web framework) route files."""

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".py":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return bool(SANIC_IMPORT.search(content))
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_file():
            routes.extend(self._parse_file(path))
        elif path.is_dir():
            for py_file in sorted(path.rglob("*.py")):
                if self.supports_file(py_file):
                    routes.extend(self._parse_file(py_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        # Match shorthand decorators: @app.get("/path")
        for match in DECORATOR_PATTERN.finditer(content):
            method = match.group(1).upper()
            route_path = match.group(2)
            routes.append(RouteEntry(
                path=route_path,
                method=method,
                source=str(path),
            ))

        # Match @app.route("/path", methods=["GET", "POST"])
        for match in ROUTE_PATTERN.finditer(content):
            route_path = match.group(1)
            methods_str = match.group(2)
            if methods_str:
                methods = [
                    m.strip().strip("'\"}").upper()
                    for m in methods_str.split(",")
                ]
            else:
                methods = ["GET"]
            for method in methods:
                if method:
                    routes.append(RouteEntry(
                        path=route_path,
                        method=method,
                        source=str(path),
                    ))

        # Match app.add_route(handler, "/path", methods=[...])
        for match in ADD_ROUTE_PATTERN.finditer(content):
            route_path = match.group(1)
            methods_str = match.group(2)
            if methods_str:
                methods = [
                    m.strip().strip("'\"}").upper()
                    for m in methods_str.split(",")
                ]
            else:
                methods = ["GET"]
            for method in methods:
                if method:
                    routes.append(RouteEntry(
                        path=route_path,
                        method=method,
                        source=str(path),
                    ))

        return routes
