"""Credit or Refund Not Processed Category Rubric Definition."""

REFUND_CATEGORY = {
    "category_id": "credit_refund_not_processed",
    "title": "Credit or Refund Not Processed",
    "description": "Cardholder claims they were promised a refund or credit that was never credited to their account.",
    "reason_codes": ["13.6", "4860", "UPI-05", "RP-4004", "C04", "RZP_REF_06"],
    "required_evidence": [
        {
            "item_id": "refund_proof_or_cancellation_policy",
            "name": "Refund Reference / ARN / Policy Proof",
            "weight": 40.0,
            "compelling_level": "critical",
            "required_fields": ["refund_id", "arn_rrn", "refund_amount", "refund_timestamp", "status"],
            "strong_evidence_indicators": [
                "Valid Bank ARN / RRN showing refund was processed to original payment method prior to dispute",
                "Explicit non-refundable policy accepted by customer for custom/non-cancellable service"
            ],
            "weak_evidence_indicators": [
                "Refund initiated internally but failed at gateway",
                "No ARN/RRN generated prior to dispute filing"
            ]
        },
        {
            "item_id": "cancellation_timestamp_log",
            "name": "Cancellation Cutoff & Timestamp Verification",
            "weight": 30.0,
            "compelling_level": "important",
            "required_fields": ["order_timestamp", "cancellation_request_timestamp", "policy_cutoff_hours"],
            "strong_evidence_indicators": [
                "Cancellation requested after published deadline (e.g. < 24h before event or post-dispatch)",
                "No cancellation request submitted in merchant system"
            ],
            "weak_evidence_indicators": [
                "Cancellation submitted within allowed policy window before cutoff"
            ]
        },
        {
            "item_id": "merchant_customer_communication",
            "name": "Store Credit Agreement / Ticket Communication",
            "weight": 30.0,
            "compelling_level": "important",
            "required_fields": ["ticket_id", "agreed_resolution", "store_credit_voucher_code"],
            "strong_evidence_indicators": [
                "Customer explicitly agreed in email to accept store credit/voucher in lieu of cash refund",
                "Voucher issued and partially/fully redeemed by customer"
            ],
            "weak_evidence_indicators": [
                "Store credit issued unilaterally without customer consent"
            ]
        }
    ],
    "abstention_triggers": [
        "Merchant promised cash refund in email thread but failed to execute refund transaction",
        "Refund processed to incorrect account or bounced payment method without customer notice"
    ],
    "win_probability_thresholds": {"high": 0.85, "medium": 0.50}
}
