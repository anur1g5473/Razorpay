"""Evaluation harness — runs the full DisputeShield pipeline over test cases."""

from __future__ import annotations
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional

from data.generate_cases import load_all_cases, DisputeCase
from agent.pipeline import DisputePipeline, PipelineResult
from eval.metrics import (
    ClassificationMetrics,
    FinancialCostMetrics,
    CategoryPerformance,
    EvaluationSummary,
    compute_classification_metrics,
    compute_confusion_matrix,
    compute_financial_metrics,
    compute_category_breakdown,
)

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


EvaluationReport = EvaluationSummary


class EvaluationHarness:
    def __init__(
        self,
        pipeline: Optional[DisputePipeline] = None,
        model_name: Optional[str] = None,
        use_llm: bool = False,
    ):
        self.pipeline = pipeline or DisputePipeline(model_name=model_name, use_llm=use_llm)

    def run_case(self, case: DisputeCase) -> Dict[str, Any]:
        start_t = time.perf_counter()
        result: PipelineResult = self.pipeline.run(case)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        decision_map = {
            "CONTEST": "contest",
            "ACCEPT": "accept",
            "ABSTAIN": "accept",
            "REVIEW": "human_review",
            "HUMAN_REVIEW": "human_review",
        }
        rec = decision_map.get(result.decision.upper(), "human_review")

        return {
            "case_id": case.case_id,
            "category_id": case.dispute_category,
            "category_title": result.category_title,
            "dispute_amount": case.dispute_amount,
            "currency": case.currency,
            "expected_outcome": case.ground_truth.upper(),
            "key_flaw_or_asset": case.ground_truth_reasoning,
            "predicted_recommendation": rec,
            "predicted_win_probability": result.win_probability_estimate,
            "predicted_confidence": result.total_score,
            "is_abstaining": result.scoring_result.is_abstaining,
            "abstention_reasons": result.scoring_result.abstention_reasons,
            "rebuttal_drafted": bool(result.rebuttal_letter),
            "rebuttal_length": len(result.rebuttal_letter) if result.rebuttal_letter else 0,
            "retrieved_slices_count": len(result.retrieved_slices),
            "latency_ms": round(elapsed_ms, 2),
        }

    def run_all(
        self,
        cases: Optional[List[DisputeCase]] = None,
        save_results: bool = True,
    ) -> EvaluationSummary:
        if cases is None:
            cases = load_all_cases()

        predictions: List[Dict[str, Any]] = []
        latencies: List[float] = []

        for case in cases:
            pred = self.run_case(case)
            predictions.append(pred)
            latencies.append(pred["latency_ms"])

        classification = compute_classification_metrics(predictions)
        financial = compute_financial_metrics(predictions)
        confusion = compute_confusion_matrix(predictions)
        categories = compute_category_breakdown(predictions)

        latencies.sort()
        n_lat = len(latencies)
        latency_stats = {
            "mean_ms": round(sum(latencies) / n_lat, 2) if n_lat > 0 else 0.0,
            "min_ms": round(min(latencies), 2) if n_lat > 0 else 0.0,
            "max_ms": round(max(latencies), 2) if n_lat > 0 else 0.0,
            "p50_ms": round(latencies[int(n_lat * 0.50)], 2) if n_lat > 0 else 0.0,
            "p95_ms": round(latencies[min(int(n_lat * 0.95), n_lat - 1)], 2) if n_lat > 0 else 0.0,
        }

        eval_id = f"eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
        summary = EvaluationSummary(
            evaluation_id=eval_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            total_cases=len(predictions),
            classification=classification,
            financial=financial,
            confusion_matrix=confusion,
            category_breakdown=categories,
            latency=latency_stats,
        )

        if save_results:
            self._save_results(summary, predictions)

        return summary




    def _save_results(self, summary: EvaluationSummary, predictions: List[Dict[str, Any]]) -> None:
        latest_json = RESULTS_DIR / "latest_eval.json"
        full_payload = {
            "summary": summary.model_dump(),
            "predictions": predictions,
        }
        with open(latest_json, "w", encoding="utf-8") as f:
            json.dump(full_payload, f, indent=2)

        md_path = RESULTS_DIR / "eval_report.md"
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(self.generate_markdown_report(summary))

    def generate_markdown_report(self, summary: EvaluationSummary) -> str:
        c = summary.classification
        f = summary.financial
        cm = summary.confusion_matrix
        l = summary.latency

        lines = [
            "# DisputeShield — Benchmark Evaluation Report\n",
            f"> **Evaluation Run ID:** `{summary.evaluation_id}`  ",
            f"> **Date:** {summary.timestamp}  ",
            f"> **Total Evaluated Cases:** {summary.total_cases}",
            "\n## 1. Executive Summary & Core Metrics\n",
            "| Metric | Value | Benchmark Target | Status |",
            "|---|---|---|---|",
            f"| **Overall Accuracy** | **{c.accuracy * 100:.1f}%** | > 85.0% | {'PASS' if c.accuracy >= 0.85 else 'REVIEW'} |",
            f"| **Contest Precision** | **{c.precision_contest * 100:.1f}%** | > 90.0% | {'PASS' if c.precision_contest >= 0.90 else 'REVIEW'} |",
            f"| **Contest Recall** | **{c.recall_contest * 100:.1f}%** | > 85.0% | {'PASS' if c.recall_contest >= 0.85 else 'REVIEW'} |",
            f"| **Macro F1 Score** | **{c.macro_f1:.4f}** | > 0.8500 | {'PASS' if c.macro_f1 >= 0.85 else 'REVIEW'} |",
            f"| **P95 Latency** | **{l['p95_ms']:.1f} ms** | < 250 ms | {'PASS' if l['p95_ms'] < 250 else 'SLOW'} |",
            "\n## 2. Confusion Matrix\n",
            "| Ground Truth \\ Recommendation | Contest (Win) | Accept (Concede) | Human Review (Abstain) |",
            "|---|---|---|---|",
            f"| **Actual WIN** (40 cases) | **{cm['WIN']['contest']}** | {cm['WIN']['accept']} | {cm['WIN']['human_review']} |",
            f"| **Actual LOSE** (40 cases) | {cm['LOSE']['contest']} | **{cm['LOSE']['accept']}** | {cm['LOSE']['human_review']} |",
            f"| **Actual AMBIGUOUS** (20 cases) | {cm['AMBIGUOUS']['contest']} | {cm['AMBIGUOUS']['accept']} | **{cm['AMBIGUOUS']['human_review']}** |",
            "\n## 3. Financial Cost & ROI Analysis\n",
            f"- **Total Disputed Volume:** INR {f.total_disputed_amount_inr:,.2f}",
            f"- **Direct Recovered Amount:** INR {f.recovered_amount_inr:,.2f} ({f.recovery_rate_pct:.1f}% of winnable volume)",
            f"- **Prevented Representation Penalties:** INR {f.prevented_penalty_fees_inr:,.2f}",
            f"- **False Contest Penalty Incurred:** INR {f.false_contest_penalty_inr:,.2f}",
            f"- **Net Financial Gain:** **INR {f.net_financial_gain_inr:,.2f}**",
            f"- **Savings vs Blind Automated Contest:** **INR {f.savings_vs_blind_contest_inr:,.2f}**",
            "\n## 4. Category Performance Breakdown\n",
            "| Category | Total Cases | Accuracy | Macro F1 | Net Financial Gain |",
            "|---|---|---|---|---|",
        ]

        for cat_id, cat in summary.category_breakdown.items():
            lines.append(
                f"| {cat.category_title} | {cat.total_cases} | {cat.accuracy * 100:.1f}% | {cat.macro_f1:.4f} | INR {cat.net_gain_inr:,.2f} |"
            )

        lines.extend([
            "\n## 5. Performance Latency Profile\n",
            f"- **Mean Latency:** {l['mean_ms']} ms",
            f"- **Median (P50):** {l['p50_ms']} ms",
            f"- **P95 Latency:** {l['p95_ms']} ms",
            f"- **Min / Max:** {l['min_ms']} ms / {l['max_ms']} ms",
        ])

        return "\n".join(lines)


def run_eval() -> EvaluationSummary:
    harness = EvaluationHarness()
    summary = harness.run_all(save_results=True)
    print(f"Evaluation complete: {summary.total_cases} cases evaluated.")
    print(f"Accuracy: {summary.classification.accuracy * 100:.1f}% | Macro F1: {summary.classification.macro_f1:.4f}")
    print(f"Net Gain: Rs {summary.financial.net_financial_gain_inr:,.2f} | P95: {summary.latency['p95_ms']} ms")
    return summary



EvalHarness = EvaluationHarness

if __name__ == "__main__":
    run_eval()

