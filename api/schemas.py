"""Pydantic request and response schemas for the DisputeShield API."""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, model_validator
from data.schemas import DisputeCase


class AnalyzeRequest(BaseModel):
    model_name: Optional[str] = Field(None, description="LLM model name to use for drafting")
    use_llm: bool = Field(False, description="Whether to call external LLM or deterministic engine")
    evidence_overrides: Optional[Dict[str, Any]] = Field(default=None, description="Optional override slices for what-if simulations")


class CustomDisputeInput(BaseModel):
    dispute_id: Optional[str] = Field("disp_custom_adhoc", description="Optional ID for custom case")
    case_id: Optional[str] = None
    dispute_category: Optional[str] = None
    category: Optional[str] = None
    reason_code: str = Field("10.4", description="Dispute reason code")
    dispute_amount: Optional[float] = None
    dispute_amount_inr: Optional[float] = None
    currency: str = Field("INR", description="Currency ISO code")
    merchant_name: str = Field("Merchant Store", description="Merchant business name")
    merchant_category: str = Field("General Retail", description="Merchant MCC or category")
    payment_method: str = Field("card", description="card, upi, netbanking, or wallet")
    card_network: Optional[str] = Field(None, description="Visa, Mastercard, RuPay, Amex")
    filed_date: str = Field("2026-08-20", description="Dispute filing timestamp")
    due_date: str = Field("2026-08-30", description="Dispute evidence submission deadline")
    evidence_slices: Dict[str, Any] = Field(default_factory=dict, description="Provided evidence payload slices")
    auth_3ds: Optional[Dict[str, Any]] = None
    delivery_tracking: Optional[Dict[str, Any]] = None
    invoice_dispatch: Optional[Dict[str, Any]] = None
    customer_communication: Optional[List[Dict[str, Any]]] = None
    customer_account: Optional[Dict[str, Any]] = None
    refund_log: Optional[Dict[str, Any]] = None
    price_breakdown: Optional[Dict[str, Any]] = None
    subscription_mandate: Optional[Dict[str, Any]] = None
    service_usage: Optional[Dict[str, Any]] = None
    merchant_notes: Optional[str] = None

    @model_validator(mode="after")
    def populate_aliases(self) -> "CustomDisputeInput":
        if not self.dispute_category:
            self.dispute_category = self.category or "fraudulent_unauthorized"
        if not self.category:
            self.category = self.dispute_category
        if self.dispute_amount is None:
            self.dispute_amount = self.dispute_amount_inr if self.dispute_amount_inr is not None else 1000.0
        if self.dispute_amount_inr is None:
            self.dispute_amount_inr = self.dispute_amount
        if not self.case_id:
            self.case_id = self.dispute_id
        return self


class CaseSummaryItem(BaseModel):
    case_id: str
    dispute_category: str
    reason_code: str
    ground_truth: str
    dispute_amount: float
    currency: str
    merchant_name: str
    merchant_category: str
    payment_method: str
    card_network: Optional[str] = None
    filed_date: str
    due_date: str


class CaseListResponse(BaseModel):
    total_count: int
    categories: Dict[str, int]
    outcomes: Dict[str, int]
    cases: List[CaseSummaryItem]


class EvalRunRequest(BaseModel):
    model_name: Optional[str] = Field(None, description="Optional LLM model for evaluation")
    use_llm: bool = Field(False, description="Evaluate using deterministic engine or LLM")
    save_results: bool = Field(True, description="Whether to save evaluation results to disk")


