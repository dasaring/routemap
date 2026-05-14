import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class FiberParser(BaseParser):
    """Parser for Go Fiber web framework route definitions."""

    # Fiber HTTP method calls: app.Get("/path", handler)
    ROUTE_PATTERN = re.compile(
        r'\.(?P<method>Get|Post|Put|Patch|Delete|Head|Options|All)\s*'
        r'\(\s*"(?P<path>[^"]+)"',
        re.MULTILINE,
    )

    # Group routes: v1 := app.Group("/v1")
    GROUP_PATTERN = re.compile(
        r'(?P<var>\w+)\s*:?=\s*(?:\w+)\.Group\(\s*"(?P<prefix>[^"]+)"'
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".go",):
            return False
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            return "github.com/gofiber/fiber" in content or "fiber.New" in content
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for go_file in sorted(path.rglob("*.go")):
                if self.supports_file(go_file):
                    routes.extend(self._parse_file(go_file))
        elif path.is_file() and self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        content = path.read_text(encoding="utf-8", errors="ignore")
        routes: List[RouteEntry] = []

        # Build prefix map: variable name -> prefix string
        prefix_map: dict = {}
        for m in self.GROUP_PATTERN.finditer(content):
            prefix_map[m.group("var")] = m.group("prefix").rstrip("/")

        # Match all route registrations with their preceding variable
        for m in self.ROUTE_PATTERN.finditer(content):
            method = m.group("method").upper()
            if method == "ALL":
                method = "*"
            raw_path = m.group("path")

            # Try to find which variable owns this call by scanning backwards
            prefix = ""
            preceding = content[: m.start()]
            # Find the last identifier before the dot
            var_match = re.search(r'(\w+)\s*$', preceding)
            if var_match:
                var_name = var_match.group(1)
                prefix = prefix_map.get(var_name, "")

            full_path = prefix + raw_path if not raw_path.startswith(prefix) else raw_path

            routes.append(
                RouteEntry(
                    method=method,
                    path=full_path,
                    source=str(path),
                )
            )

        return routes
