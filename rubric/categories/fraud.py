"""Fraudulent / Unauthorized Transaction Category."""

CATEGORY = {
    "category_id": "fraudulent_unauthorized",
    "title": "Fraudulent / Unauthorized Transaction",
    "description": "Cardholder claims they did not participate in or authorize the transaction.",
    "reason_codes": ["10.4", "4837", "UPI-01", "RP-4001", "F29", "RZP_FRAUD_01"],
    "required_evidence": [
        {
            "item_id": "3ds_authentication_log",
            "name": "3D Secure / OTP / UPI PIN Authentication Log",
            "weight": 35.0,
            "compelling_level": "critical",
            "required_fields": ["auth_type", "cavv_eci", "auth_timestamp", "status", "transaction_reference"],
            "strong_evidence_indicators": [
                "Fully authenticated 3DS v2.x transaction with ECI 05 or 02",
                "UPI PIN successfully verified by issuing bank",
                "OTP verified on customer registered mobile number"
            ],
            "weak_evidence_indicators": [
                "3DS attempted but downgraded or bypassed",
                "Missing ECI or CAVV authentication value",
                "Authorization without secondary factor authentication"
            ]
        },
        {
            "item_id": "ip_and_device_fingerprint",
            "name": "IP Address & Device Fingerprint Log",
            "weight": 20.0,
            "compelling_level": "important",
            "required_fields": ["ip_address", "device_id", "geo_location", "user_agent", "session_id"],
            "strong_evidence_indicators": [
                "IP geolocation matches customer billing address city/country",
                "Device ID matches prior undisputed account logins",
                "No proxy or VPN detected during transaction"
            ],
            "weak_evidence_indicators": [
                "IP address located in different country from billing address",
                "Anonymous proxy or VPN detected at checkout"
            ]
        },
        {
            "item_id": "customer_communication",
            "name": "Customer Communication & Support History",
            "weight": 20.0,
            "compelling_level": "important",
            "required_fields": ["ticket_id", "correspondence_timestamps", "customer_email", "summary"],
            "strong_evidence_indicators": [
                "Customer acknowledged purchase or communicated about item delivery",
                "Email thread shows customer requested order modification or password reset"
            ],
            "weak_evidence_indicators": [
                "No recorded communication or unresolved customer complaint email"
            ]
        },
        {
            "item_id": "order_fulfillment_history",
            "name": "Customer Account Order History",
            "weight": 15.0,
            "compelling_level": "supporting",
            "required_fields": ["account_created_date", "prior_order_count", "prior_undisputed_amount", "matching_email_or_phone"],
            "strong_evidence_indicators": [
                "Established account with 3+ prior undisputed transactions using same card/account",
                "Account age > 90 days with consistent login history"
            ],
            "weak_evidence_indicators": [
                "First-time buyer with guest checkout and disposable email"
            ]
        },
        {
            "item_id": "terms_acceptance",
            "name": "Terms of Service & Refund Policy Acceptance",
            "weight": 10.0,
            "compelling_level": "supporting",
            "required_fields": ["terms_version", "acceptance_timestamp", "ip_at_acceptance"],
            "strong_evidence_indicators": [
                "Timestamped click-through acceptance of Terms of Service prior to payment"
            ],
            "weak_evidence_indicators": [
                "Pre-checked box or unrecorded acceptance timestamp"
            ]
        }
    ],
    "abstention_triggers": [
        "Transaction lacks 3DS / OTP / UPI PIN authentication log and transaction amount exceeds Rs 10,000",
        "Merchant acknowledged fraudulent activity in internal notes",
        "Known stolen card reported by card network prior to dispatch"
    ],
    "win_probability_thresholds": {"high": 0.75, "medium": 0.45}
}
