"""Comprehensive tests for DisputeShield multi-step agent pipeline."""

from __future__ import annotations
import pytest
from agent.pipeline import run_pipeline, run_pipeline_batch, PipelineResult
from data.generate_cases import load_all_cases, load_case_by_id
from data.schemas import DisputeCase


@pytest.fixture(scope="module")
def all_cases():
    return load_all_cases()


def test_pipeline_run_win_case(all_cases):
    win_cases = [c for c in all_cases if c.ground_truth == "win"]
    assert len(win_cases) > 0
    case = win_cases[0]

    result = run_pipeline(case, use_llm=False)
    assert isinstance(result, PipelineResult)
    assert result.decision == "CONTEST"
    assert result.confidence == "HIGH"
    assert result.total_score >= 65.0
    assert result.win_probability_estimate >= 0.65
    assert result.predicted_outcome == "win"
    assert result.rebuttal_letter is not None
    assert len(result.rebuttal_letter) > 100
    assert result.execution_time_ms >= 0


def test_pipeline_run_lose_case(all_cases):
    lose_cases = [c for c in all_cases if c.ground_truth == "lose"]
    assert len(lose_cases) > 0
    case = lose_cases[0]

    result = run_pipeline(case, use_llm=False)
    assert isinstance(result, PipelineResult)
    assert result.decision in ("ABSTAIN", "ACCEPT")
    assert result.total_score < 60.0
    assert result.predicted_outcome == "lose"


def test_pipeline_run_ambiguous_case(all_cases):
    amb_cases = [c for c in all_cases if c.ground_truth == "ambiguous"]
    assert len(amb_cases) > 0
    case = amb_cases[0]

    result = run_pipeline(case, use_llm=False)
    assert isinstance(result, PipelineResult)
    assert result.decision == "REVIEW"
    assert len(result.missing_critical_items) > 0 or len(result.actionable_recommendations) > 0


def test_pipeline_retrieved_slices(all_cases):
    case = all_cases[0]
    result = run_pipeline(case, use_llm=False)

    slices = result.retrieved_slices
    assert isinstance(slices, dict)
    assert "transaction" in slices
    assert "customer" in slices
    assert "fulfillment" in slices
    assert "authentication" in slices
    assert "policies" in slices


def test_pipeline_supports_dict_input(all_cases):
    case_dict = all_cases[0].model_dump()
    result = run_pipeline(case_dict, use_llm=False)

    assert isinstance(result, PipelineResult)
    assert result.case_id == case_dict["case_id"]
    assert result.total_score > 0


def test_pipeline_batch_run(all_cases):
    batch = all_cases[:5]
    results = run_pipeline_batch(batch, use_llm=False)

    assert len(results) == 5
    for r in results:
        assert isinstance(r, PipelineResult)
        assert r.case_id is not None
        assert r.decision in ("CONTEST", "REVIEW", "ABSTAIN", "ACCEPT")


def test_deterministic_rebuttal_contains_facts(all_cases):
    win_cases = [c for c in all_cases if c.ground_truth == "win"]
    case = win_cases[0]
    result = run_pipeline(case, use_llm=False)

    letter = result.rebuttal_letter
    assert letter is not None
    assert case.payment_id in letter


