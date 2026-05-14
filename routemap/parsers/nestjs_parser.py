import re
from pathlib import Path
from typing import List
from routemap.parsers.base import BaseParser, RouteEntry


class NestJSParser(BaseParser):
    """Parser for NestJS TypeScript controller files."""

    CONTROLLER_RE = re.compile(r"@Controller\(['\"]([^'\"]*)['\"]\)")
    ROUTE_RE = re.compile(
        r"@(Get|Post|Put|Patch|Delete|Options|Head)\((?:['\"]([^'\"]*)['\"])?\)",
        re.IGNORECASE,
    )
    METHOD_MAP = {
        "get": "GET",
        "post": "POST",
        "put": "PUT",
        "patch": "PATCH",
        "delete": "DELETE",
        "options": "OPTIONS",
        "head": "HEAD",
    }

    def supports_file(self, path: Path) -> bool:
        if path.suffix not in (".ts",):
            return False
        content = path.read_text(errors="ignore")
        return "@Controller" in content and "@nestjs/common" in content

    def parse(self, root: Path) -> List[RouteEntry]:
        routes = []
        for ts_file in root.rglob("*.ts"):
            if self.supports_file(ts_file):
                routes.extend(self._parse_file(ts_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        content = path.read_text(errors="ignore")
        routes = []

        controller_match = self.CONTROLLER_RE.search(content)
        base_path = controller_match.group(1).strip("/") if controller_match else ""

        lines = content.splitlines()
        for i, line in enumerate(lines):
            match = self.ROUTE_RE.search(line)
            if match:
                http_method = self.METHOD_MAP[match.group(1).lower()]
                sub_path = (match.group(2) or "").strip("/")
                if base_path and sub_path:
                    full_path = f"/{base_path}/{sub_path}"
                elif base_path:
                    full_path = f"/{base_path}"
                elif sub_path:
                    full_path = f"/{sub_path}"
                else:
                    full_path = "/"

                handler = None
                for j in range(i + 1, min(i + 4, len(lines))):
                    fn_match = re.search(r"(?:async\s+)?(\w+)\s*\(", lines[j])
                    if fn_match:
                        handler = fn_match.group(1)
                        break

                routes.append(
                    RouteEntry(
                        method=http_method,
                        path=full_path,
                        handler=handler,
                        source=str(path),
                    )
                )
        return routes
