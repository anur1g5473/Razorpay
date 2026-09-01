"""DisputeShield CLI entry point.

Usage:
    py -m agent --help                  Show help and available commands.
    py -m agent analyze CASE_001        Analyze a single dispute case.
    py -m agent analyze --all           Analyze all cases in the dataset.
    py -m agent eval                    Run evaluation harness over all cases.
    py -m agent list                    List all available case IDs.
"""

from __future__ import annotations

import argparse
import sys

from rich.console import Console

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="disputeshield",
        description="DisputeShield — AI-powered chargeback evidence responder.",
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── analyze ──────────────────────────────────────────────
    analyze_p = sub.add_parser("analyze", help="Analyze a dispute case")
    analyze_p.add_argument(
        "case_id",
        nargs="?",
        default=None,
        help="Case ID to analyze (e.g. CASE_001). Omit with --all to run all.",
    )
    analyze_p.add_argument(
        "--all",
        action="store_true",
        dest="run_all",
        help="Analyze every case in the dataset.",
    )

    # ── eval ─────────────────────────────────────────────────
    sub.add_parser("eval", help="Run full evaluation harness and report metrics")

    # ── list ─────────────────────────────────────────────────
    sub.add_parser("list", help="List all available case IDs")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        console.print(
            "[bold blue]DisputeShield[/bold blue] v0.1.0 — "
            "AI-powered chargeback evidence responder.\n"
        )
        parser.print_help()
        return 0

    if args.command == "analyze":
        if args.run_all:
            console.print("[yellow]⏳ Batch analysis not yet implemented (Phase 3)[/yellow]")
        elif args.case_id:
            console.print(
                f"[yellow]⏳ Analysis for [bold]{args.case_id}[/bold] "
                f"not yet implemented (Phase 3)[/yellow]"
            )
        else:
            console.print("[red]Error: provide a CASE_ID or use --all[/red]")
            return 1

    elif args.command == "eval":
        console.print("[yellow]⏳ Evaluation harness not yet implemented (Phase 4)[/yellow]")

    elif args.command == "list":
        console.print("[yellow]⏳ Case listing not yet implemented (Phase 2)[/yellow]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
