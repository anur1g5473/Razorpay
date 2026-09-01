"""Unit tests for the deterministic evidence scorer and abstention engine."""

from __future__ import annotations
import pytest
from agent.scorer import score_dispute_case, batch_score_cases, ScoringResult
from data.generate_cases import load_all_cases, load_case_by_id


@pytest.fixture(scope="module")
def all_cases():
    return load_all_cases()


def test_scorer_returns_scoring_result(all_cases):
    case = all_cases[0]
    result = score_dispute_case(case)
    assert isinstance(result, ScoringResult)
    assert result.case_id == case.case_id
    assert 0.0 <= result.total_score <= 100.0
    assert result.recommendation in ["CONTEST", "REVIEW", "ABSTAIN", "ACCEPT"]
    assert result.confidence in ["HIGH", "MEDIUM", "LOW"]
    assert 0.0 <= result.win_probability_estimate <= 1.0
    assert len(result.item_scores) >= 3


def test_win_cases_score_high_and_contest(all_cases):
    win_cases = [c for c in all_cases if c.ground_truth == "win"]
    assert len(win_cases) == 40

    contest_count = 0
    for c in win_cases:
        res = score_dispute_case(c)
        assert res.total_score >= 60.0, f"Win case {c.case_id} scored too low: {res.total_score}"
        if res.recommendation == "CONTEST":
            contest_count += 1
    # At least 90% of ground-truth win cases should get CONTEST recommendation
    assert contest_count >= 36, f"Only {contest_count}/40 win cases recommended CONTEST"


def test_lose_cases_score_low_or_abstain(all_cases):
    lose_cases = [c for c in all_cases if c.ground_truth == "lose"]
    assert len(lose_cases) == 40

    non_contest_count = 0
    for c in lose_cases:
        res = score_dispute_case(c)
        if res.recommendation in ["ACCEPT", "ABSTAIN", "REVIEW"]:
            non_contest_count += 1
    assert non_contest_count >= 36, f"Only {non_contest_count}/40 lose cases were flagged non-contest"


def test_ambiguous_cases_trigger_review(all_cases):
    ambig_cases = [c for c in all_cases if c.ground_truth == "ambiguous"]
    assert len(ambig_cases) == 20

    review_or_gaps = 0
    for c in ambig_cases:
        res = score_dispute_case(c)
        if res.recommendation == "REVIEW" or len(res.quality_warnings) > 0 or res.missing_important_items:
            review_or_gaps += 1
    assert review_or_gaps >= 18, f"Only {review_or_gaps}/20 ambiguous cases had review/gaps"


def test_hard_abstention_trigger_for_rto():
    pnr_rto_case = {
        "case_id": "test_rto_01",
        "dispute_category": "product_service_not_received",
        "reason_code": "13.1",
        "dispute_amount": 3500.0,
        "delivery_tracking": {
            "carrier_name": "Delhivery",
            "status": "rto",
            "rto_reason": "Customer refused delivery / address not found",
        },
    }
    res = score_dispute_case(pnr_rto_case)
    assert res.abstention_triggered is True
    assert res.recommendation == "ABSTAIN"
    assert any("returned" in r.lower() for r in res.abstention_reasons)


def test_hard_abstention_trigger_for_high_value_fraud():
    fraud_unauth_case = {
        "case_id": "test_fraud_01",
        "dispute_category": "fraudulent_unauthorized",
        "reason_code": "10.4",
        "dispute_amount": 25000.0,
        "auth_3ds": {
            "auth_type": "NONE",
            "status": "failed",
        },
    }
    res = score_dispute_case(fraud_unauth_case)
    assert res.abstention_triggered is True
    assert res.recommendation == "ABSTAIN"


def test_empty_payload_graceful_handling():
    res = score_dispute_case({})
    assert isinstance(res, ScoringResult)
    assert res.total_score <= 20.0
    assert res.recommendation in ["ACCEPT", "ABSTAIN"]


def test_batch_score_cases(all_cases):
    batch_results = batch_score_cases(all_cases[:10])
    assert len(batch_results) == 10
    for r in batch_results:
        assert isinstance(r, ScoringResult)

