import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class DjangoParser(BaseParser):
    """Parser for Django URL patterns (urls.py files)."""

    # Matches: path('endpoint', view, name='name')
    # or: re_path(r'^endpoint/$', view)
    PATH_PATTERN = re.compile(
        r"(?:re_)?path\(\s*[r']([^']+)'\s*,\s*([\w.]+)",
        re.MULTILINE,
    )
    # Matches router.register or include() based routers (DRF)
    ROUTER_PATTERN = re.compile(
        r"router\.register\(\s*[r']([^']+)'\s*,\s*([\w.]+)",
        re.MULTILINE,
    )
    # HTTP method decorators used in function-based views
    METHOD_DECORATOR = re.compile(
        r"@(?:require_(GET|POST|PUT|PATCH|DELETE|http_methods))",
        re.IGNORECASE,
    )

    DRF_ACTIONS = ["GET", "POST", "PUT", "PATCH", "DELETE"]

    def supports_file(self, path: Path) -> bool:
        return path.suffix == ".py" and "urls" in path.name

    def parse(self, root: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        for py_file in root.rglob("*.py"):
            if self.supports_file(py_file):
                routes.extend(self._parse_file(py_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        source = path.read_text(encoding="utf-8")

        for match in self.PATH_PATTERN.finditer(source):
            endpoint, view = match.group(1), match.group(2)
            routes.extend(self._infer_routes(endpoint, view, path))

        for match in self.ROUTER_PATTERN.finditer(source):
            prefix, viewset = match.group(1), match.group(2)
            for method, suffix in [
                ("GET", ""),
                ("POST", ""),
                ("GET", "/{id}"),
                ("PUT", "/{id}"),
                ("PATCH", "/{id}"),
                ("DELETE", "/{id}"),
            ]:
                routes.append(
                    RouteEntry(
                        method=method,
                        path=f"/{prefix.strip('/')}{suffix}",
                        handler=viewset,
                        source_file=str(path),
                    )
                )
        return routes

    def _infer_routes(self, endpoint: str, view: str, path: Path) -> List[RouteEntry]:
        """Infer HTTP methods; default to GET+POST for generic views."""
        clean = endpoint.strip("^").strip("$").strip("/")
        url = f"/{clean}" if clean else "/"
        methods = ["GET", "POST"] if not re.search(r"<|pk|id", endpoint) else ["GET", "PUT", "PATCH", "DELETE"]
        return [
            RouteEntry(method=m, path=url, handler=view, source_file=str(path))
            for m in methods
        ]
