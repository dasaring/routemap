"""JSON renderer — serialises route entries to a JSON document."""

import json
from typing import Any

from routemap.parsers.base import RouteEntry


class JsonRenderer:
    """Render route entries as a JSON array.

    Each entry is a plain object with the fields:
        method, path, handler, source_file, line_number.
    """

    def __init__(self, indent: int = 2, sort_keys: bool = False) -> None:
        self.indent = indent
        self.sort_keys = sort_keys

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, routes: list[RouteEntry]) -> str:
        """Return a JSON string representing *routes*."""
        return json.dumps(
            [self._route_to_dict(r) for r in routes],
            indent=self.indent,
            sort_keys=self.sort_keys,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _route_to_dict(route: RouteEntry) -> dict[str, Any]:
        return {
            "method": route.method,
            "path": route.path,
            "handler": route.handler,
            "source_file": str(route.source_file) if route.source_file else None,
            "line_number": route.line_number,
        }
