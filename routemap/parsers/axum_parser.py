import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}

# Matches: .route("/path", get(handler)) or .route("/path", post(handler).layer(...))
ROUTE_PATTERN = re.compile(
    r'\.route\(\s*"([^"]+)"\s*,\s*([^)]+)\)',
    re.MULTILINE,
)

# Matches method names used inside route(), e.g. get(...), post(...)
METHOD_PATTERN = re.compile(r'\b(' + '|'.join(HTTP_METHODS) + r')\s*\(')


class AxumParser(BaseParser):
    """Parser for Rust Axum web framework route definitions."""

    framework = "axum"

    def supports_file(self, path: Path) -> bool:
        if path.suffix != ".rs":
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return False
        return "axum" in content and (".route(" in content or "Router::new()" in content)

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if not path.is_dir():
            routes.extend(self._parse_file(path))
        else:
            for rs_file in path.rglob("*.rs"):
                if self.supports_file(rs_file):
                    routes.extend(self._parse_file(rs_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            return []

        routes: List[RouteEntry] = []
        for match in ROUTE_PATTERN.finditer(content):
            route_path = match.group(1).strip()
            method_body = match.group(2)
            methods = METHOD_PATTERN.findall(method_body)
            if not methods:
                # Fallback: treat as GET if no explicit method found
                methods = ["get"]
            for method in methods:
                routes.append(
                    RouteEntry(
                        method=method.upper(),
                        path=route_path,
                        source=str(path),
                        framework="axum",
                    )
                )
        return routes
