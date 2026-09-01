"""Rubric loader and query interface for DisputeShield."""

from __future__ import annotations
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from rubric.models import EvidenceRubric, DisputeCategoryRubric, EvidenceItem
from rubric.defs_fraud import FRAUD_CATEGORY
from rubric.defs_pnr import PNR_CATEGORY
from rubric.defs_defective import DEFECTIVE_CATEGORY
from rubric.defs_refund import REFUND_CATEGORY
from rubric.defs_duplicate import DUPLICATE_CATEGORY
from rubric.defs_subscription import SUBSCRIPTION_CATEGORY

_CACHED_RUBRIC: Optional[EvidenceRubric] = None
RUBRIC_JSON_PATH = Path(__file__).parent / "evidence_rubric.json"


def get_default_rubric() -> EvidenceRubric:
    categories = {
        FRAUD_CATEGORY["category_id"]: DisputeCategoryRubric(**FRAUD_CATEGORY),
        PNR_CATEGORY["category_id"]: DisputeCategoryRubric(**PNR_CATEGORY),
        DEFECTIVE_CATEGORY["category_id"]: DisputeCategoryRubric(**DEFECTIVE_CATEGORY),
        REFUND_CATEGORY["category_id"]: DisputeCategoryRubric(**REFUND_CATEGORY),
        DUPLICATE_CATEGORY["category_id"]: DisputeCategoryRubric(**DUPLICATE_CATEGORY),
        SUBSCRIPTION_CATEGORY["category_id"]: DisputeCategoryRubric(**SUBSCRIPTION_CATEGORY),
    }
    return EvidenceRubric(
        version="1.0.0",
        last_updated="2026-09-01",
        description="DisputeShield Evidence Evaluation Rubric across card schemes (Visa, Mastercard, RuPay, Amex), UPI, and Razorpay codes.",
        categories=categories,
    )


def save_rubric_json(target_path: Optional[Path | str] = None) -> Path:
    dest = Path(target_path) if target_path else RUBRIC_JSON_PATH
    rubric = get_default_rubric()
    dest.write_text(rubric.model_dump_json(indent=2), encoding="utf-8")
    return dest


def load_rubric(force_reload: bool = False) -> EvidenceRubric:
    """Load rubric from JSON if present, falling back to embedded python definition."""
    global _CACHED_RUBRIC
    if _CACHED_RUBRIC is not None and not force_reload:
        return _CACHED_RUBRIC

    if RUBRIC_JSON_PATH.exists():
        try:
            with open(RUBRIC_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            _CACHED_RUBRIC = EvidenceRubric(**data)
            return _CACHED_RUBRIC
        except Exception:
            _CACHED_RUBRIC = get_default_rubric()
            return _CACHED_RUBRIC
    _CACHED_RUBRIC = get_default_rubric()
    save_rubric_json()
    return _CACHED_RUBRIC


def get_rubric() -> EvidenceRubric:
    return load_rubric()


def get_reason_code_mapping() -> Dict[str, str]:
    """Map every reason code string to its category_id."""
    rubric = get_rubric()
    mapping: Dict[str, str] = {}
    for cat_id, cat in rubric.categories.items():
        mapping[cat_id.lower()] = cat_id
        for code in cat.reason_codes:
            mapping[code.lower()] = cat_id
            mapping[code.upper()] = cat_id
    return mapping


def get_category_rubric(category_or_code: str) -> Optional[DisputeCategoryRubric]:
    """Retrieve category rubric by category ID slug or network reason code."""
    rubric = get_rubric()
    clean_query = category_or_code.strip()
    if clean_query in rubric.categories:
        return rubric.categories[clean_query]

    clean_lower = clean_query.lower()
    for cat_id, cat in rubric.categories.items():
        if clean_lower in cat_id.lower() or cat_id.lower() in clean_lower:
            return cat
        for code in cat.reason_codes:
            if clean_lower == code.lower() or clean_query == code:
                return cat
    return None


def list_categories() -> List[str]:
    """Return all supported category IDs."""
    rubric = get_rubric()
    return list(rubric.categories.keys())


def get_required_evidence_items(category_or_code: str) -> List[EvidenceItem]:
    """Return required evidence items for a given category or reason code."""
    cat = get_category_rubric(category_or_code)
    if cat is None:
        return []
    return cat.required_evidence


def check_abstention_triggers(category_id: str, case_data: Dict[str, Any]) -> List[str]:
    """Evaluate deterministic rules to identify whether case must abstain and escalate to human."""
    triggers: List[str] = []
    cat = get_category_rubric(category_id)
    if not cat:
        return ["Unknown dispute category requiring manual review."]

    amount = float(case_data.get("dispute_amount", 0.0) or case_data.get("amount", 0.0))
    metadata = case_data.get("metadata", {})
    notes = str(case_data.get("merchant_notes", "")).lower()
    delivery_status = str(case_data.get("delivery_status", "")).lower()
    auth_3ds = case_data.get("auth_3ds", {})

    # Universal triggers
    if "fraud acknowledged" in notes or "merchant fault" in notes or "internal error" in notes:
        triggers.append("Merchant internal notes acknowledge operational defect or merchant liability.")

    if category_id == "fraudulent_unauthorized":
        eci = str(auth_3ds.get("eci", "")).strip()
        auth_status = str(auth_3ds.get("status", "")).lower()
        if not auth_3ds or (auth_status not in ["success", "authenticated"] and eci not in ["05", "02", "06"]):
            if amount > 10000.0:
                triggers.append(
                    f"High-value dispute (INR {amount:,.2f}) completely lacks 3D Secure / UPI OTP liability shift."
                )

    elif category_id == "product_service_not_received":
        if delivery_status in ["rto", "returned_to_origin", "failed", "cancelled", "undelivered"]:
            triggers.append(f"Courier tracking indicates package was returned/undelivered (status: '{delivery_status}').")

    elif category_id == "credit_refund_not_processed":
        refund_status = str(case_data.get("refund_status", "")).lower()
        if "promised" in notes and refund_status not in ["success", "processed", "settled"]:
            triggers.append("Merchant communications confirm refund was promised but no ARN reference was generated.")

    elif category_id == "duplicate_incorrect_amount":
        if case_data.get("gateway_retry_duplicate") is True:
            triggers.append("Gateway logs confirm automated payment retry created duplicate capture.")

    elif category_id == "subscription_recurring_cancellation":
        cancellation_date = case_data.get("cancellation_requested_date")
        charge_date = case_data.get("charge_date")
        if cancellation_date and charge_date and cancellation_date < charge_date:
            triggers.append("Customer cancellation timestamp preceded recurring billing execution.")

    return triggers
