"""Graphviz DOT format renderer for route maps."""
from typing import List, Dict
from routemap.parsers.base import RouteEntry

METHOD_COLORS = {
    "GET": "#61affe",
    "POST": "#49cc90",
    "PUT": "#fca130",
    "PATCH": "#50e3c2",
    "DELETE": "#f93e3e",
    "OPTIONS": "#0d5aa7",
    "HEAD": "#9012fe",
}


class DotRenderer:
    """Renders route entries as a Graphviz DOT graph."""

    def __init__(self, rankdir: str = "LR", concentrate: bool = True):
        """
        Args:
            rankdir: Graph layout direction ('LR', 'TB', 'RL', 'BT').
            concentrate: Whether to merge parallel edges.
        """
        self.rankdir = rankdir
        self.concentrate = concentrate

    def render(self, routes: List[RouteEntry]) -> str:
        """Render routes as a DOT graph string."""
        lines = []
        lines.append("digraph routemap {")
        lines.append(f'    rankdir={self.rankdir};')
        lines.append(f'    concentrate={str(self.concentrate).lower()};')
        lines.append('    node [shape=box fontname="Helvetica" fontsize=11];')
        lines.append('    edge [fontname="Helvetica" fontsize=9];')
        lines.append("")

        grouped = self._group_by_source(routes)

        for source, source_routes in grouped.items():
            safe_source = self._safe_id(source)
            lines.append(f'    subgraph cluster_{safe_source} {{')
            lines.append(f'        label="{source}";')
            lines.append('        style=filled;')
            lines.append('        color=lightgrey;')
            lines.append("")

            for route in source_routes:
                node_id = self._safe_id(f"{source}_{route.method}_{route.path}")
                color = METHOD_COLORS.get(route.method.upper(), "#888888")
                label = f"{route.method}\\n{route.path}"
                lines.append(
                    f'        {node_id} [label="{label}" '
                    f'style=filled fillcolor="{color}" fontcolor=white];'
                )

            lines.append("    }")
            lines.append("")

        lines.append("}")
        return "\n".join(lines)

    def _group_by_source(self, routes: List[RouteEntry]) -> Dict[str, List[RouteEntry]]:
        grouped: Dict[str, List[RouteEntry]] = {}
        for route in routes:
            grouped.setdefault(route.source_file, []).append(route)
        return grouped

    def _safe_id(self, value: str) -> str:
        """Convert a string to a valid DOT identifier."""
        return "".join(c if c.isalnum() else "_" for c in value)
