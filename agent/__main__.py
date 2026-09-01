"""DisputeShield CLI — AI-powered chargeback evidence responder."""

from __future__ import annotations
import argparse
import sys
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from data.generate_cases import load_all_cases, load_case_by_id, DisputeCase
from agent.pipeline import DisputePipeline, PipelineResult
from eval.harness import EvaluationHarness

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="disputeshield",
        description="DisputeShield — Autonomous AI Chargeback Defense & Rubric-Scored Evidence Responder.",
    )
    sub = parser.add_subparsers(dest="command", help="Available subcommands")

    # analyze
    analyze_p = sub.add_parser("analyze", help="Analyze a dispute case and generate rebuttal")
    analyze_p.add_argument("case_id", nargs="?", default=None, help="Case ID to analyze (e.g. CASE_001)")
    analyze_p.add_argument("--all", action="store_true", dest="run_all", help="Analyze all cases in dataset")
    analyze_p.add_argument("--llm", action="store_true", help="Enable LLM rebuttal drafting")

    # eval
    sub.add_parser("eval", help="Run full benchmark evaluation harness over 100 dispute cases")

    # list
    list_p = sub.add_parser("list", help="List all dispute cases in the dataset")
    list_p.add_argument("--category", type=str, default=None, help="Filter by category")
    list_p.add_argument("--outcome", type=str, default=None, help="Filter by ground truth outcome")
    list_p.add_argument("--limit", type=int, default=25, help="Limit number of cases displayed")

    return parser



def handle_list(category: Optional[str] = None, outcome: Optional[str] = None, limit: int = 25) -> int:
    cases = load_all_cases()
    if category:
        cases = [c for c in cases if category.lower() in c.dispute_category.lower()]
    if outcome:
        cases = [c for c in cases if c.ground_truth.lower() == outcome.lower()]

    table = Table(
        title=f"DisputeShield Cases (Showing {min(len(cases), limit)} of {len(cases)})",
        box=box.ROUNDED,
        header_style="bold cyan",
    )
    table.add_column("Case ID", style="bold yellow", width=12)
    table.add_column("Category", style="green", width=28)
    table.add_column("Amount", justify="right", style="bold white", width=14)
    table.add_column("Outcome", justify="center", width=12)
    table.add_column("Key Ground Truth Reasoning", style="dim", width=40)

    for c in cases[:limit]:
        outcome_style = "bold green" if c.ground_truth == "win" else "bold red" if c.ground_truth == "lose" else "bold yellow"
        table.add_row(
            c.case_id,
            c.dispute_category.replace("_", " ").title()[:26],
            f"{c.currency} {c.dispute_amount:,.2f}",
            f"[{outcome_style}]{c.ground_truth.upper()}[/{outcome_style}]",
            c.ground_truth_reasoning[:38] + ("..." if len(c.ground_truth_reasoning) > 38 else ""),
        )

    console.print(table)
    return 0


def handle_analyze_single(case_id: str, use_llm: bool = False) -> int:
    try:
        case = load_case_by_id(case_id)
    except FileNotFoundError:
        console.print(f"[bold red]Error:[/bold red] Case [bold]{case_id}[/bold] not found in dataset.")
        return 1

    pipeline = DisputePipeline(use_llm=use_llm)
    result = pipeline.run(case)

    dec_color = "green" if result.decision == "CONTEST" else "red" if result.decision in ("ABSTAIN", "ACCEPT") else "yellow"
    prob_pct = f"{result.win_probability_estimate * 100:.1f}%"

    console.print()
    console.print(Panel(
        f"[bold white]Case ID:[/bold white] {case.case_id}  |  "
        f"[bold white]Category:[/bold white] {result.category_title}  |  "
        f"[bold white]Amount:[/bold white] {case.currency} {case.dispute_amount:,.2f}\n"
        f"[bold white]Decision:[/bold white] [{dec_color} bold]{result.decision}[/{dec_color} bold]  |  "
        f"[bold white]Confidence Score:[/bold white] {result.total_score:.1f}/100  |  "
        f"[bold white]Win Probability:[/bold white] {prob_pct}  |  "
        f"[bold white]Latency:[/bold white] {result.execution_time_ms:.1f}ms",
        title="[bold blue]DisputeShield Defense Analysis[/bold blue]",
        border_style="blue",
        box=box.ROUNDED,
    ))

    table = Table(title="Rubric Evidence Evaluation", box=box.SIMPLE, header_style="bold magenta")
    table.add_column("Evidence Item", style="white")
    table.add_column("Level", justify="center")
    table.add_column("Weight", justify="right")
    table.add_column("Points Awarded", justify="right")
    table.add_column("Findings / Notes", style="dim")

    for item in result.scoring_result.evidence_breakdown:
        lvl_style = "bold red" if item.compelling_level == "critical" else "bold yellow" if item.compelling_level == "important" else "cyan"
        pts_style = "green" if item.points_awarded > 0 else "red"
        table.add_row(
            item.name,
            f"[{lvl_style}]{item.compelling_level.upper()}[/{lvl_style}]",
            f"{item.weight:.1f}",
            f"[{pts_style}]{item.points_awarded:.1f}[/{pts_style}]",
            "; ".join(item.findings)[:60] if item.findings else "No issues found",
        )
    console.print(table)

    if result.scoring_result.abstention_reasons:
        console.print(Panel(
            "\n".join([f"• {r}" for r in result.scoring_result.abstention_reasons]),
            title="[bold red]Abstention / Review Triggers Detected[/bold red]",
            border_style="red",
        ))

    if result.rebuttal_letter:
        console.print(Panel(
            result.rebuttal_letter,
            title="[bold green]Drafted Representation Letter[/bold green]",
            border_style="green",
            box=box.ROUNDED,
        ))

    return 0


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
