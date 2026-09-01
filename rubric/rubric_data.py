"""Complete definitions of DisputeShield Evidence Rubric categories."""

from __future__ import annotations
import json
from pathlib import Path
from rubric.models import (
    EvidenceItem,
    WinProbabilityThresholds,
    DisputeCategoryRubric,
    EvidenceRubric,
)

FRAUD_CATEGORY = DisputeCategoryRubric(
    category_id="fraudulent_unauthorized",
    title="Fraudulent / Unauthorized Transaction",
    description="Cardholder claims they did not participate in or authorize the transaction.",
    reason_codes=["10.4", "4837", "UPI-01", "RP-4001", "F29", "RZP_FRAUD_01"],
    required_evidence=[
        EvidenceItem(
            item_id="3ds_authentication_log",
            name="3D Secure / OTP / UPI PIN Authentication Log",
            weight=35.0,
            compelling_level="critical",
            required_fields=["auth_type", "cavv_eci", "auth_timestamp", "status", "transaction_reference"],
            strong_evidence_indicators=[
                "Fully authenticated 3DS v2.x transaction with ECI 05 or 02",
                "UPI PIN successfully verified by issuing bank",
                "OTP verified on customer registered mobile number",
            ],
            weak_evidence_indicators=[
                "3DS attempted but downgraded or bypassed",
                "Missing ECI or CAVV authentication value",
                "Authorization without secondary factor authentication",
            ],
        ),
        EvidenceItem(
            item_id="ip_and_device_fingerprint",
            name="IP Address & Device Fingerprint Log",
            weight=20.0,
            compelling_level="important",
            required_fields=["ip_address", "device_id", "geo_location", "user_agent", "session_id"],
            strong_evidence_indicators=[
                "IP geolocation matches customer billing address city/country",
                "Device ID matches prior undisputed account logins",
                "No proxy or VPN detected during transaction",
            ],
            weak_evidence_indicators=[
                "IP address located in different country from billing address",
                "Anonymous proxy or VPN detected at checkout",
            ],
        ),
        EvidenceItem(
            item_id="customer_communication",
            name="Customer Communication & Support History",
            weight=20.0,
            compelling_level="important",
            required_fields=["ticket_id", "correspondence_timestamps", "customer_email", "summary"],
            strong_evidence_indicators=[
                "Customer acknowledged purchase or communicated about item delivery",
                "Email thread shows customer requested order modification or password reset",
            ],
            weak_evidence_indicators=[
                "No recorded communication or unresolved customer complaint email",
            ],
        ),
        EvidenceItem(
            item_id="order_fulfillment_history",
            name="Customer Account Order History",
            weight=15.0,
            compelling_level="supporting",
            required_fields=["account_created_date", "prior_order_count", "prior_undisputed_amount", "matching_email_or_phone"],
            strong_evidence_indicators=[
                "Established account with 3+ prior undisputed transactions using same card/account",
                "Account age > 90 days with consistent login history",
            ],
            weak_evidence_indicators=[
                "First-time buyer with guest checkout and disposable email",
            ],
        ),
        EvidenceItem(
            item_id="terms_acceptance",
            name="Terms of Service & Refund Policy Acceptance",
            weight=10.0,
            compelling_level="supporting",
            required_fields=["terms_version", "acceptance_timestamp", "ip_at_acceptance"],
            strong_evidence_indicators=[
                "Timestamped click-through acceptance of Terms of Service prior to payment",
            ],
            weak_evidence_indicators=[
                "Pre-checked box or unrecorded acceptance timestamp",
            ],
        ),
    ],
    abstention_triggers=[
        "Transaction lacks 3DS / OTP / UPI PIN authentication log and transaction amount exceeds Rs 10,000",
        "Merchant acknowledged fraudulent activity in internal notes",
        "Known stolen card reported by card network prior to dispatch",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.75, medium=0.45),
)

PNR_CATEGORY = DisputeCategoryRubric(
    category_id="product_service_not_received",
    title="Product or Service Not Received",
    description="Cardholder claims they purchased goods or services but did not receive them.",
    reason_codes=["13.1", "4855", "UPI-02", "RP-4002", "C08", "RZP_NR_02"],
    required_evidence=[
        EvidenceItem(
            item_id="proof_of_delivery",
            name="Proof of Delivery / Courier Tracking",
            weight=40.0,
            compelling_level="critical",
            required_fields=["carrier_name", "tracking_number", "delivery_timestamp", "delivery_address", "recipient_signature_or_gps"],
            strong_evidence_indicators=[
                "Courier tracking status confirmed 'Delivered' to exact shipping address",
                "Recipient signature or GPS coordinates match customer location",
                "Delivery completed prior to dispute filing date",
            ],
            weak_evidence_indicators=[
                "Tracking status 'In Transit', 'Pending', or 'Out for Delivery'",
                "Delivery address differs from customer checkout shipping address",
                "Package returned to merchant (RTO)",
            ],
        ),
        EvidenceItem(
            item_id="fulfillment_dispatch_proof",
            name="Invoice & Shipping Dispatch Proof",
            weight=25.0,
            compelling_level="important",
            required_fields=["invoice_number", "dispatch_date", "item_manifest", "shipping_label_id"],
            strong_evidence_indicators=[
                "Detailed tax invoice with itemized line items matching transaction amount",
                "Dispatch manifest verified by logistics partner",
            ],
            weak_evidence_indicators=[
                "Incomplete order invoice or mismatched line item values",
            ],
        ),
        EvidenceItem(
            item_id="delivery_communication",
            name="Shipping & Tracking Notification Log",
            weight=15.0,
            compelling_level="important",
            required_fields=["notification_type", "sent_timestamp", "recipient_email_or_phone", "tracking_url"],
            strong_evidence_indicators=[
                "Automated email/SMS with tracking link sent to customer upon dispatch",
                "Customer opened tracking notification email",
            ],
            weak_evidence_indicators=[
                "No dispatch notification sent to customer",
            ],
        ),
        EvidenceItem(
            item_id="customer_usage_activity",
            name="Digital Access / Service Usage Log (Digital Goods)",
            weight=10.0,
            compelling_level="supporting",
            required_fields=["account_id", "login_timestamps", "bytes_downloaded_or_feature_accessed", "ip_address"],
            strong_evidence_indicators=[
                "Logins recorded after transaction date with active digital service usage",
                "Software license key activated or content downloaded successfully",
            ],
            weak_evidence_indicators=[
                "Zero login activity or failed activation logs",
            ],
        ),
        EvidenceItem(
            item_id="service_fulfillment_confirmation",
            name="Service Completion / Acceptance Form",
            weight=10.0,
            compelling_level="supporting",
            required_fields=["completion_date", "service_description", "customer_signoff"],
            strong_evidence_indicators=[
                "Signed work completion order or digital sign-off by customer",
            ],
            weak_evidence_indicators=[
                "Unsigned or verbal service confirmation without documentation",
            ],
        ),
    ],
    abstention_triggers=[
        "Courier tracking confirms package returned to sender (RTO) or undelivered",
        "Expected delivery date passed without dispatch or tracking details",
        "Digital access was blocked or credentials failed to provision",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.80, medium=0.50),
)

DEFECTIVE_CATEGORY = DisputeCategoryRubric(
    category_id="product_unacceptable_defective",
    title="Product Unacceptable, Defective, or Not as Described",
    description="Cardholder claims the received product or service was defective, damaged, or significantly different from description.",
    reason_codes=["13.3", "4853", "UPI-04", "RP-4003", "C02", "RZP_DEF_05"],
    required_evidence=[
        EvidenceItem(
            item_id="item_specification_description",
            name="Published Product Description & Specification",
            weight=25.0,
            compelling_level="important",
            required_fields=["product_url", "spec_details", "order_confirmation_snapshot"],
            strong_evidence_indicators=[
                "Detailed product description and specs matching delivered item exactly",
                "Clear disclaimer regarding color variations, size charts, or digital compatibility",
            ],
            weak_evidence_indicators=[
                "Vague product specs or missing product photos at time of sale",
            ],
        ),
        EvidenceItem(
            item_id="quality_assurance_log",
            name="Pre-Shipment QA Inspection Log",
            weight=25.0,
            compelling_level="important",
            required_fields=["qa_cert_id", "inspection_timestamp", "inspector_id", "serial_number"],
            strong_evidence_indicators=[
                "QA inspection certificate confirming item was functional and undamaged prior to packing",
                "Serial number recorded and checked against factory database",
            ],
            weak_evidence_indicators=[
                "No pre-dispatch inspection records available",
            ],
        ),
        EvidenceItem(
            item_id="merchant_customer_correspondence",
            name="Support Ticket & Replacement Correspondence",
            weight=30.0,
            compelling_level="critical",
            required_fields=["ticket_id", "resolution_offered", "customer_response", "return_instructions_sent"],
            strong_evidence_indicators=[
                "Merchant offered free return label or replacement which customer refused or ignored",
                "Customer failed to return defective item despite return authorization",
            ],
            weak_evidence_indicators=[
                "Merchant ignored customer complaint ticket or refused valid replacement",
            ],
        ),
        EvidenceItem(
            item_id="return_policy_and_terms",
            name="Published Return & Replacement Policy",
            weight=20.0,
            compelling_level="supporting",
            required_fields=["policy_url", "return_window_days", "terms_acceptance_proof"],
            strong_evidence_indicators=[
                "Dispute filed outside contractually agreed return window (e.g. > 14 days post-delivery)",
                "Return policy clearly accepted at checkout",
            ],
            weak_evidence_indicators=[
                "Unclear return policy or missing policy link at checkout",
            ],
        ),
    ],
    abstention_triggers=[
        "Customer returned item with valid tracking proof but merchant did not process replacement or refund",
        "Merchant acknowledged manufacturing defect in customer support ticket",
        "Item damaged during transit due to improper merchant packaging",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.75, medium=0.45),
)


CREDIT_REFUND_CATEGORY = DisputeCategoryRubric(
    category_id="credit_refund_not_processed",
    title="Credit or Refund Not Processed",
    description="Cardholder claims they were promised a refund or credit that was never credited to their account.",
    reason_codes=["13.6", "4860", "UPI-05", "RP-4004", "C04", "RZP_REF_06"],
    required_evidence=[
        EvidenceItem(
            item_id="refund_proof_or_cancellation_policy",
            name="Refund Reference / ARN / Policy Proof",
            weight=40.0,
            compelling_level="critical",
            required_fields=["refund_id", "arn_rrn", "refund_amount", "refund_timestamp", "status"],
            strong_evidence_indicators=[
                "Valid Bank ARN / RRN showing refund was processed to original payment method prior to dispute",
                "Explicit non-refundable policy accepted by customer for custom/non-cancellable service",
            ],
            weak_evidence_indicators=[
                "Refund initiated internally but failed at gateway",
                "No ARN/RRN generated prior to dispute filing",
            ],
        ),
        EvidenceItem(
            item_id="cancellation_timestamp_log",
            name="Cancellation Cutoff & Timestamp Verification",
            weight=30.0,
            compelling_level="important",
            required_fields=["order_timestamp", "cancellation_request_timestamp", "policy_cutoff_hours"],
            strong_evidence_indicators=[
                "Cancellation requested after published deadline (e.g. < 24h before event or post-dispatch)",
                "No cancellation request submitted in merchant system",
            ],
            weak_evidence_indicators=[
                "Cancellation submitted within allowed policy window before cutoff",
            ],
        ),
        EvidenceItem(
            item_id="merchant_customer_communication",
            name="Store Credit Agreement / Ticket Communication",
            weight=30.0,
            compelling_level="important",
            required_fields=["ticket_id", "agreed_resolution", "store_credit_voucher_code"],
            strong_evidence_indicators=[
                "Customer explicitly agreed in email to accept store credit/voucher in lieu of cash refund",
                "Voucher issued and partially/fully redeemed by customer",
            ],
            weak_evidence_indicators=[
                "Store credit issued unilaterally without customer consent",
            ],
        ),
    ],
    abstention_triggers=[
        "Merchant promised cash refund in email thread but failed to execute refund transaction",
        "Refund processed to incorrect account or bounced payment method without customer notice",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.85, medium=0.50),
)

DUPLICATE_CATEGORY = DisputeCategoryRubric(
    category_id="duplicate_incorrect_amount",
    title="Duplicate Processing or Incorrect Amount",
    description="Cardholder claims they were charged multiple times for a single order or charged an amount different from checkout.",
    reason_codes=["12.6", "4834", "UPI-03", "RP-4005", "C05", "RZP_DUP_04"],
    required_evidence=[
        EvidenceItem(
            item_id="separate_transaction_proof",
            name="Separate Order & Invoice Proof",
            weight=40.0,
            compelling_level="critical",
            required_fields=["order_id_1", "order_id_2", "invoice_1_id", "invoice_2_id", "fulfillment_1_details", "fulfillment_2_details"],
            strong_evidence_indicators=[
                "Two distinct orders placed with separate itemizations, shipping addresses, or timestamps",
                "Both orders individually fulfilled and delivered with distinct tracking numbers",
            ],
            weak_evidence_indicators=[
                "Identical cart items submitted within 60 seconds (likely payment retry duplicate)",
            ],
        ),
        EvidenceItem(
            item_id="price_breakdown_and_authorization",
            name="Itemized Checkout Price Breakdown",
            weight=40.0,
            compelling_level="critical",
            required_fields=["item_subtotal", "tax_amount", "shipping_fee", "discounts", "total_authorized_amount"],
            strong_evidence_indicators=[
                "Authorized charge matches exact total of subtotal + taxes + shipping signed off by user at checkout",
                "Dynamic currency conversion or FX terms clearly disclosed and accepted",
            ],
            weak_evidence_indicators=[
                "Charged total exceeds displayed checkout total due to undisclosed merchant fees",
            ],
        ),
        EvidenceItem(
            item_id="billing_statement_and_receipt",
            name="Merchant Receipt & Payment Logs",
            weight=20.0,
            compelling_level="supporting",
            required_fields=["receipt_id", "gateway_payment_id_1", "gateway_payment_id_2"],
            strong_evidence_indicators=[
                "Customer received separate confirmation emails for each distinct transaction",
            ],
            weak_evidence_indicators=[
                "Single receipt sent for two gateway charges",
            ],
        ),
    ],
    abstention_triggers=[
        "System logs reveal payment gateway retried transaction automatically resulting in double debit for single order",
        "Merchant backend shows single order fulfilled but two payments captured",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.85, medium=0.50),
)

SUBSCRIPTION_CATEGORY = DisputeCategoryRubric(
    category_id="subscription_recurring_cancellation",
    title="Cancelled Subscription / Recurring Charge",
    description="Cardholder claims they cancelled recurring subscription prior to billing or were charged after cancellation.",
    reason_codes=["13.7", "4841", "UPI-06", "RP-4006", "C06", "RZP_SUB_03"],
    required_evidence=[
        EvidenceItem(
            item_id="subscription_contract_terms",
            name="Subscription Terms & Mandate Agreement",
            weight=35.0,
            compelling_level="critical",
            required_fields=["subscription_id", "mandate_id", "billing_cycle", "recurrence_amount", "terms_acceptance_timestamp"],
            strong_evidence_indicators=[
                "Active E-Mandate / SI registered with bank authentication",
                "Clear recurring billing terms with frequency, price, and auto-renew policy accepted at signup",
            ],
            weak_evidence_indicators=[
                "Missing recurring mandate registration proof",
            ],
        ),
        EvidenceItem(
            item_id="cancellation_policy_compliance",
            name="Cancellation Request & Log Audit",
            weight=35.0,
            compelling_level="critical",
            required_fields=["cancellation_timestamp", "cancellation_status", "effective_end_date", "billing_date"],
            strong_evidence_indicators=[
                "No cancellation request submitted prior to recurring billing date",
                "Cancellation request submitted AFTER renewal cutoff date specified in terms",
            ],
            weak_evidence_indicators=[
                "Cancellation requested before billing date but merchant failed to process cancellation in CRM",
            ],
        ),
        EvidenceItem(
            item_id="service_usage_during_period",
            name="Service Usage Activity During Disputed Period",
            weight=20.0,
            compelling_level="important",
            required_fields=["period_start_date", "period_end_date", "active_login_count", "features_used"],
            strong_evidence_indicators=[
                "Customer actively logged in and utilized subscription features during the disputed billing cycle",
            ],
            weak_evidence_indicators=[
                "Zero login or service usage recorded during disputed cycle",
            ],
        ),
        EvidenceItem(
            item_id="recurring_billing_notification",
            name="Pre-Debit Renewal Notification Log",
            weight=10.0,
            compelling_level="supporting",
            required_fields=["pre_debit_notification_id", "sent_timestamp", "channel"],
            strong_evidence_indicators=[
                "Pre-debit notification SMS/Email delivered 24-48h prior to recurring charge as per RBI / Card network rules",
            ],
            weak_evidence_indicators=[
                "Pre-debit notification failed to deliver or was omitted",
            ],
        ),
    ],
    abstention_triggers=[
        "Customer submitted valid cancellation request via portal or email prior to billing cycle cutoff",
        "Mandate was revoked by customer at bank prior to debit date",
        "Pre-debit notification mandated by regulations was not sent",
    ],
    win_probability_thresholds=WinProbabilityThresholds(high=0.80, medium=0.50),
)


def get_default_rubric() -> EvidenceRubric:
    return EvidenceRubric(
        version="1.0.0",
        last_updated="2026-09-01",
        description="DisputeShield Evidence Evaluation Rubric covering card networks (Visa, Mastercard, RuPay, Amex), UPI, and Razorpay dispute reason codes.",
        categories={
            "fraudulent_unauthorized": FRAUD_CATEGORY,
            "product_service_not_received": PNR_CATEGORY,
            "product_unacceptable_defective": DEFECTIVE_CATEGORY,
            "credit_refund_not_processed": CREDIT_REFUND_CATEGORY,
            "duplicate_incorrect_amount": DUPLICATE_CATEGORY,
            "subscription_recurring_cancellation": SUBSCRIPTION_CATEGORY,
        },
    )


RUBRIC = get_default_rubric()
ALL_CATEGORIES = RUBRIC.categories


def save_rubric_to_file(path: Path | str | None = None) -> Path:
    if path is None:
        path = Path(__file__).parent / "evidence_rubric.json"
    else:
        path = Path(path)
    rubric = get_default_rubric()
    with open(path, "w", encoding="utf-8") as f:
        f.write(rubric.model_dump_json(indent=2))
    return path


if __name__ == "__main__":
    saved = save_rubric_to_file()
    print(f"Generated rubric at {saved}")

