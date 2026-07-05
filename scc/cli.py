"""Command-line interface for skill-collision-checker.

Usage:
    python -m scc check [root] [options]

Positional:
    root           path to a directory of skill folders (each containing a
                   SKILL.md), or a single skill's directory. Defaults to
                   ~/.claude/skills.

Options:
    --plugin PATH  an additional skills directory to include (repeatable) -
                   use this for a plugin's skills dir alongside the main root.
    --threshold F  keyword/phrase collision score threshold, 0-1 (default 0.3)
    --near-ratio F text-similarity ratio for near-duplicate wording (default 0.85)
    --html PATH    also write a self-contained HTML report
    --md PATH      also write a Markdown report
    --quiet        suppress the text report on stdout

Exit code 0 on success (this is a report, not a gate - it never fails on
"collisions found"), 2 on a usage/IO error.
"""

from __future__ import annotations

import argparse
import os
import sys

from .audit import check as run_check
from . import report as report_mod

DEFAULT_ROOT = os.path.join(os.path.expanduser("~"), ".claude", "skills")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scc",
        description="Find trigger-keyword collisions in a Claude Code skill corpus (offline, suggest-only).",
    )
    sub = parser.add_subparsers(dest="command")
    a = sub.add_parser("check", help="check a directory of SKILL.md files for collisions")
    a.add_argument("root", nargs="?", default=DEFAULT_ROOT,
                    help=f"skills directory to scan (default: {DEFAULT_ROOT})")
    a.add_argument("--plugin", action="append", default=[], metavar="PATH",
                    help="an additional skills directory to include (repeatable)")
    a.add_argument("--threshold", type=float, default=0.3, help="collision score threshold, 0-1 (default 0.3)")
    a.add_argument("--near-ratio", type=float, default=0.85, help="near-duplicate text-similarity ratio (default 0.85)")
    a.add_argument("--html", default=None, help="write an HTML report to this path")
    a.add_argument("--md", default=None, help="write a Markdown report to this path")
    a.add_argument("--quiet", action="store_true", help="suppress stdout text report")
    return parser


def _ensure_parent(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)


def run(args) -> int:
    roots = [args.root] + list(args.plugin)
    try:
        result = run_check(roots, threshold=args.threshold, near_ratio=args.near_ratio)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not args.quiet:
        print(report_mod.render_text(result))
    if args.html:
        _ensure_parent(args.html)
        with open(args.html, "w", encoding="utf-8") as handle:
            handle.write(report_mod.render_html(result))
        if not args.quiet:
            print(f"\nwrote HTML report: {args.html}")
    if args.md:
        _ensure_parent(args.md)
        with open(args.md, "w", encoding="utf-8") as handle:
            handle.write(report_mod.render_markdown(result))
        if not args.quiet:
            print(f"wrote Markdown report: {args.md}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "check":
        return run(args)
    parser.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
