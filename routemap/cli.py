"""Command-line interface for routemap."""

import argparse
import sys
from pathlib import Path

from routemap.parsers import get_parser
from routemap.renderers import get_renderer


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="routemap",
        description="Generate visual API route maps from Express and FastAPI codebases.",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to the project directory or a single file to analyse.",
    )
    parser.add_argument(
        "--renderer",
        choices=["ascii", "mermaid"],
        default="ascii",
        help="Output renderer (default: ascii).",
    )
    parser.add_argument(
        "--direction",
        default="LR",
        help="Graph direction for Mermaid renderer (default: LR).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI colour output (ASCII renderer only).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write output to a file instead of stdout.",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    target: Path = args.path.resolve()
    if not target.exists():
        print(f"error: path does not exist: {target}", file=sys.stderr)
        return 1

    files = [target] if target.is_file() else list(target.rglob("*"))

    all_routes = []
    for file in files:
        parser = get_parser(file)
        if parser is not None:
            all_routes.extend(parser.parse(file))

    if not all_routes:
        print("No routes found.", file=sys.stderr)
        return 0

    renderer_kwargs = {}
    if args.renderer == "mermaid":
        renderer_kwargs["direction"] = args.direction
    elif args.renderer == "ascii":
        renderer_kwargs["use_color"] = not args.no_color

    renderer = get_renderer(args.renderer, **renderer_kwargs)
    output = renderer.render(all_routes)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"Output written to {args.output}")
    else:
        print(output)

    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
