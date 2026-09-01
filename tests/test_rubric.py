"""Tests for evidence rubric loading, validation, queries, and abstention triggers."""

from __future__ import annotations
import pytest
from rubric.rubric_loader import (
    load_rubric,
    get_rubric,
    get_category_rubric,
    list_categories,
    get_reason_code_mapping,
    get_required_evidence_items,
    check_abstention_triggers,
)
from rubric.models import EvidenceRubric, DisputeCategoryRubric


def test_rubric_load():
    """Verify that rubric loads successfully with expected top-level metadata."""
    rubric = get_rubric()
    assert isinstance(rubric, EvidenceRubric)
    assert rubric.version == "1.0.0"
    assert len(rubric.categories) == 6


def test_all_six_categories_exist():
    """Verify all 6 standardized dispute categories are defined."""
    categories = list_categories()
    expected = [
        "fraudulent_unauthorized",
        "product_service_not_received",
        "product_unacceptable_defective",
        "credit_refund_not_processed",
        "duplicate_incorrect_amount",
        "subscription_recurring_cancellation",
    ]
    for exp in expected:
        assert exp in categories, f"Category '{exp}' missing from rubric"


@pytest.mark.parametrize(
    "cat_id",
    [
        "fraudulent_unauthorized",
        "product_service_not_received",
        "product_unacceptable_defective",
        "credit_refund_not_processed",
        "duplicate_incorrect_amount",
        "subscription_recurring_cancellation",
    ],
)
def test_category_structure_and_weights(cat_id: str):
    """Verify category weights sum to 100 and items have non-empty fields."""
    cat = get_category_rubric(cat_id)
    assert cat is not None
    assert isinstance(cat, DisputeCategoryRubric)
    assert len(cat.reason_codes) >= 4
    assert len(cat.required_evidence) >= 3
    assert len(cat.abstention_triggers) >= 1
    assert cat.win_probability_thresholds.high > cat.win_probability_thresholds.medium

    total_weight = sum(item.weight for item in cat.required_evidence)
    assert total_weight == 100.0, f"Category {cat_id} weights sum to {total_weight}, expected 100.0"

    for item in cat.required_evidence:
        assert item.item_id
        assert item.name
        assert item.compelling_level in ["critical", "important", "supporting"]
        assert len(item.required_fields) > 0
        assert len(item.strong_evidence_indicators) > 0
        assert len(item.weak_evidence_indicators) > 0


def test_reason_code_lookup():
    """Verify network reason codes map correctly to their categories."""
    test_cases = [
        ("10.4", "fraudulent_unauthorized"),
        ("4837", "fraudulent_unauthorized"),
        ("UPI-01", "fraudulent_unauthorized"),
        ("13.1", "product_service_not_received"),
        ("4855", "product_service_not_received"),
        ("13.3", "product_unacceptable_defective"),
        ("4853", "product_unacceptable_defective"),
        ("13.6", "credit_refund_not_processed"),
        ("4860", "credit_refund_not_processed"),
        ("12.6", "duplicate_incorrect_amount"),
        ("4834", "duplicate_incorrect_amount"),
        ("13.7", "subscription_recurring_cancellation"),
        ("4841", "subscription_recurring_cancellation"),
    ]
    for code, expected_cat in test_cases:
        cat = get_category_rubric(code)
        assert cat is not None, f"Failed lookup for code '{code}'"
        assert cat.category_id == expected_cat, f"Code '{code}' resolved to '{cat.category_id}', expected '{expected_cat}'"


def test_reason_code_mapping_completeness():
    """Verify global reason code map contains both lower and upper case entries."""
    mapping = get_reason_code_mapping()
    assert "10.4" in mapping
    assert "upi-01" in mapping
    assert "UPI-01" in mapping
    assert mapping["upi-01"] == "fraudulent_unauthorized"


def test_required_evidence_items_query():
    """Verify extraction of evidence requirements by category and by code."""
    items_by_cat = get_required_evidence_items("fraudulent_unauthorized")
    assert len(items_by_cat) >= 4
    items_by_code = get_required_evidence_items("10.4")
    assert len(items_by_code) == len(items_by_cat)


def test_abstention_triggers_detection():
    """Verify programmatic abstention trigger detection under critical failure conditions."""
    # 1. High value fraud without 3DS
    triggers = check_abstention_triggers(
        "fraudulent_unauthorized",
        {
            "dispute_amount": 25000.0,
            "auth_3ds": {"status": "failed", "eci": "07"},
        },
    )
    assert len(triggers) >= 1
    assert "liability shift" in triggers[0]

    # 2. PNR with package RTO
    pnr_triggers = check_abstention_triggers(
        "product_service_not_received",
        {
            "dispute_amount": 1500.0,
            "delivery_status": "returned_to_origin",
        },
    )
    assert len(pnr_triggers) >= 1
    assert "returned/undelivered" in pnr_triggers[0]

    # 3. Credit not processed with refund promised
    refund_triggers = check_abstention_triggers(
        "credit_refund_not_processed",
        {
            "merchant_notes": "We promised customer a full refund on 12th Aug",
            "refund_status": "pending_manual",
        },
    )
    assert len(refund_triggers) >= 1
    assert "promised" in refund_triggers[0]

