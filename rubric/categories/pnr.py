"""Product or Service Not Received Category."""

CATEGORY = {
    "category_id": "product_service_not_received",
    "title": "Product or Service Not Received",
    "description": "Cardholder claims they purchased goods or services but did not receive them.",
    "reason_codes": ["13.1", "4855", "UPI-02", "RP-4002", "C08", "RZP_NR_02"],
    "required_evidence": [
        {
            "item_id": "proof_of_delivery",
            "name": "Proof of Delivery / Courier Tracking",
            "weight": 35.0,
            "compelling_level": "critical",
            "required_fields": ["carrier_name", "tracking_number", "delivery_timestamp", "delivery_address", "recipient_signature_or_gps"],
            "strong_evidence_indicators": [
                "Courier tracking status confirmed 'Delivered' to exact shipping address",
                "Recipient signature or GPS coordinates match customer location",
                "Delivery completed prior to dispute filing date"
            ],
            "weak_evidence_indicators": [
                "Tracking status 'In Transit', 'Pending', or 'Out for Delivery'",
                "Delivery address differs from customer checkout shipping address",
                "Package returned to merchant (RTO)"
            ]
        },
        {
            "item_id": "fulfillment_dispatch_proof",
            "name": "Invoice & Shipping Dispatch Proof",
            "weight": 25.0,
            "compelling_level": "important",
            "required_fields": ["invoice_number", "dispatch_date", "item_manifest", "shipping_label_id"],
            "strong_evidence_indicators": [
                "Detailed tax invoice with itemized line items matching transaction amount",
                "Dispatch manifest verified by logistics partner"
            ],
            "weak_evidence_indicators": [
                "Incomplete order invoice or mismatched line item values"
            ]
        },
        {
            "item_id": "delivery_communication",
            "name": "Shipping & Tracking Notification Log",
            "weight": 20.0,
            "compelling_level": "important",
            "required_fields": ["notification_type", "sent_timestamp", "recipient_email_or_phone", "tracking_url"],
            "strong_evidence_indicators": [
                "Automated email/SMS with tracking link sent to customer upon dispatch",
                "Customer opened tracking notification email"
            ],
            "weak_evidence_indicators": [
                "No dispatch notification sent to customer"
            ]
        },
        {
            "item_id": "customer_usage_activity",
            "name": "Digital Access / Service Usage Log (Digital Goods)",
            "weight": 35.0,
            "compelling_level": "critical",
            "required_fields": ["account_id", "login_timestamps", "bytes_downloaded_or_feature_accessed", "ip_address"],
            "strong_evidence_indicators": [
                "Logins recorded after transaction date with active digital service usage",
                "Software license key activated or content downloaded successfully"
            ],
            "weak_evidence_indicators": [
                "Zero login activity or failed activation logs"
            ]
        },
        {
            "item_id": "service_fulfillment_confirmation",
            "name": "Service Completion / Acceptance Form",
            "weight": 20.0,
            "compelling_level": "supporting",
            "required_fields": ["completion_date", "service_description", "customer_signoff"],
            "strong_evidence_indicators": [
                "Signed work completion order or digital sign-off by customer"
            ],
            "weak_evidence_indicators": [
                "Unsigned or verbal service confirmation without documentation"
            ]
        }
    ],
    "abstention_triggers": [
        "Courier tracking confirms package returned to sender (RTO) or undelivered",
        "Expected delivery date passed without dispatch or tracking details",
        "Digital access was blocked or credentials failed to provision"
    ],
    "win_probability_thresholds": {"high": 0.80, "medium": 0.50}
}
