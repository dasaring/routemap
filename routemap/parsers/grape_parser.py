import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class GrapeParser(BaseParser):
    """Parser for Ruby Grape API framework."""

    ROUTE_PATTERN = re.compile(
        r'^\s*(get|post|put|patch|delete|options|head)\s+[\'"]([^\'"]+)[\'"]',
        re.MULTILINE | re.IGNORECASE,
    )
    NAMESPACE_PATTERN = re.compile(
        r'^\s*(?:namespace|prefix|group)\s+[\'"]([^\'"]+)[\'"]',
        re.MULTILINE,
    )
    GRAPE_INDICATOR = re.compile(
        r'(?:Grape::API|include Grape::DSL|mount\s+\w|< Grape::API)',
        re.MULTILINE,
    )

    def supports_file(self, path: Path) -> bool:
        if path.suffix != '.rb':
            return False
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            return bool(self.GRAPE_INDICATOR.search(content))
        except OSError:
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for rb_file in path.rglob('*.rb'):
                if self.supports_file(rb_file):
                    routes.extend(self._parse_file(rb_file))
        elif path.is_file() and self.supports_file(path):
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
        except OSError:
            return routes

        namespace_stack: List[str] = []
        lines = content.splitlines()

        for line in lines:
            ns_match = self.NAMESPACE_PATTERN.match(line)
            if ns_match:
                namespace_stack.append(ns_match.group(1).strip('/'))
                continue

            if re.match(r'^\s*end\b', line) and namespace_stack:
                namespace_stack.pop()
                continue

            route_match = self.ROUTE_PATTERN.match(line)
            if route_match:
                method = route_match.group(1).upper()
                raw_path = route_match.group(2).strip('/')
                prefix = '/' + '/'.join(namespace_stack) if namespace_stack else ''
                full_path = f"{prefix}/{raw_path}".rstrip('/') or '/'
                routes.append(RouteEntry(
                    method=method,
                    path=full_path,
                    source=str(path),
                ))

        return routes
