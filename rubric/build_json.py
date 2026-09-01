"""Build evidence_rubric.json from category definitions."""

import json
from pathlib import Path

from rubric.defs_fraud import FRAUD_CATEGORY
from rubric.defs_pnr import PNR_CATEGORY
from rubric.defs_defective import DEFECTIVE_CATEGORY
from rubric.defs_refund import REFUND_CATEGORY
from rubric.defs_duplicate import DUPLICATE_CATEGORY
from rubric.defs_subscription import SUBSCRIPTION_CATEGORY


def build_rubric_dict():
    return {
        "version": "1.0.0",
        "last_updated": "2026-09-01",
        "description": "DisputeShield Evidence Evaluation Rubric covering card networks (Visa, Mastercard, RuPay, Amex), UPI, and Razorpay internal dispute reason codes.",
        "categories": {
            FRAUD_CATEGORY["category_id"]: FRAUD_CATEGORY,
            PNR_CATEGORY["category_id"]: PNR_CATEGORY,
            DEFECTIVE_CATEGORY["category_id"]: DEFECTIVE_CATEGORY,
            REFUND_CATEGORY["category_id"]: REFUND_CATEGORY,
            DUPLICATE_CATEGORY["category_id"]: DUPLICATE_CATEGORY,
            SUBSCRIPTION_CATEGORY["category_id"]: SUBSCRIPTION_CATEGORY,
        },
    }


def export_json(output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = Path(__file__).parent / "evidence_rubric.json"
    data = build_rubric_dict()
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    return output_path


if __name__ == "__main__":
    path = export_json()
    print(f"Generated {path} with 6 categories.")

