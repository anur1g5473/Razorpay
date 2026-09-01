"""Pydantic schemas for DisputeShield dispute cases and evidence slices."""

from __future__ import annotations
from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field


class Auth3DSData(BaseModel):
    auth_type: Optional[str] = Field(None, description="3DS_V2, 3DS_V1, UPI_PIN, OTP, NONE")
    cavv_eci: Optional[str] = Field(None, description="ECI indicator e.g. 05, 02, 06, 07, 01")
    auth_timestamp: Optional[str] = None
    status: Optional[str] = Field(None, description="authenticated, attempted, failed, bypassed")
    transaction_reference: Optional[str] = None
    bank_reference_number: Optional[str] = None
    ip_address: Optional[str] = None
    device_fingerprint: Optional[str] = None
    vpn_detected: Optional[bool] = False
    geo_location_match: Optional[bool] = True


class DeliveryTrackingData(BaseModel):
    carrier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = Field(None, description="delivered, in_transit, rto, failed, pending")
    dispatch_date: Optional[str] = None
    delivery_timestamp: Optional[str] = None
    shipping_address: Optional[str] = None
    delivered_to_address: Optional[str] = None
    recipient_signature: Optional[str] = None
    recipient_gps: Optional[str] = None
    rto_reason: Optional[str] = None
    weight_kg: Optional[float] = None


class InvoiceDispatchData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    line_items: List[Dict[str, Any]] = Field(default_factory=list)
    item_manifest_verified: bool = True
    shipping_label_id: Optional[str] = None
    total_amount: Optional[float] = None
    tax_amount: Optional[float] = None
    shipping_fee: Optional[float] = None


class CustomerCommunicationLog(BaseModel):
    ticket_id: Optional[str] = None
    timestamp: Optional[str] = None
    sender: Optional[str] = None
    message: Optional[str] = None
    resolution_offered: Optional[str] = None
    customer_response: Optional[str] = None
    return_label_sent: Optional[bool] = None


class CustomerAccountData(BaseModel):
    account_id: Optional[str] = None
    created_date: Optional[str] = None
    prior_order_count: int = 0
    prior_undisputed_amount: float = 0.0
    account_email: Optional[str] = None
    account_phone: Optional[str] = None
    matches_billing: bool = True
    kyc_verified: bool = False


class RefundLogData(BaseModel):
    refund_id: Optional[str] = None
    arn_rrn: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = Field(None, description="processed, failed, pending, none")
    refund_timestamp: Optional[str] = None
    store_credit_code: Optional[str] = None
    store_credit_redeemed: Optional[bool] = False


class PriceBreakdownData(BaseModel):
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    shipping: Optional[float] = None
    discount: Optional[float] = 0.0
    total_authorized: Optional[float] = None
    currency: str = "INR"
    item_specifications_url: Optional[str] = None


class SubscriptionMandateData(BaseModel):
    subscription_id: Optional[str] = None
    mandate_id: Optional[str] = None
    billing_cycle: Optional[str] = "monthly"
    recurrence_amount: Optional[float] = None
    signup_timestamp: Optional[str] = None
    pre_debit_notification_sent: bool = True
    pre_debit_timestamp: Optional[str] = None
    cancellation_request_timestamp: Optional[str] = None
    terms_version: Optional[str] = "v2.1"


class ServiceUsageData(BaseModel):
    account_id: Optional[str] = None
    active_login_count: int = 0
    last_login_timestamp: Optional[str] = None
    license_key_activated: Optional[bool] = None
    features_used: List[str] = Field(default_factory=list)
    bytes_transferred: Optional[int] = None


class DisputeCase(BaseModel):
    case_id: str = Field(..., description="Unique dispute identifier e.g. disp_1001")
    merchant_id: str = Field(..., description="Merchant account ID e.g. merch_ind_01")
    merchant_name: str = Field(..., description="Business / Brand Name")
    merchant_category: str = Field(..., description="E-commerce, SaaS, Travel, QuickCommerce, EdTech, D2C")
    payment_id: str = Field(..., description="Razorpay Payment ID e.g. pay_Nabc123")
    dispute_amount: float = Field(..., gt=0.0, description="Amount in INR")
    currency: str = "INR"
    payment_method: Literal["card", "upi", "netbanking", "wallet", "emi"] = "card"
    card_network: Optional[str] = None  # Visa, Mastercard, RuPay, Amex, UPI
    dispute_category: str = Field(..., description="Category matching evidence rubric")
    reason_code: str = Field(..., description="Network or UPI reason code")
    reason_description: str = Field(..., description="Reason code explanation")
    filed_date: str = Field(..., description="Date dispute was raised YYYY-MM-DD")
    due_date: str = Field(..., description="Submission deadline YYYY-MM-DD")
    ground_truth: Literal["win", "lose", "ambiguous"] = Field(
        ..., description="Expected outcome based on objective rubric"
    )
    ground_truth_reasoning: str = Field(..., description="Explanation of why this case is win/lose/ambiguous")

    # Evidence Slices
    auth_3ds: Optional[Auth3DSData] = None
    delivery_tracking: Optional[DeliveryTrackingData] = None
    invoice_dispatch: Optional[InvoiceDispatchData] = None
    customer_communication: List[CustomerCommunicationLog] = Field(default_factory=list)
    customer_account: Optional[CustomerAccountData] = None
    refund_logs: Optional[RefundLogData] = None
    price_breakdown: Optional[PriceBreakdownData] = None
    subscription_mandate: Optional[SubscriptionMandateData] = None
    service_usage: Optional[ServiceUsageData] = None
    merchant_notes: Optional[str] = None
