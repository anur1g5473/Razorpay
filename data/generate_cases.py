"""Synthetic dispute case generator for DisputeShield.

Generates 100 realistic dispute cases (40 win / 40 lose / 20 ambiguous)
across 6 categories, card networks, UPI, and Razorpay codes.
"""

from __future__ import annotations
import json
import random
from pathlib import Path
from typing import List, Dict, Any

from data.schemas import (
    DisputeCase,
    Auth3DSData,
    DeliveryTrackingData,
    InvoiceDispatchData,
    CustomerCommunicationLog,
    CustomerAccountData,
    RefundLogData,
    PriceBreakdownData,
    SubscriptionMandateData,
    ServiceUsageData,
)
from data.generator_helpers import (
    MERCHANTS,
    INDIAN_CITIES,
    CARRIERS,
    generate_auth_3ds,
    pick_merchant,
    pick_city,
)

CASES_DIR = Path(__file__).parent / "cases"
DATASET_PATH = Path(__file__).parent / "dataset.json"


def generate_fraud_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    city, state, pin, gps = pick_city()
    amount = round(random.uniform(500.0, 45000.0), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["10.4", "4837", "UPI-01", "RP-4001", "F29", "RZP_FRAUD_01"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])

    auth = generate_auth_3ds(verdict, amount)

    if verdict == "win":
        cust_acc = CustomerAccountData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            created_date="2025-01-10",
            prior_order_count=random.randint(4, 15),
            prior_undisputed_amount=round(amount * random.uniform(3, 8), 2),
            account_email="customer@example.in",
            account_phone="+919876543210",
            matches_billing=True,
            kyc_verified=True,
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-16T10:00:00Z",
                sender="customer",
                message="Hi, when will my order be dispatched? Please update.",
                resolution_offered="Tracking link shared via WhatsApp and email.",
                customer_response="Thanks, received tracking.",
            )
        ]
        reasoning = "Fully authenticated 3DS/UPI transaction with verified account history and customer order acknowledgment."
        notes = "Customer contacted support confirming order dispatch. Established KYC account."
    elif verdict == "lose":
        cust_acc = CustomerAccountData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            created_date="2026-08-15",
            prior_order_count=0,
            prior_undisputed_amount=0.0,
            account_email="anon_temp@mailinator.com",
            account_phone="+919999900000",
            matches_billing=False,
            kyc_verified=False,
        )
        comm = []
        reasoning = "Zero 3DS authentication (bypassed/failed), foreign VPN IP, disposable email, guest checkout."
        notes = "Fraud acknowledged internally. Transaction bypassed OTP authentication."
    else:  # ambiguous
        cust_acc = CustomerAccountData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            created_date="2026-06-01",
            prior_order_count=1,
            prior_undisputed_amount=amount,
            account_email="user_border@gmail.com",
            account_phone="+919811122233",
            matches_billing=True,
            kyc_verified=False,
        )
        comm = []
        reasoning = "3DS v1 attempted with ECI 06; secondary IP mismatch without explicit fraud acknowledgment."
        notes = "Customer claims card skimming. Partial 3DS auth."

    return DisputeCase(
        case_id=case_id,
        merchant_id=merch_id,
        merchant_name=merch_name,
        merchant_category=merch_cat,
        payment_id=f"pay_{random.randint(10000000, 99999999)}",
        dispute_amount=amount,
        currency="INR",
        payment_method=pay_method,
        card_network=network,
        dispute_category="fraudulent_unauthorized",
        reason_code=reason_code,
        reason_description="Cardholder claims unauthorized transaction",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        auth_3ds=auth,
        customer_account=cust_acc,
        customer_communication=comm,
        merchant_notes=notes,
    )



from data.category_generators import (
    generate_pnr_case,
    generate_defective_case,
    generate_refund_case,
    generate_duplicate_case,
    generate_subscription_case,
)


def generate_all_cases(seed: int = 42) -> List[DisputeCase]:
    random.seed(seed)
    cases: List[DisputeCase] = []
    current_idx = 1

    # Distribution plan: 100 cases total
    # Fraud: 20 (8 win, 8 lose, 4 ambiguous)
    # PNR: 20 (8 win, 8 lose, 4 ambiguous)
    # Defective: 16 (6 win, 6 lose, 4 ambiguous)
    # Refund: 16 (6 win, 6 lose, 4 ambiguous)
    # Duplicate: 14 (6 win, 6 lose, 2 ambiguous)
    # Subscription: 14 (6 win, 6 lose, 2 ambiguous)
    category_plans = [
        (generate_fraud_case, 8, 8, 4),
        (generate_pnr_case, 8, 8, 4),
        (generate_defective_case, 6, 6, 4),
        (generate_refund_case, 6, 6, 4),
        (generate_duplicate_case, 6, 6, 2),
        (generate_subscription_case, 6, 6, 2),
    ]

    for gen_func, win_count, lose_count, ambig_count in category_plans:
        for _ in range(win_count):
            cases.append(gen_func(current_idx, "win"))
            current_idx += 1
        for _ in range(lose_count):
            cases.append(gen_func(current_idx, "lose"))
            current_idx += 1
        for _ in range(ambig_count):
            cases.append(gen_func(current_idx, "ambiguous"))
            current_idx += 1

    return cases


def save_cases(cases: List[DisputeCase]) -> None:
    CASES_DIR.mkdir(parents=True, exist_ok=True)
    all_dict = []
    for c in cases:
        c_dict = c.model_dump()
        all_dict.append(c_dict)
        case_file = CASES_DIR / f"{c.case_id}.json"
        with open(case_file, "w", encoding="utf-8") as f:
            json.dump(c_dict, f, indent=2)

    with open(DATASET_PATH, "w", encoding="utf-8") as f:
        json.dump(
            {
                "total_cases": len(cases),
                "distribution": {
                    "win": sum(1 for c in cases if c.ground_truth == "win"),
                    "lose": sum(1 for c in cases if c.ground_truth == "lose"),
                    "ambiguous": sum(1 for c in cases if c.ground_truth == "ambiguous"),
                },
                "cases": all_dict,
            },
            f,
            indent=2,
        )
    print(f"Saved {len(cases)} cases to {CASES_DIR} and {DATASET_PATH}")


def load_all_cases() -> List[DisputeCase]:
    if DATASET_PATH.exists():
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return [DisputeCase(**c) for c in data["cases"]]
    cases = generate_all_cases()
    save_cases(cases)
    return cases


def load_case_by_id(case_id: str) -> DisputeCase:
    case_file = CASES_DIR / f"{case_id}.json"
    if case_file.exists():
        with open(case_file, "r", encoding="utf-8") as f:
            return DisputeCase(**json.load(f))
    # Fallback to load_all_cases
    for c in load_all_cases():
        if c.case_id == case_id:
            return c
    raise KeyError(f"Case with ID {case_id} not found.")


load_case = load_case_by_id


if __name__ == "__main__":
    cases = generate_all_cases()
    save_cases(cases)

