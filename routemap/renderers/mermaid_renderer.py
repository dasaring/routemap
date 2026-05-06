from typing import List
from routemap.parsers.base import RouteEntry


HTTP_METHOD_STYLES = {
    "GET": "fill:#d4edda,stroke:#28a745,color:#155724",
    "POST": "fill:#cce5ff,stroke:#004085,color:#004085",
    "PUT": "fill:#fff3cd,stroke:#856404,color:#856404",
    "PATCH": "fill:#fde8d8,stroke:#c05621,color:#7b341e",
    "DELETE": "fill:#f8d7da,stroke:#721c24,color:#721c24",
}


class MermaidRenderer:
    """Renders route entries as a Mermaid.js flowchart diagram."""

    def __init__(self, direction: str = "LR"):
        self.direction = direction

    def render(self, routes: List[RouteEntry]) -> str:
        lines = [f"graph {self.direction}"]
        style_classes = set()
        node_ids = {}
        counter = 0

        for route in routes:
            method = route.method.upper()
            path = route.path
            source = route.source_file or "unknown"

            source_id = self._safe_id(f"src_{source}")
            if source_id not in node_ids:
                node_ids[source_id] = source_id
                label = source.split("/")[-1]
                lines.append(f'    {source_id}["📁 {label}"]')

            node_key = f"{method}_{path}"
            if node_key not in node_ids:
                node_id = f"node{counter}"
                node_ids[node_key] = node_id
                counter += 1
                lines.append(f'    {node_id}["{method} {path}"]')
                lines.append(f"    {source_id} --> {node_id}")
                style_class = f"method{method}"
                lines.append(f"    class {node_id} {style_class}")
                style_classes.add(method)

        for method in style_classes:
            style = HTTP_METHOD_STYLES.get(method, "fill:#e2e3e5,stroke:#6c757d")
            lines.append(f"    classDef method{method} {style}")

        return "\n".join(lines) + "\n"

    def _safe_id(self, value: str) -> str:
        return value.replace("/", "_").replace(".", "_").replace("-", "_")
