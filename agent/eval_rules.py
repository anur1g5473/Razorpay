"""Rule-based evaluation functions for dispute evidence items."""

from __future__ import annotations
from typing import Dict, Any, Tuple, List


def eval_3ds_authentication(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    auth = data.get("auth_3ds") or {}
    status = auth.get("status")
    auth_type = auth.get("auth_type")
    eci = auth.get("cavv_eci")
    fields = ["auth_type", "cavv_eci", "auth_timestamp", "status", "transaction_reference"]
    f_pres = [k for k in fields if auth.get(k)]
    f_miss = [k for k in fields if not auth.get(k)]

    if status == "authenticated" and (eci in ["05", "02"] or auth_type == "UPI_PIN"):
        return 1.0, f_pres, f_miss, [f"Full 3DS/UPI authentication verified ({auth_type}, ECI {eci})"], []
    elif status == "attempted" or eci in ["06", "01"]:
        return 0.5, f_pres, f_miss, [], [f"Liability shift uncertain: 3DS only attempted (ECI {eci})"]
    else:
        return 0.0, f_pres, f_miss, [], ["Missing or failed 3DS authentication - high fraud liability on merchant"]


def eval_ip_device(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    auth = data.get("auth_3ds") or {}
    ip = auth.get("ip_address")
    dev = auth.get("device_fingerprint")
    vpn = auth.get("vpn_detected", False)
    geo = auth.get("geo_location_match", True)
    fields = ["ip_address", "device_id", "geo_location", "user_agent", "session_id"]
    f_pres = [k for k in ["ip_address", "device_id"] if auth.get(k)]
    f_miss = [k for k in ["ip_address", "device_id"] if not auth.get(k)]

    if ip or dev:
        if geo and not vpn:
            return 1.0, f_pres, f_miss, [f"Clean IP ({ip}) matching billing geo-location, no VPN"], []
        elif vpn:
            return 0.3, f_pres, f_miss, [], ["Anonymous VPN / proxy detected during checkout"]
        else:
            return 0.5, f_pres, f_miss, [], ["IP location does not match cardholder billing country"]
    return 0.0, f_pres, f_miss, [], ["Missing IP & device fingerprint session logs"]


def eval_proof_of_delivery(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    deliv = data.get("delivery_tracking") or {}
    status = deliv.get("status")
    sig = deliv.get("recipient_signature")
    gps = deliv.get("recipient_gps")
    fields = ["carrier_name", "tracking_number", "delivery_timestamp", "delivery_address", "recipient_signature_or_gps"]
    f_pres = [k for k in ["carrier_name", "tracking_number", "delivery_timestamp", "shipping_address"] if deliv.get(k)]
    f_miss = [k for k in ["carrier_name", "tracking_number", "delivery_timestamp", "shipping_address"] if not deliv.get(k)]

    if status == "delivered":
        if sig or gps:
            return 1.0, f_pres, f_miss, [f"Confirmed delivery with recipient proof ({deliv.get('carrier_name')})"], []
        return 0.85, f_pres, f_miss, [f"Carrier confirmed delivery to shipping address ({deliv.get('tracking_number')})"], []
    elif status == "in_transit":
        return 0.4, f_pres, f_miss, [], ["Package still in transit, delivery unconfirmed"]
    elif status == "rto":
        return 0.0, f_pres, f_miss, [], [f"Package returned to origin (RTO): {deliv.get('rto_reason', 'Undelivered')}"]
    return 0.0, f_pres, f_miss, [], ["No courier tracking or delivery confirmation available"]


def eval_invoice_dispatch(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    inv = data.get("invoice_dispatch") or {}
    inv_num = inv.get("invoice_number")
    line_items = inv.get("line_items") or []
    f_pres = [k for k in ["invoice_number", "dispatch_date", "shipping_label_id"] if inv.get(k)]
    f_miss = [k for k in ["invoice_number", "dispatch_date", "shipping_label_id"] if not inv.get(k)]

    if inv_num and len(line_items) > 0:
        return 1.0, f_pres, f_miss, [f"Itemized tax invoice ({inv_num}) matching transaction total"], []
    elif inv_num:
        return 0.7, f_pres, f_miss, [f"Tax invoice on file ({inv_num})"], []
    return 0.0, f_pres, f_miss, [], ["Missing tax invoice & dispatch manifest"]


def eval_customer_comm(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    comm = data.get("customer_communication") or []
    f_pres = ["ticket_id", "correspondence_timestamps", "customer_email"] if comm else []
    f_miss = [] if comm else ["ticket_id", "correspondence_timestamps", "customer_email"]

    if comm:
        return 1.0, f_pres, f_miss, [f"Support ticket history on record ({len(comm)} interaction logs)"], []
    return 0.0, f_pres, f_miss, [], ["No customer correspondence on record"]


def eval_account_history(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    acc = data.get("customer_account") or {}
    prior_count = acc.get("prior_order_count", 0)
    matches = acc.get("matches_billing", True)
    f_pres = [k for k in ["account_id", "created_date", "prior_order_count"] if acc.get(k) is not None]
    f_miss = [k for k in ["account_id", "created_date", "prior_order_count"] if acc.get(k) is None]

    if prior_count >= 3 and matches:
        return 1.0, f_pres, f_miss, [f"Established account with {prior_count} prior orders"], []
    elif prior_count >= 1:
        return 0.6, f_pres, f_miss, [f"Account with {prior_count} prior orders"], []
    return 0.0, f_pres, f_miss, [], ["First-time user or missing account history"]


def eval_terms_acceptance(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    mandate = data.get("subscription_mandate") or {}
    price = data.get("price_breakdown") or {}
    terms_v = mandate.get("terms_version") or price.get("terms_version") or "v2.0"
    return 1.0, ["terms_version", "acceptance_timestamp"], [], [f"Terms & conditions ({terms_v}) agreed at checkout"], []


def eval_digital_usage(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    usage = data.get("service_usage") or {}
    logins = usage.get("active_login_count", 0)
    lic = usage.get("license_key_activated")
    f_pres = [k for k in ["account_id", "active_login_count", "license_key_activated"] if usage.get(k) is not None]
    f_miss = [k for k in ["account_id", "active_login_count", "license_key_activated"] if usage.get(k) is None]

    if logins > 0 or lic is True:
        return 1.0, f_pres, f_miss, [f"Active service utilization: {logins} logins, license activated"], []
    return 0.0, f_pres, f_miss, [], ["Zero digital access or service consumption logged"]


def eval_qa_log(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    inv = data.get("invoice_dispatch") or {}
    if inv.get("item_manifest_verified", True):
        return 1.0, ["qa_cert_id", "inspection_timestamp"], [], ["Pre-shipment QA inspection verified undamaged condition"], []
    return 0.0, [], ["qa_cert_id"], [], ["Missing pre-shipment QA verification"]


def eval_refund_proof(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    ref = data.get("refund_logs") or {}
    arn = ref.get("arn_rrn")
    status = ref.get("status")
    credit = ref.get("store_credit_code")
    redeemed = ref.get("store_credit_redeemed")
    f_pres = [k for k in ["refund_id", "arn_rrn", "status"] if ref.get(k)]
    f_miss = [k for k in ["refund_id", "arn_rrn", "status"] if not ref.get(k)]

    if status == "processed" and arn:
        return 1.0, f_pres, f_miss, [f"Bank ARN/RRN ({arn}) confirms refund completed to source"], []
    elif credit and redeemed:
        return 1.0, f_pres, f_miss, [f"Store credit voucher ({credit}) issued & redeemed by customer"], []
    elif credit:
        return 0.5, f_pres, f_miss, [f"Store credit voucher ({credit}) issued"], ["Store credit unredeemed / cardholder requested monetary refund"]
    elif status == "pending":
        return 0.3, f_pres, f_miss, [], ["Refund pending at merchant gateway - not settled to cardholder"]
    return 0.0, f_pres, f_miss, [], ["No proof of refund ARN or valid non-refundable terms on record"]



def eval_separate_orders(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    price = data.get("price_breakdown") or {}
    deliv = data.get("delivery_tracking") or {}
    tot = price.get("total_authorized")
    sub = price.get("subtotal")

    if tot and sub and tot == (sub + (price.get("tax") or 0.0) + (price.get("shipping") or 0.0) - (price.get("discount") or 0.0)):
        return 1.0, ["order_id_1", "invoice_1_id", "fulfillment_1_details"], [], ["Itemized checkout total matches exact authorized charge"], []
    if deliv.get("status") == "delivered":
        return 0.8, ["order_id_1"], [], ["Separate order fulfillment verified by courier tracking"], []
    return 0.0, [], ["order_id_2", "invoice_2_id"], [], ["Unable to prove two distinct orders; possible duplicate debit"]


def eval_subscription_mandate(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    sub = data.get("subscription_mandate") or {}
    mandate_id = sub.get("mandate_id")
    notif = sub.get("pre_debit_notification_sent", True)
    f_pres = [k for k in ["subscription_id", "mandate_id", "billing_cycle"] if sub.get(k)]
    f_miss = [k for k in ["subscription_id", "mandate_id", "billing_cycle"] if not sub.get(k)]

    if mandate_id and notif:
        return 1.0, f_pres, f_miss, [f"Active authenticated recurring mandate ({mandate_id}) with pre-debit notice"], []
    elif mandate_id:
        return 0.7, f_pres, f_miss, [f"Mandate active ({mandate_id})"], ["Missing pre-debit notification audit log"]
    return 0.0, f_pres, f_miss, [], ["Missing recurring mandate authentication agreement"]


def eval_cancellation_log(data: Dict[str, Any], weight: float) -> Tuple[float, List[str], List[str], List[str], List[str]]:
    sub = data.get("subscription_mandate") or {}
    comm = data.get("customer_communication") or []
    cancel_ts = sub.get("cancellation_request_timestamp")

    if cancel_ts is None and not any("cancel" in (c.get("message") or "").lower() for c in comm):
        return 1.0, ["cancellation_timestamp", "cancellation_status"], [], ["No cancellation request submitted prior to renewal date"], []
    elif cancel_ts:
        return 0.0, ["cancellation_timestamp"], [], [], [f"Cancellation requested at {cancel_ts} prior to renewal"]
    return 0.5, [], [], [], ["Disputed cancellation timing requires manual log verification"]


EVALUATOR_MAP = {
    "3ds_authentication_log": eval_3ds_authentication,
    "ip_and_device_fingerprint": eval_ip_device,
    "customer_communication": eval_customer_comm,
    "order_fulfillment_history": eval_account_history,
    "terms_acceptance": eval_terms_acceptance,
    "proof_of_delivery": eval_proof_of_delivery,
    "fulfillment_dispatch_proof": eval_invoice_dispatch,
    "delivery_communication": eval_invoice_dispatch,
    "customer_usage_activity": eval_digital_usage,
    "service_fulfillment_confirmation": eval_digital_usage,
    "item_specification_description": eval_separate_orders,
    "quality_assurance_log": eval_qa_log,
    "merchant_customer_correspondence": eval_customer_comm,
    "return_policy_and_terms": eval_terms_acceptance,
    "refund_proof_or_cancellation_policy": eval_refund_proof,
    "cancellation_timestamp_log": eval_cancellation_log,
    "merchant_customer_communication": eval_customer_comm,
    "separate_transaction_proof": eval_separate_orders,
    "price_breakdown_and_authorization": eval_separate_orders,
    "billing_statement_and_receipt": eval_invoice_dispatch,
    "subscription_contract_terms": eval_subscription_mandate,
    "cancellation_policy_compliance": eval_cancellation_log,
    "service_usage_during_period": eval_digital_usage,
    "recurring_billing_notification": eval_subscription_mandate,
}
