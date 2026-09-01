"""Specialized case generators for PNR, Defective, Refund, Duplicate, and Subscription disputes."""

from __future__ import annotations
import random
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
    pick_merchant,
    pick_city,
    generate_auth_3ds,
)


def generate_pnr_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    city, state, pin, gps = pick_city()
    amount = round(random.uniform(400.0, 18000.0), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["13.1", "4855", "UPI-02", "RP-4002", "C08", "RZP_NR_02"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])
    carrier = random.choice(CARRIERS)

    if verdict == "win":
        delivery = DeliveryTrackingData(
            carrier_name=carrier,
            tracking_number=f"TRK{random.randint(10000000, 99999999)}",
            status="delivered",
            dispatch_date="2026-08-10",
            delivery_timestamp="2026-08-14T16:45:00Z",
            shipping_address=f"Flat {random.randint(101, 909)}, Palm Grove, {city}, {state} - {pin}",
            delivered_to_address=f"Flat {random.randint(101, 909)}, Palm Grove, {city}, {state} - {pin}",
            recipient_signature="Rahul S / Security Gate Verified",
            recipient_gps=gps,
            weight_kg=1.45,
        )
        invoice = InvoiceDispatchData(
            invoice_number=f"INV-2026-{random.randint(10000, 99999)}",
            invoice_date="2026-08-10",
            line_items=[{"item": "Wireless Noise Cancelling Earbuds", "qty": 1, "price": amount}],
            item_manifest_verified=True,
            shipping_label_id=f"LBL-{random.randint(100000, 999999)}",
            total_amount=amount,
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-10T11:00:00Z",
                sender="system",
                message=f"Your package has been dispatched via {carrier} with tracking URL https://track.example.com",
                resolution_offered="Tracking link delivered via SMS and email.",
            )
        ]
        service_use = ServiceUsageData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            active_login_count=5,
            last_login_timestamp="2026-08-18T12:00:00Z",
            license_key_activated=True,
        )
        reasoning = "Carrier tracking confirms physical delivery with recipient GPS match prior to dispute date."
        notes = "Courier confirmed delivery signed by recipient at registered address."

    elif verdict == "lose":
        delivery = DeliveryTrackingData(
            carrier_name=carrier,
            tracking_number=f"TRK{random.randint(10000000, 99999999)}",
            status="rto",
            dispatch_date="2026-08-10",
            delivery_timestamp=None,
            shipping_address=f"House {random.randint(10, 90)}, {city}, {state} - {pin}",
            delivered_to_address=None,
            rto_reason="Consignee not reachable / Returned to Origin",
        )
        invoice = InvoiceDispatchData(
            invoice_number=f"INV-2026-{random.randint(10000, 99999)}",
            invoice_date="2026-08-10",
            line_items=[{"item": "Apparel Order", "qty": 1, "price": amount}],
            item_manifest_verified=False,
            total_amount=amount,
        )
        comm = []
        service_use = None
        reasoning = "Carrier tracking confirms package was returned to origin (RTO); customer never received goods."
        notes = "Package undelivered and returned to warehouse. Refund was not yet initiated."

    else:  # ambiguous
        delivery = DeliveryTrackingData(
            carrier_name=carrier,
            tracking_number=f"TRK{random.randint(10000000, 99999999)}",
            status="in_transit",
            dispatch_date="2026-08-16",
            delivery_timestamp=None,
            shipping_address=f"Sector {random.randint(1, 50)}, {city}, {state} - {pin}",
            delivered_to_address=None,
        )
        invoice = InvoiceDispatchData(
            invoice_number=f"INV-2026-{random.randint(10000, 99999)}",
            invoice_date="2026-08-16",
            line_items=[{"item": "Home Decor Set", "qty": 1, "price": amount}],
            item_manifest_verified=True,
            total_amount=amount,
        )
        comm = []
        service_use = None
        reasoning = "Package still in transit past estimated delivery date; neither delivered nor returned."
        notes = "Courier delayed due to regional transit strikes."

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
        dispute_category="product_service_not_received",
        reason_code=reason_code,
        reason_description="Cardholder claims goods or services were not received",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        delivery_tracking=delivery,
        invoice_dispatch=invoice,
        customer_communication=comm,
        service_usage=service_use,
        merchant_notes=notes,
    )



def generate_defective_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    city, state, pin, gps = pick_city()
    amount = round(random.uniform(800.0, 32000.0), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["13.3", "4853", "UPI-04", "RP-4003", "C02", "RZP_DEF_05"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])

    if verdict == "win":
        price = PriceBreakdownData(
            subtotal=amount,
            tax=0.0,
            shipping=0.0,
            total_authorized=amount,
            item_specifications_url="https://merchant.in/products/item-specs-certified",
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-16T14:00:00Z",
                sender="merchant",
                message="We provided a pre-paid return shipping label #RET-8812 for inspection or replacement.",
                resolution_offered="Pre-paid return shipping label and replacement within 48 hours.",
                customer_response="Customer refused return process and demanded instant chargeback.",
                return_label_sent=True,
            )
        ]
        reasoning = "Merchant provided detailed spec match and offered return/replacement label which customer refused."
        notes = "Return authorization provided; customer kept product and refused return shipment."

    elif verdict == "lose":
        price = PriceBreakdownData(
            subtotal=amount,
            tax=0.0,
            shipping=0.0,
            total_authorized=amount,
            item_specifications_url=None,
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-16T14:00:00Z",
                sender="support_agent",
                message="Acknowledged that a defective unit from batch #B-902 was dispatched in error.",
                resolution_offered="None offered prior to dispute.",
                customer_response="Dispute raised following no response.",
            )
        ]
        reasoning = "Support ticket shows merchant acknowledged manufacturing defect but did not provide replacement."
        notes = "Merchant internal fault acknowledged: batch quality check failed."

    else:  # ambiguous
        price = PriceBreakdownData(
            subtotal=amount,
            tax=0.0,
            shipping=0.0,
            total_authorized=amount,
            item_specifications_url="https://merchant.in/general-info",
        )
        comm = []
        reasoning = "Subjective quality dispute with generic product description and no clear support resolution logs."
        notes = "Customer claims fabric quality is different from photos."

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
        dispute_category="product_unacceptable_defective",
        reason_code=reason_code,
        reason_description="Cardholder claims product was defective, damaged, or not as described",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        price_breakdown=price,
        customer_communication=comm,
        merchant_notes=notes,
    )


def generate_refund_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    amount = round(random.uniform(500.0, 25000.0), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["13.6", "4860", "UPI-05", "RP-4004", "C04", "RZP_REF_06"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])

    if verdict == "win":
        refund = RefundLogData(
            refund_id=f"rfnd_{random.randint(1000000, 9999999)}",
            arn_rrn=f"ARN{random.randint(100000000000, 999999999999)}",
            amount=amount,
            status="processed",
            refund_timestamp="2026-08-14T10:30:00Z",
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-14T10:35:00Z",
                sender="system",
                message="Refund of INR {amount} has been successfully processed to your bank account under ARN reference.",
                resolution_offered="Bank ARN reference provided.",
            )
        ]
        reasoning = "Valid Acquirer Reference Number (ARN) confirms refund was settled back to cardholder prior to dispute."
        notes = "Refund completed to original payment method before chargeback was received."

    elif verdict == "lose":
        refund = RefundLogData(
            refund_id=f"rfnd_{random.randint(1000000, 9999999)}",
            arn_rrn=None,
            amount=amount,
            status="failed",
            refund_timestamp="2026-08-15T09:00:00Z",
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-12T11:00:00Z",
                sender="support",
                message="We will process your full refund within 3 business days.",
                resolution_offered="Full refund promised.",
            )
        ]
        reasoning = "Merchant promised refund in support chat, but gateway refund transaction failed with no ARN generated."
        notes = "Refund promised to customer but failed at payment processor without retry."

    else:  # ambiguous
        refund = RefundLogData(
            refund_id=None,
            arn_rrn=None,
            amount=amount,
            status="none",
            store_credit_code="VOUCHER_CR_9012",
            store_credit_redeemed=False,
        )
        comm = [
            CustomerCommunicationLog(
                ticket_id=f"TICK-{random.randint(1000, 9999)}",
                timestamp="2026-08-14T15:00:00Z",
                sender="merchant",
                message="Store credit voucher sent to registered email.",
                resolution_offered="Store credit in lieu of cash refund.",
                customer_response="Unconfirmed by customer.",
            )
        ]
        reasoning = "Store credit issued without explicit customer consent; dispute raised for card refund."
        notes = "Customer accepted store credit policy during checkout but disputed after requesting cash."

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
        dispute_category="credit_refund_not_processed",
        reason_code=reason_code,
        reason_description="Cardholder claims promised refund or credit was not processed",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        refund_logs=refund,
        customer_communication=comm,
        merchant_notes=notes,
    )


def generate_duplicate_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    amount = round(random.uniform(300.0, 15000.0), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["12.6", "4834", "UPI-03", "RP-4005", "C05", "RZP_DUP_04"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])

    if verdict == "win":
        price = PriceBreakdownData(
            subtotal=amount - 100.0,
            tax=50.0,
            shipping=50.0,
            discount=0.0,
            total_authorized=amount,
        )
        reasoning = "Two distinct orders placed with separate invoice numbers and verified deliveries; charge matches authorized total."
        notes = "Separate orders with distinct fulfillment logs."

    elif verdict == "lose":
        price = PriceBreakdownData(
            subtotal=amount - 300.0,
            tax=0.0,
            shipping=0.0,
            discount=0.0,
            total_authorized=amount - 300.0,
        )
        reasoning = "Charged total exceeds checkout authorization by INR 300 due to unnotified merchant surcharge."
        notes = "Discrepancy in authorized checkout vs captured total."

    else:  # ambiguous
        price = PriceBreakdownData(
            subtotal=amount,
            tax=0.0,
            shipping=0.0,
            discount=0.0,
            total_authorized=amount,
        )
        reasoning = "Single order submitted with retry charge within 45 seconds; one fulfillment recorded."
        notes = "Customer claims duplicate charge from network timeout retry."

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
        dispute_category="duplicate_incorrect_amount",
        reason_code=reason_code,
        reason_description="Cardholder claims duplicate processing or incorrect charged amount",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        price_breakdown=price,
        merchant_notes=notes,
    )



def generate_subscription_case(idx: int, verdict: str) -> DisputeCase:
    merch_id, merch_name, merch_cat = pick_merchant()
    amount = round(random.choice([499.0, 999.0, 1499.0, 2999.0, 4999.0]), 2)
    case_id = f"disp_{idx:03d}"
    reason_code = random.choice(["13.7", "4841", "UPI-06", "RP-4006", "C06", "RZP_SUB_03"])
    pay_method = "upi" if "UPI" in reason_code else "card"
    network = "UPI" if pay_method == "upi" else random.choice(["Visa", "Mastercard", "RuPay"])

    if verdict == "win":
        sub = SubscriptionMandateData(
            subscription_id=f"sub_{random.randint(100000, 999999)}",
            mandate_id=f"mand_{random.randint(1000000, 9999999)}",
            billing_cycle="monthly",
            recurrence_amount=amount,
            signup_timestamp="2026-06-15T00:00:00Z",
            pre_debit_notification_sent=True,
            pre_debit_timestamp="2026-08-13T10:00:00Z",
            cancellation_request_timestamp=None,
        )
        service = ServiceUsageData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            active_login_count=12,
            last_login_timestamp="2026-08-22T19:00:00Z",
            features_used=["api_access", "dashboard_analytics", "export_reports"],
        )
        reasoning = "Active recurring mandate with compliant pre-debit notice sent; active logins during disputed billing cycle."
        notes = "Customer utilized premium tier during disputed month with no cancellation on file."

    elif verdict == "lose":
        sub = SubscriptionMandateData(
            subscription_id=f"sub_{random.randint(100000, 999999)}",
            mandate_id=f"mand_{random.randint(1000000, 9999999)}",
            billing_cycle="monthly",
            recurrence_amount=amount,
            signup_timestamp="2026-06-15T00:00:00Z",
            pre_debit_notification_sent=False,
            cancellation_request_timestamp="2026-08-10T14:00:00Z",
        )
        service = ServiceUsageData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            active_login_count=0,
            last_login_timestamp="2026-08-01T10:00:00Z",
            features_used=[],
        )
        reasoning = "Customer cancelled subscription 5 days before renewal date, but system erroneously billed cardholder."
        notes = "Cancellation was recorded in customer dashboard prior to billing run."

    else:  # ambiguous
        sub = SubscriptionMandateData(
            subscription_id=f"sub_{random.randint(100000, 999999)}",
            mandate_id=f"mand_{random.randint(1000000, 9999999)}",
            billing_cycle="annual",
            recurrence_amount=amount * 10,
            signup_timestamp="2025-08-15T00:00:00Z",
            pre_debit_notification_sent=True,
            cancellation_request_timestamp="2026-08-16T02:00:00Z",
        )
        service = ServiceUsageData(
            account_id=f"cust_{random.randint(1000, 9999)}",
            active_login_count=1,
            last_login_timestamp="2026-08-16T03:00:00Z",
        )
        reasoning = "Annual subscription renewal notification sent; cancellation requested 1 day after renewal charge."
        notes = "Auto-renew policy states 48h notice before charge; user requested refund 2 hours post-charge."

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
        dispute_category="subscription_recurring_cancellation",
        reason_code=reason_code,
        reason_description="Cardholder claims subscription was cancelled prior to recurring charge",
        filed_date="2026-08-20",
        due_date="2026-09-05",
        ground_truth=verdict,
        ground_truth_reasoning=reasoning,
        subscription_mandate=sub,
        service_usage=service,
        merchant_notes=notes,
    )
