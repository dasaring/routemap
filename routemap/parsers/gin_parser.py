import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class GinParser(BaseParser):
    """Parser for Go Gin framework route definitions."""

    # Matches: router.GET("/path", handler) or r.POST("/path", handler)
    ROUTE_PATTERN = re.compile(
        r'(?:router|r|v\d+|api|group)\.(GET|POST|PUT|PATCH|DELETE|OPTIONS|HEAD)\s*'
        r'\(\s*"([^"]+)"',
        re.MULTILINE,
    )

    # Matches group prefix: v1 := router.Group("/api/v1")
    GROUP_PATTERN = re.compile(
        r'(\w+)\s*:?=\s*(?:router|r|\w+)\.Group\s*\(\s*"([^"]+)"',
        re.MULTILINE,
    )

    def supports_file(self, path: Path) -> bool:
        return path.suffix == ".go"

    def parse(self, root: Path) -> List[RouteEntry]:
        routes = []
        for go_file in root.rglob("*.go"):
            routes.extend(self._parse_file(go_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        try:
            source = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return []

        # Build a map of variable name -> group prefix
        group_prefixes = {}
        for match in self.GROUP_PATTERN.finditer(source):
            var_name, prefix = match.group(1), match.group(2)
            group_prefixes[var_name] = prefix.rstrip("/")

        routes = []
        for match in self.ROUTE_PATTERN.finditer(source):
            method = match.group(1).upper()
            route_path = match.group(2)

            # Determine which variable called the method
            call_start = match.start()
            line_start = source.rfind("\n", 0, call_start) + 1
            line = source[line_start : match.start()]
            var_match = re.match(r"(\w+)\s*$", line.strip())
            prefix = ""
            if var_match:
                var_name = var_match.group(1)
                prefix = group_prefixes.get(var_name, "")

            full_path = prefix + route_path if not route_path.startswith(prefix) else route_path

            routes.append(
                RouteEntry(
                    method=method,
                    path=full_path,
                    handler=None,
                    source_file=str(path),
                )
            )
        return routes
