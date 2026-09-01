"""Cancelled Subscription / Recurring Charge Category."""

CATEGORY = {
    "category_id": "subscription_recurring_cancellation",
    "title": "Cancelled Subscription / Recurring Charge",
    "description": "Cardholder claims they cancelled recurring subscription prior to billing or were charged after cancellation.",
    "reason_codes": ["13.7", "4841", "UPI-06", "RP-4006", "C06", "RZP_SUB_03"],
    "required_evidence": [
        {
            "item_id": "subscription_contract_terms",
            "name": "Subscription Terms & Mandate Agreement",
            "weight": 35.0,
            "compelling_level": "critical",
            "required_fields": ["subscription_id", "mandate_id", "billing_cycle", "recurrence_amount", "terms_acceptance_timestamp"],
            "strong_evidence_indicators": [
                "Active E-Mandate / SI registered with bank authentication",
                "Clear recurring billing terms with frequency, price, and auto-renew policy accepted at signup"
            ],
            "weak_evidence_indicators": [
                "Missing recurring mandate registration proof"
            ]
        },
        {
            "item_id": "cancellation_policy_compliance",
            "name": "Cancellation Request & Log Audit",
            "weight": 35.0,
            "compelling_level": "critical",
            "required_fields": ["cancellation_timestamp", "cancellation_status", "effective_end_date", "billing_date"],
            "strong_evidence_indicators": [
                "No cancellation request submitted prior to recurring billing date",
                "Cancellation request submitted AFTER renewal cutoff date specified in terms"
            ],
            "weak_evidence_indicators": [
                "Cancellation requested before billing date but merchant failed to process cancellation in CRM"
            ]
        },
        {
            "item_id": "service_usage_during_period",
            "name": "Service Usage Activity During Disputed Period",
            "weight": 20.0,
            "compelling_level": "important",
            "required_fields": ["period_start_date", "period_end_date", "active_login_count", "features_used"],
            "strong_evidence_indicators": [
                "Customer actively logged in and utilized subscription features during the disputed billing cycle"
            ],
            "weak_evidence_indicators": [
                "Zero login or service usage recorded during disputed cycle"
            ]
        },
        {
            "item_id": "recurring_billing_notification",
            "name": "Pre-Debit Renewal Notification Log",
            "weight": 10.0,
            "compelling_level": "supporting",
            "required_fields": ["pre_debit_notification_id", "sent_timestamp", "channel"],
            "strong_evidence_indicators": [
                "Pre-debit notification SMS/Email delivered 24-48h prior to recurring charge as per RBI / Card network rules"
            ],
            "weak_evidence_indicators": [
                "Pre-debit notification failed to deliver or was omitted"
            ]
        }
    ],
    "abstention_triggers": [
        "Customer submitted valid cancellation request via portal or email prior to billing cycle cutoff",
        "Mandate was revoked by customer at bank prior to debit date",
        "Pre-debit notification mandated by regulations was not sent"
    ],
    "win_probability_thresholds": {"high": 0.80, "medium": 0.50}
}
