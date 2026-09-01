"""Duplicate Processing or Incorrect Amount Category."""

CATEGORY = {
    "category_id": "duplicate_incorrect_amount",
    "title": "Duplicate Processing or Incorrect Amount",
    "description": "Cardholder claims they were charged multiple times for a single order or charged an amount different from checkout.",
    "reason_codes": ["12.6", "4834", "UPI-03", "RP-4005", "C05", "RZP_DUP_04"],
    "required_evidence": [
        {
            "item_id": "separate_transaction_proof",
            "name": "Separate Order & Invoice Proof",
            "weight": 40.0,
            "compelling_level": "critical",
            "required_fields": ["order_id_1", "order_id_2", "invoice_1_id", "invoice_2_id", "fulfillment_1_details", "fulfillment_2_details"],
            "strong_evidence_indicators": [
                "Two distinct orders placed with separate itemizations, shipping addresses, or timestamps",
                "Both orders individually fulfilled and delivered with distinct tracking numbers"
            ],
            "weak_evidence_indicators": [
                "Identical cart items submitted within 60 seconds (likely payment retry duplicate)"
            ]
        },
        {
            "item_id": "price_breakdown_and_authorization",
            "name": "Itemized Checkout Price Breakdown",
            "weight": 40.0,
            "compelling_level": "critical",
            "required_fields": ["item_subtotal", "tax_amount", "shipping_fee", "discounts", "total_authorized_amount"],
            "strong_evidence_indicators": [
                "Authorized charge matches exact total of subtotal + taxes + shipping signed off by user at checkout",
                "Dynamic currency conversion or FX terms clearly disclosed and accepted"
            ],
            "weak_evidence_indicators": [
                "Charged total exceeds displayed checkout total due to undisclosed merchant fees"
            ]
        },
        {
            "item_id": "billing_statement_and_receipt",
            "name": "Merchant Receipt & Payment Logs",
            "weight": 20.0,
            "compelling_level": "supporting",
            "required_fields": ["receipt_id", "gateway_payment_id_1", "gateway_payment_id_2"],
            "strong_evidence_indicators": [
                "Customer received separate confirmation emails for each distinct transaction"
            ],
            "weak_evidence_indicators": [
                "Single receipt sent for two gateway charges"
            ]
        }
    ],
    "abstention_triggers": [
        "System logs reveal payment gateway retried transaction automatically resulting in double debit for single order",
        "Merchant backend shows single order fulfilled but two payments captured"
    ],
    "win_probability_thresholds": {"high": 0.85, "medium": 0.50}
}
