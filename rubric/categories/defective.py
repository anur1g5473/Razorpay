"""Product Unacceptable, Defective, or Not as Described Category."""

CATEGORY = {
    "category_id": "product_unacceptable_defective",
    "title": "Product Unacceptable, Defective, or Not as Described",
    "description": "Cardholder claims the received product or service was defective, damaged, or significantly different from description.",
    "reason_codes": ["13.3", "4853", "UPI-04", "RP-4003", "C02", "RZP_DEF_05"],
    "required_evidence": [
        {
            "item_id": "item_specification_description",
            "name": "Published Product Description & Specification",
            "weight": 25.0,
            "compelling_level": "important",
            "required_fields": ["product_url", "spec_details", "order_confirmation_snapshot"],
            "strong_evidence_indicators": [
                "Detailed product description and specs matching delivered item exactly",
                "Clear disclaimer regarding color variations, size charts, or digital compatibility"
            ],
            "weak_evidence_indicators": [
                "Vague product specs or missing product photos at time of sale"
            ]
        },
        {
            "item_id": "quality_assurance_log",
            "name": "Pre-Shipment QA Inspection Log",
            "weight": 25.0,
            "compelling_level": "important",
            "required_fields": ["qa_cert_id", "inspection_timestamp", "inspector_id", "serial_number"],
            "strong_evidence_indicators": [
                "QA inspection certificate confirming item was functional and undamaged prior to packing",
                "Serial number recorded and checked against factory database"
            ],
            "weak_evidence_indicators": [
                "No pre-dispatch inspection records available"
            ]
        },
        {
            "item_id": "merchant_customer_correspondence",
            "name": "Support Ticket & Replacement Correspondence",
            "weight": 30.0,
            "compelling_level": "critical",
            "required_fields": ["ticket_id", "resolution_offered", "customer_response", "return_instructions_sent"],
            "strong_evidence_indicators": [
                "Merchant offered free return label or replacement which customer refused or ignored",
                "Customer failed to return defective item despite return authorization"
            ],
            "weak_evidence_indicators": [
                "Merchant ignored customer complaint ticket or refused valid replacement"
            ]
        },
        {
            "item_id": "return_policy_and_terms",
            "name": "Published Return & Replacement Policy",
            "weight": 20.0,
            "compelling_level": "supporting",
            "required_fields": ["policy_url", "return_window_days", "terms_acceptance_proof"],
            "strong_evidence_indicators": [
                "Dispute filed outside contractually agreed return window (e.g. > 14 days post-delivery)",
                "Return policy clearly accepted at checkout"
            ],
            "weak_evidence_indicators": [
                "Unclear return policy or missing policy link at checkout"
            ]
        }
    ],
    "abstention_triggers": [
        "Customer returned item with valid tracking proof but merchant did not process replacement or refund",
        "Merchant acknowledged manufacturing defect in customer support ticket",
        "Item damaged during transit due to improper merchant packaging"
    ],
    "win_probability_thresholds": {"high": 0.75, "medium": 0.45}
}
