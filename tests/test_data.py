"""Tests for synthetic dataset schema and distribution."""

from __future__ import annotations
import pytest
from pathlib import Path
from data.schemas import DisputeCase
from data.generate_cases import load_all_cases, load_case_by_id, generate_all_cases


@pytest.fixture(scope="module")
def dataset():
    return load_all_cases()


def test_dataset_total_count(dataset):
    assert len(dataset) == 100


def test_dataset_outcome_distribution(dataset):
    win_count = sum(1 for c in dataset if c.ground_truth == "win")
    lose_count = sum(1 for c in dataset if c.ground_truth == "lose")
    ambig_count = sum(1 for c in dataset if c.ground_truth == "ambiguous")

    assert win_count == 40
    assert lose_count == 40
    assert ambig_count == 20


def test_all_six_categories_present(dataset):
    expected_categories = {
        "fraudulent_unauthorized",
        "product_service_not_received",
        "product_unacceptable_defective",
        "credit_refund_not_processed",
        "duplicate_incorrect_amount",
        "subscription_recurring_cancellation",
    }
    present_categories = {c.dispute_category for c in dataset}
    assert present_categories == expected_categories


def test_each_category_has_win_lose_ambiguous(dataset):
    categories = {c.dispute_category for c in dataset}
    for cat in categories:
        cat_cases = [c for c in dataset if c.dispute_category == cat]
        outcomes = {c.ground_truth for c in cat_cases}
        assert "win" in outcomes, f"Missing win in {cat}"
        assert "lose" in outcomes, f"Missing lose in {cat}"
        assert "ambiguous" in outcomes, f"Missing ambiguous in {cat}"


def test_case_id_uniqueness(dataset):
    ids = [c.case_id for c in dataset]
    assert len(ids) == len(set(ids))


def test_case_schema_validity(dataset):
    for c in dataset:
        assert isinstance(c, DisputeCase)
        assert c.dispute_amount > 0
        assert c.currency == "INR"
        assert c.merchant_id
        assert c.merchant_name
        assert c.payment_id
        assert c.filed_date
        assert c.due_date
        assert c.ground_truth_reasoning


def test_load_case_by_id(dataset):
    sample = dataset[0]
    loaded = load_case_by_id(sample.case_id)
    assert loaded.case_id == sample.case_id
    assert loaded.ground_truth == sample.ground_truth
    assert loaded.dispute_category == sample.dispute_category


def test_reproducible_seed():
    cases1 = generate_all_cases(seed=123)
    cases2 = generate_all_cases(seed=123)
    assert [c.case_id for c in cases1] == [c.case_id for c in cases2]
    assert [c.dispute_amount for c in cases1] == [c.dispute_amount for c in cases2]

