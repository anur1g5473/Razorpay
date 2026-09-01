"""Retriever tool functions for the agent pipeline.

Each function simulates a distinct "tool call" the agent or LLM makes to fetch
one slice of case data. This keeps the design modular (no mega-prompt) and
mirrors how a real production agent works against live Razorpay / merchant APIs.
"""

from __future__ import annotations
from typing import Dict, Any, Optional


def get_transaction_details(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve core transaction and payment gateway details."""
    txn = case_data.get("transaction", {})
    return {
        "payment_id": txn.get("payment_id") or case_data.get("payment_id", "N/A"),
        "order_id": txn.get("order_id") or case_data.get("order_id", "N/A"),
        "amount": txn.get("amount") or case_data.get("amount", 0.0),
        "currency": txn.get("currency") or case_data.get("currency", "INR"),
        "payment_method": txn.get("payment_method") or case_data.get("payment_method", "card"),
        "created_at": txn.get("created_at") or case_data.get("created_at", "N/A"),
        "bank_arn": txn.get("bank_arn") or case_data.get("bank_arn"),
        "bank_rrn": txn.get("bank_rrn") or case_data.get("bank_rrn"),
        "merchant_id": txn.get("merchant_id") or case_data.get("merchant_id", "rzp_live_default"),
        "gateway_status": txn.get("gateway_status", "captured"),
    }


def get_customer_profile(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve customer identity and account history."""
    cust = case_data.get("customer", {})
    return {
        "customer_id": cust.get("customer_id", "guest"),
        "name": cust.get("name") or cust.get("customer_name", "N/A"),
        "email": cust.get("email") or cust.get("customer_email", "N/A"),
        "phone": cust.get("phone") or cust.get("customer_phone", "N/A"),
        "billing_address": cust.get("billing_address", {}),
        "account_created_at": cust.get("account_created_at") or cust.get("account_created_date"),
        "prior_orders_count": cust.get("prior_orders_count", 0),
        "prior_undisputed_amount": cust.get("prior_undisputed_amount", 0.0),
    }


def get_authentication_log(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve 3DS, OTP, UPI PIN, and device/IP authentication telemetry."""
    auth = case_data.get("authentication", {})
    dev = case_data.get("device_and_network", {})
    return {
        "auth_type": auth.get("auth_type", "NONE"),
        "auth_status": auth.get("auth_status") or auth.get("status", "NOT_AUTHENTICATED"),
        "cavv_eci": auth.get("cavv_eci") or auth.get("eci_indicator"),
        "auth_timestamp": auth.get("auth_timestamp") or auth.get("timestamp"),
        "transaction_reference": auth.get("transaction_reference"),
        "ip_address": dev.get("ip_address") or case_data.get("ip_address"),
        "device_id": dev.get("device_id") or case_data.get("device_id"),
        "geo_location": dev.get("geo_location") or case_data.get("geo_location"),
        "user_agent": dev.get("user_agent"),
        "vpn_detected": dev.get("vpn_detected", False),
        "proxy_detected": dev.get("proxy_detected", False),
    }


def get_fulfillment_and_delivery(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve logistics, courier tracking, and delivery confirmation."""
    fulfill = case_data.get("fulfillment", {})
    digital = case_data.get("digital_access", {})
    return {
        "is_digital": case_data.get("is_digital_goods", False) or bool(digital),
        "carrier_name": fulfill.get("carrier_name") or fulfill.get("carrier"),
        "tracking_number": fulfill.get("tracking_number"),
        "shipping_address": fulfill.get("shipping_address", {}),
        "dispatch_date": fulfill.get("dispatch_date"),
        "delivery_timestamp": fulfill.get("delivery_timestamp") or fulfill.get("delivered_at"),
        "delivery_status": fulfill.get("status") or fulfill.get("delivery_status", "UNKNOWN"),
        "recipient_signature": fulfill.get("recipient_signature"),
        "gps_coordinates": fulfill.get("gps_coordinates"),
        "dispatch_manifest_id": fulfill.get("dispatch_manifest_id") or fulfill.get("shipping_label_id"),
        "invoice_number": fulfill.get("invoice_number"),
        "digital_access_logs": digital.get("login_timestamps", []),
        "license_key": digital.get("license_key"),
        "bytes_downloaded": digital.get("bytes_downloaded", 0),
        "feature_accessed": digital.get("feature_accessed"),
    }


def get_customer_communication(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve merchant-customer communication, support tickets, and chat logs."""
    comm = case_data.get("communication", {})
    return {
        "tickets": comm.get("tickets", []),
        "email_threads": comm.get("email_threads", []),
        "latest_ticket_id": comm.get("latest_ticket_id"),
        "resolution_offered": comm.get("resolution_offered"),
        "customer_acknowledged": comm.get("customer_acknowledged", False),
        "store_credit_agreed": comm.get("store_credit_agreed", False),
        "store_credit_code": comm.get("store_credit_code"),
    }


def get_policies_and_terms(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve accepted policies, terms of service, and refund policy links."""
    terms = case_data.get("terms_and_policies", {})
    return {
        "terms_version": terms.get("terms_version", "v1.0"),
        "acceptance_timestamp": terms.get("acceptance_timestamp"),
        "ip_at_acceptance": terms.get("ip_at_acceptance"),
        "return_policy_url": terms.get("return_policy_url"),
        "return_window_days": terms.get("return_window_days", 14),
        "cancellation_cutoff_hours": terms.get("cancellation_cutoff_hours", 24),
    }


def get_refund_and_billing_history(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve refund status, double billing checks, and prior receipts."""
    ref = case_data.get("refund", {})
    dup = case_data.get("duplicate_check", {})
    return {
        "refund_id": ref.get("refund_id"),
        "refund_arn": ref.get("arn") or ref.get("arn_rrn"),
        "refund_amount": ref.get("amount"),
        "refund_status": ref.get("status"),
        "refund_timestamp": ref.get("refund_timestamp") or ref.get("timestamp"),
        "order_1_id": dup.get("order_1_id"),
        "order_2_id": dup.get("order_2_id"),
        "order_1_fulfilled": dup.get("order_1_fulfilled", False),
        "order_2_fulfilled": dup.get("order_2_fulfilled", False),
        "distinct_items": dup.get("distinct_items", False),
    }


def get_subscription_mandate(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieve recurring mandate registration, pre-debit notifications, and cancellation audits."""
    sub = case_data.get("subscription", {})
    return {
        "subscription_id": sub.get("subscription_id"),
        "mandate_id": sub.get("mandate_id"),
        "billing_interval": sub.get("billing_interval", "monthly"),
        "recurring_amount": sub.get("recurring_amount"),
        "pre_debit_notification_sent": sub.get("pre_debit_notification_sent", False),
        "pre_debit_notification_timestamp": sub.get("pre_debit_notification_timestamp"),
        "cancellation_requested": sub.get("cancellation_requested", False),
        "cancellation_timestamp": sub.get("cancellation_timestamp"),
        "service_used_in_period": sub.get("service_used_in_period", False),
    }


def retrieve_all_slices(case_data: Dict[str, Any]) -> Dict[str, Any]:
    """Retrieves all evidence slices for comprehensive agent evaluation."""
    return {
        "transaction": get_transaction_details(case_data),
        "customer": get_customer_profile(case_data),
        "authentication": get_authentication_log(case_data),
        "fulfillment": get_fulfillment_and_delivery(case_data),
        "communication": get_customer_communication(case_data),
        "policies": get_policies_and_terms(case_data),
        "refund_and_billing": get_refund_and_billing_history(case_data),
        "subscription": get_subscription_mandate(case_data),
    }

