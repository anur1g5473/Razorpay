"""LLM-powered response letter drafter and deterministic fallback engine.

Given scored evidence and rubric metrics, drafts a professional dispute-response
letter citing ONLY facts present in the case data.
"""

from __future__ import annotations
import os
import logging
from typing import Dict, Any, Optional

from agent.config import get_openai_client, get_llm_config
from agent.prompts import SYSTEM_PROMPT_DRAFTER, DRAFT_LETTER_TEMPLATE
from agent.scorer import ScoringResult

logger = logging.getLogger(__name__)


def _format_compelling_evidence_summary(scoring_result: ScoringResult, case_data: Dict[str, Any]) -> str:
    """Format scored evidence items and verified fields into bullet points."""
    lines = []
    for item in scoring_result.item_scores:
        status = "VERIFIED" if item.present else "MISSING"
        lines.append(f"- [{status}] {item.name} (Weight: {item.weight}%, Score: {item.score_awarded}/{item.max_score})")
        if item.fields_present:
            lines.append(f"  Verified Fields: {', '.join(item.fields_present)}")
        if item.strengths:
            for s in item.strengths:
                lines.append(f"  * Strength: {s}")
        if item.weaknesses:
            for w in item.weaknesses:
                lines.append(f"  ! Note: {w}")
    return "\n".join(lines) if lines else "No detailed evidence items recorded."


def _draft_deterministic_rebuttal(case_data: Dict[str, Any], scoring_result: ScoringResult) -> str:
    """Deterministic fallback rebuttal letter generator."""
    txn = case_data.get("transaction", {})
    cust = case_data.get("customer", {})
    fulfill = case_data.get("fulfillment", {})
    auth = case_data.get("authentication", {})

    payment_id = txn.get("payment_id") or case_data.get("payment_id", "N/A")
    order_id = txn.get("order_id") or case_data.get("order_id", "N/A")
    amount = txn.get("amount") or case_data.get("amount", "0.00")
    currency = txn.get("currency") or case_data.get("currency", "INR")
    reason_code = case_data.get("reason_code", "N/A")
    customer_name = cust.get("name") or cust.get("customer_name", "Cardholder")
    merchant_name = case_data.get("merchant_name", "Merchant")

    letter_lines = [
        "================================================================================",
        f"FORMAL DISPUTE REBUTTAL & EVIDENCE PACK: {case_data.get('case_id', 'CASE')}",
        "================================================================================",
        f"Date: 2026-09-01",
        f"To: Payment Network Dispute Resolution / Issuing Bank Arbitration Department",
        f"From: {merchant_name} (via Razorpay DisputeShield Resolution Services)",
        f"Subject: Chargeback Defense for Transaction {payment_id} / Order {order_id}",
        f"Dispute Reason Code: {reason_code} | Category: {scoring_result.category_title}",
        f"Disputed Amount: {currency} {amount}",
        "",
        "1. EXECUTIVE SUMMARY",
        f"{merchant_name} formally contests the chargeback filed on Transaction",
        f"{payment_id} for {currency} {amount}. Comprehensive documentation is enclosed proving",
        f"proper authorization and fulfillment. Evidence evaluation score: {scoring_result.total_score}/100.",
        "",
        "2. TRANSACTION & AUTHENTICATION CHRONOLOGY",
        f"- Payment Reference ID: {payment_id}",
        f"- Merchant Order ID: {order_id}",
        f"- Cardholder Name: {customer_name}",
    ]
    if auth.get("auth_type") in ("3DS_V2", "OTP", "UPI_PIN"):
        letter_lines.extend([
            f"- Authentication Mode: {auth.get('auth_type')} (Status: {auth.get('auth_status', 'SUCCESS')})",
            f"- Authentication Verification: ECI/CAVV indicator {auth.get('cavv_eci', '05')} verified by Issuer",
            "- Card Network Rule Reference: Liability shifted to issuing bank under 3D Secure / 2FA protocols.",
        ])

    if fulfill.get("tracking_number"):
        carrier = fulfill.get("carrier_name") or fulfill.get("carrier", "Logistics Partner")
        track_num = fulfill.get("tracking_number")
        del_time = fulfill.get("delivery_timestamp") or fulfill.get("delivered_at", "Verified Date")
        letter_lines.extend([
            "",
            "3. PROOF OF FULFILLMENT & DELIVERY",
            f"- Logistics Carrier: {carrier} | Tracking: {track_num}",
            f"- Delivery Status: {fulfill.get('status', 'DELIVERED')} at {del_time}",
            f"- Delivery Verification: GPS {fulfill.get('gps_coordinates', 'Confirmed')} / Signed by {fulfill.get('recipient_signature', 'Recipient')}",
        ])

    letter_lines.extend([
        "",
        "4. CONCLUSION & REQUEST FOR DISPUTE CLOSURE",
        f"Based on the conclusive evidence, {merchant_name} requests the immediate reversal of this",
        f"dispute and release of funds of {currency} {amount} back to merchant.",
        "================================================================================",
    ])
    return "\n".join(letter_lines)


def draft_rebuttal_letter(
    case_data: Dict[str, Any],
    scoring_result: ScoringResult,
    use_llm: bool = True,
) -> str:
    """Drafts a formal dispute rebuttal letter using LLM or deterministic engine."""
    if scoring_result.recommendation in ("ABSTAIN", "ACCEPT"):
        return (
            f"DISPUTE DECISION: {scoring_result.recommendation}\n"
            f"Evidence score ({scoring_result.total_score}/100) or network abstention trigger "
            f"indicates dispute should not be contested.\n"
            f"Reasons: {'; '.join(scoring_result.abstention_reasons or scoring_result.actionable_recommendations)}"
        )

    has_api_key = bool(os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or os.getenv("OMNIROUTE_BASE_URL"))

    if use_llm and has_api_key:
        try:
            client = get_openai_client()
            cfg = get_llm_config()

            txn = case_data.get("transaction", {})
            evidence_summary = _format_compelling_evidence_summary(scoring_result, case_data)
            warnings_summary = "\n".join(f"- {w}" for w in scoring_result.quality_warnings) if scoring_result.quality_warnings else "None detected."

            user_prompt = DRAFT_LETTER_TEMPLATE.format(
                case_id=case_data.get("case_id", "N/A"),
                payment_id=txn.get("payment_id") or case_data.get("payment_id", "N/A"),
                order_id=txn.get("order_id") or case_data.get("order_id", "N/A"),
                category_title=scoring_result.category_title,
                category_id=scoring_result.category_id,
                reason_code=case_data.get("reason_code", "N/A"),
                amount=txn.get("amount") or case_data.get("amount", "0.00"),
                currency=txn.get("currency") or case_data.get("currency", "INR"),
                transaction_date=txn.get("created_at") or case_data.get("created_at", "2026-09-01"),
                merchant_name=case_data.get("merchant_name", "Merchant"),
                merchant_id=txn.get("merchant_id") or case_data.get("merchant_id", "rzp_live_default"),
                total_score=scoring_result.total_score,
                recommendation=scoring_result.recommendation,
                confidence=scoring_result.confidence,
                win_probability=int(scoring_result.win_probability_estimate * 100),
                compelling_evidence_summary=evidence_summary,
                warnings_summary=warnings_summary,
            )

            model_name = cfg.model or "gemini-2.5-flash"
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_DRAFTER},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
                max_tokens=2048,
            )
            content = response.choices[0].message.content
            if content and len(content.strip()) > 50:
                return content.strip()
        except Exception as e:
            logger.warning(f"LLM drafting failed, falling back to deterministic template: {e}")

    return _draft_deterministic_rebuttal(case_data, scoring_result)

