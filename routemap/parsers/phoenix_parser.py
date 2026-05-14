import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class PhoenixParser(BaseParser):
    """Parser for Phoenix (Elixir) router files."""

    # Matches: get "/path", ControllerModule, :action
    ROUTE_PATTERN = re.compile(
        r'\b(get|post|put|patch|delete|options|head)\s+"([^"]+)"\s*,\s*([\w.]+)\s*,\s*:(\w+)',
        re.MULTILINE,
    )

    # Matches: resources "/path", ControllerModule
    RESOURCES_PATTERN = re.compile(
        r'\bresources\s+"([^"]+)"\s*,\s*([\w.]+)',
        re.MULTILINE,
    )

    RESOURCE_ACTIONS = [
        ("GET", ""),
        ("GET", "/new"),
        ("POST", ""),
        ("GET", "/:id"),
        ("GET", "/:id/edit"),
        ("PUT", "/:id"),
        ("PATCH", "/:id"),
        ("DELETE", "/:id"),
    ]

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".ex":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "use Phoenix.Router" in content or "Phoenix.Router" in content
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for file in path.rglob("*.ex"):
                if self.supports_file(file):
                    routes.extend(self._parse_file(file))
        elif self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return routes

        for match in self.ROUTE_PATTERN.finditer(content):
            method, route_path, controller, action = match.groups()
            routes.append(
                RouteEntry(
                    method=method.upper(),
                    path=route_path,
                    source=str(path),
                    handler=f"{controller}.{action}",
                )
            )

        for match in self.RESOURCES_PATTERN.finditer(content):
            base_path, controller = match.groups()
            base_path = base_path.rstrip("/")
            for method, suffix in self.RESOURCE_ACTIONS:
                routes.append(
                    RouteEntry(
                        method=method,
                        path=f"{base_path}{suffix}",
                        source=str(path),
                        handler=f"{controller} (resource)",
                    )
                )

        return routes
