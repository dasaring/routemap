import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class FlaskParser(BaseParser):
    """
    Parser for Flask Python applications.
    Detects routes defined with @app.route or @blueprint.route decorators.
    """

    ROUTE_PATTERN = re.compile(
        r'@(?P<app>\w+)\.route\(\s*[\'"](?P<path>[^\'"]+)[\'"]'
        r'(?:.*?methods=\[(?P<methods>[^\]]+)\])?',
        re.DOTALL
    )
    FUNC_PATTERN = re.compile(r'def\s+(\w+)\s*\(')

    def supports_file(self, path: Path) -> bool:
        if path.suffix != '.py':
            return False
        try:
            content = path.read_text(encoding='utf-8')
            return 'flask' in content.lower() and ('@app.route' in content or '.route(' in content)
        except (OSError, UnicodeDecodeError):
            return False

    def parse(self, path: Path) -> List[RouteEntry]:
        routes: List[RouteEntry] = []
        if path.is_dir():
            for py_file in sorted(path.rglob('*.py')):
                routes.extend(self._parse_file(py_file))
        elif path.is_file():
            routes.extend(self._parse_file(path))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        try:
            content = path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return []

        routes = []
        lines = content.splitlines()

        for i, line in enumerate(lines):
            decorator_text = ''
            j = i
            # Collect multi-line decorator
            while j < len(lines) and (j == i or lines[j - 1].rstrip().endswith(',') or not decorator_text):
                decorator_text += ' ' + lines[j].strip()
                if ')' in lines[j] and j > i:
                    break
                if j > i and not lines[j - 1].rstrip().endswith(','):
                    break
                j += 1

            match = self.ROUTE_PATTERN.search(decorator_text)
            if not match:
                continue

            route_path = match.group('path')
            methods_raw = match.group('methods')
            if methods_raw:
                methods = [m.strip().strip('\'"').upper() for m in methods_raw.split(',')]
            else:
                methods = ['GET']

            # Find the function name on the next non-decorator line
            func_name = None
            for k in range(i + 1, min(i + 6, len(lines))):
                func_match = self.FUNC_PATTERN.search(lines[k])
                if func_match:
                    func_name = func_match.group(1)
                    break

            for method in methods:
                routes.append(RouteEntry(
                    path=route_path,
                    method=method,
                    handler=func_name or 'unknown',
                    source=str(path)
                ))

        return routes
