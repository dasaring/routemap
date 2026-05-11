import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class LaravelParser(BaseParser):
    """Parser for Laravel PHP route files (routes/web.php, routes/api.php)."""

    ROUTE_PATTERN = re.compile(
        r"Route::(?P<method>get|post|put|patch|delete|options|any)\s*\("
        r"\s*['\"](?P<path>[^'\"]+)['\"]\s*,",
        re.IGNORECASE,
    )

    RESOURCE_PATTERN = re.compile(
        r"Route::resource\s*\(\s*['\"](?P<resource>[^'\"]+)['\"]\s*,",
        re.IGNORECASE,
    )

    RESOURCE_METHODS = [
        ("GET", "/{resource}"),
        ("GET", "/{resource}/create"),
        ("POST", "/{resource}"),
        ("GET", "/{resource}/{id}"),
        ("GET", "/{resource}/{id}/edit"),
        ("PUT", "/{resource}/{id}"),
        ("DELETE", "/{resource}/{id}"),
    ]

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".php":
            return False
        return path.name in ("web.php", "api.php") or path.parent.name == "routes"

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for php_file in path.rglob("*.php"):
                if self.supports_file(php_file):
                    routes.extend(self._parse_file(php_file))
        elif self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            source = path.read_text(encoding="utf-8")
        except OSError:
            return routes

        for match in self.ROUTE_PATTERN.finditer(source):
            method = match.group("method").upper()
            route_path = match.group("path")
            # Normalize Laravel {param} to :{param} style for consistency
            route_path = re.sub(r"\{(\w+)\}", r":\1", route_path)
            if not route_path.startswith("/"):
                route_path = "/" + route_path
            routes.append(RouteEntry(method=method, path=route_path, source=str(path)))

        for match in self.RESOURCE_PATTERN.finditer(source):
            resource = match.group("resource").strip("/")
            for method, path_tpl in self.RESOURCE_METHODS:
                route_path = path_tpl.replace("{resource}", resource)
                routes.append(
                    RouteEntry(method=method, path=route_path, source=str(path))
                )

        return routes
