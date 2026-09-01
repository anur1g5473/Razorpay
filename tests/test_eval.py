"""Unit and integration tests for DisputeShield Evaluation Harness & Metrics."""

import pytest
from eval.metrics import (
    compute_classification_metrics,
    compute_financial_metrics,
    compute_confusion_matrix,
    compute_category_breakdown,
)
from eval.harness import EvaluationHarness, run_eval


def test_compute_classification_metrics_perfect():
    preds = [
        {"expected_outcome": "WIN", "predicted_recommendation": "contest"},
        {"expected_outcome": "LOSE", "predicted_recommendation": "accept"},
        {"expected_outcome": "AMBIGUOUS", "predicted_recommendation": "human_review"},
    ]
    metrics = compute_classification_metrics(preds)
    assert metrics.accuracy == 1.0
    assert metrics.macro_f1 == 1.0
    assert metrics.precision_contest == 1.0
    assert metrics.recall_contest == 1.0


def test_compute_financial_metrics_savings():
    preds = [
        {"expected_outcome": "WIN", "predicted_recommendation": "contest", "dispute_amount": 10000.0},
        {"expected_outcome": "LOSE", "predicted_recommendation": "accept", "dispute_amount": 5000.0},
        {"expected_outcome": "LOSE", "predicted_recommendation": "contest", "dispute_amount": 3000.0},
    ]
    fin = compute_financial_metrics(preds)
    assert fin.recovered_amount_inr == 10000.0
    assert fin.prevented_penalty_fees_inr == 1500.0
    assert fin.false_contest_penalty_inr == 1500.0
    assert fin.net_financial_gain_inr > 0


def test_compute_confusion_matrix_structure():
    preds = [
        {"expected_outcome": "WIN", "predicted_recommendation": "contest"},
        {"expected_outcome": "WIN", "predicted_recommendation": "contest"},
        {"expected_outcome": "LOSE", "predicted_recommendation": "accept"},
        {"expected_outcome": "AMBIGUOUS", "predicted_recommendation": "human_review"},
    ]
    cm = compute_confusion_matrix(preds)
    assert cm["WIN"]["contest"] == 2
    assert cm["LOSE"]["accept"] == 1
    assert cm["AMBIGUOUS"]["human_review"] == 1


def test_compute_category_breakdown():
    preds = [
        {
            "category_id": "fraudulent_unauthorized",
            "category_title": "Fraud",
            "expected_outcome": "WIN",
            "predicted_recommendation": "contest",
            "dispute_amount": 5000.0,
        },
        {
            "category_id": "fraudulent_unauthorized",
            "category_title": "Fraud",
            "expected_outcome": "LOSE",
            "predicted_recommendation": "accept",
            "dispute_amount": 2000.0,
        },
    ]
    breakdown = compute_category_breakdown(preds)
    assert "fraudulent_unauthorized" in breakdown
    assert breakdown["fraudulent_unauthorized"].total_cases == 2
    assert breakdown["fraudulent_unauthorized"].accuracy == 1.0


def test_eval_harness_run_all_benchmark():
    harness = EvaluationHarness()
    summary = harness.run_all(save_results=True)
    assert summary.total_cases == 100
    assert summary.classification.accuracy >= 0.85
    assert summary.financial.net_financial_gain_inr > 0
    assert summary.latency["p95_ms"] < 250.0
