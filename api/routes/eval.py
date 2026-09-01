"""GET & POST /api/eval — run benchmark evaluation and retrieve metrics."""

from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
import json

from eval.harness import EvalHarness, EvaluationReport
from api.schemas import EvalRunRequest

router = APIRouter(prefix="/api/eval", tags=["eval"])

RESULTS_DIR = Path(__file__).resolve().parent.parent.parent / "eval" / "results"


@router.get("/results")
async def get_eval_results(
    force_rerun: bool = Query(False, description="Whether to re-run benchmark evaluation")
):
    latest_path = RESULTS_DIR / "latest_eval.json"
    benchmark_path = RESULTS_DIR / "benchmark_report.json"

    target_file = latest_path if latest_path.exists() else benchmark_path

    if target_file.exists() and not force_rerun:
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "summary" in data:
                    return data["summary"]
                return data
        except Exception:
            pass

    harness = EvalHarness(use_llm=False)
    report: EvaluationReport = harness.run_all(save_results=True)
    return report.to_dict()


@router.post("/run")
async def run_evaluation(request: Optional[EvalRunRequest] = None):
    model_name = request.model_name if request else None
    use_llm = request.use_llm if request else False
    save_results = request.save_results if request is not None else True

    harness = EvalHarness(model_name=model_name, use_llm=use_llm)
    report: EvaluationReport = harness.run_all(save_results=save_results)
    return report.to_dict()


@router.get("/summary")
async def get_eval_summary():
    latest_path = RESULTS_DIR / "latest_eval.json"
    benchmark_path = RESULTS_DIR / "benchmark_report.json"

    data = None
    target_file = latest_path if latest_path.exists() else benchmark_path
    if target_file.exists():
        try:
            with open(target_file, "r", encoding="utf-8") as f:
                raw = json.load(f)
                data = raw.get("summary", raw)
        except Exception:
            pass

    if not data:
        harness = EvalHarness(use_llm=False)
        report: EvaluationReport = harness.run_all(save_results=True)
        data = report.to_dict()

    clf = data.get("classification", {})
    fin = data.get("financial", {})

    return {
        "timestamp": data.get("timestamp"),
        "total_cases": data.get("total_cases", 0),
        "overall_accuracy": clf.get("accuracy", 0.0),
        "macro_f1": clf.get("macro_f1", 0.0),
        "precision_contest": clf.get("precision_contest", 0.0),
        "recall_contest": clf.get("recall_contest", 0.0),
        "dispute_prevention_savings_inr": fin.get("savings_vs_blind_contest_inr", 0.0),
        "net_financial_gain_inr": fin.get("net_financial_gain_inr", 0.0),
        "recovered_amount_inr": fin.get("recovered_amount_inr", 0.0),
        "category_breakdown": data.get("category_breakdown", {}),
        "confusion_matrix": data.get("confusion_matrix", {}),
        "latency": data.get("latency", {}),
    }


