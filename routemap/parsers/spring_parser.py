import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class SpringParser(BaseParser):
    """Parser for Spring Boot (Java/Kotlin) REST controllers."""

    MAPPING_PATTERN = re.compile(
        r'@(GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)'
        r'\s*\(\s*(?:value\s*=\s*)?"([^"]+)"'
    )
    CLASS_MAPPING_PATTERN = re.compile(
        r'@RequestMapping\s*\(\s*(?:value\s*=\s*)?"([^"]+)"'
    )
    METHOD_MAP = {
        "GetMapping": "GET",
        "PostMapping": "POST",
        "PutMapping": "PUT",
        "DeleteMapping": "DELETE",
        "PatchMapping": "PATCH",
        "RequestMapping": "GET",
    }

    def supports_file(self, path: Path) -> bool:
        return path.suffix in (".java", ".kt")

    def parse(self, root: Path) -> List[RouteEntry]:
        routes = []
        for ext in ("**/*.java", "**/*.kt"):
            for file in root.glob(ext):
                routes.extend(self._parse_file(file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes = []
        try:
            content = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return routes

        if "@RestController" not in content and "@Controller" not in content:
            return routes

        class_prefix = ""
        class_match = self.CLASS_MAPPING_PATTERN.search(content)
        if class_match:
            class_prefix = class_match.group(1).rstrip("/")

        for match in self.MAPPING_PATTERN.finditer(content):
            annotation, route_path = match.group(1), match.group(2)
            method = self.METHOD_MAP.get(annotation, "GET")
            full_path = class_prefix + "/" + route_path.lstrip("/") if class_prefix else route_path
            routes.append(RouteEntry(
                method=method,
                path=full_path,
                source=str(path),
            ))
        return routes
