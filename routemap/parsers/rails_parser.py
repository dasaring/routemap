import re
from pathlib import Path
from typing import List
from .base import BaseParser, RouteEntry


class RailsParser(BaseParser):
    """Parser for Ruby on Rails routes.rb files."""

    HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head"}

    ROUTE_PATTERN = re.compile(
        r"^\s*(get|post|put|patch|delete|options|head)\s+['\"]([^'\"]+)['\"]\s*(?:,\s*to:\s*['\"]([^'\"]+)['\"])?\s*(?:,\s*as:\s*['\"]([^'\"]+)['\"]")?",
        re.IGNORECASE,
    )

    RESOURCE_PATTERN = re.compile(
        r"^\s*resources?\s+:([\w]+)", re.IGNORECASE
    )

    NAMESPACE_PATTERN = re.compile(
        r"^\s*namespace\s+:([\w]+)", re.IGNORECASE
    )

    def supports_file(self, path: Path) -> bool:
        return path.suffix == ".rb" and path.name == "routes.rb"

    def parse(self, path: Path) -> List[RouteEntry]:
        routes = []
        if path.is_file():
            routes.extend(self._parse_file(path))
        elif path.is_dir():
            for rb_file in path.rglob("routes.rb"):
                routes.extend(self._parse_file(rb_file))
        return routes

    def _parse_file(self, path: Path) -> List[RouteEntry]:
        routes = []
        namespace_stack = []
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeDecodeError):
            return routes

        for line in lines:
            ns_match = self.NAMESPACE_PATTERN.match(line)
            if ns_match:
                namespace_stack.append(ns_match.group(1))
                continue

            if re.match(r"^\s*end\b", line) and namespace_stack:
                namespace_stack.pop()
                continue

            route_match = self.ROUTE_PATTERN.match(line)
            if route_match:
                method = route_match.group(1).upper()
                raw_path = route_match.group(2)
                controller_action = route_match.group(3) or ""
                prefix = "/" + "/".join(namespace_stack) if namespace_stack else ""
                full_path = prefix + ("" if raw_path.startswith("/") else "/") + raw_path
                routes.append(
                    RouteEntry(
                        method=method,
                        path=full_path,
                        handler=controller_action,
                        source=str(path),
                    )
                )
                continue

            res_match = self.RESOURCE_PATTERN.match(line)
            if res_match:
                resource = res_match.group(1)
                prefix = "/" + "/".join(namespace_stack) if namespace_stack else ""
                routes.extend(self._infer_resource_routes(resource, prefix, str(path)))

        return routes

    def _infer_resource_routes(self, resource: str, prefix: str, source: str) -> List[RouteEntry]:
        base = f"{prefix}/{resource}"
        return [
            RouteEntry("GET", base, f"{resource}#index", source),
            RouteEntry("POST", base, f"{resource}#create", source),
            RouteEntry("GET", f"{base}/:id", f"{resource}#show", source),
            RouteEntry("PUT", f"{base}/:id", f"{resource}#update", source),
            RouteEntry("PATCH", f"{base}/:id", f"{resource}#update", source),
            RouteEntry("DELETE", f"{base}/:id", f"{resource}#destroy", source),
        ]
