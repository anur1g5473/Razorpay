"""Deterministic Evidence Scorer for DisputeShield.

Evaluates evidence payloads against category-specific rubrics. Computes weighted
scores, flags missing critical / important items, evaluates quality indicators,
detects hard abstention triggers, and produces actionable contest recommendations.
"""

from __future__ import annotations
from typing import List, Dict, Optional, Any, Literal, Union
from pydantic import BaseModel, Field

from rubric.rubric_loader import (
    get_category_rubric,
    get_rubric,
    check_abstention_triggers,
)
from rubric.models import DisputeCategoryRubric, EvidenceItem
from data.schemas import DisputeCase


class EvidenceItemScore(BaseModel):
    item_id: str
    name: str
    weight: float
    compelling_level: Literal["critical", "important", "supporting"]
    present: bool
    score_awarded: float = Field(..., ge=0.0)
    max_score: float = Field(..., ge=0.0)
    score_percentage: float = Field(..., ge=0.0, le=100.0)
    fields_present: List[str] = Field(default_factory=list)
    fields_missing: List[str] = Field(default_factory=list)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)


class ScoringResult(BaseModel):
    case_id: Optional[str] = None
    category_id: str
    category_title: str
    total_score: float = Field(..., ge=0.0, le=100.0, description="Weighted composite score out of 100")
    recommendation: Literal["CONTEST", "REVIEW", "ABSTAIN", "ACCEPT"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    win_probability_estimate: float = Field(..., ge=0.0, le=1.0)
    item_scores: List[EvidenceItemScore] = Field(default_factory=list)
    missing_critical_items: List[str] = Field(default_factory=list)
    missing_important_items: List[str] = Field(default_factory=list)
    missing_supporting_items: List[str] = Field(default_factory=list)
    abstention_triggered: bool = False
    abstention_reasons: List[str] = Field(default_factory=list)
    quality_warnings: List[str] = Field(default_factory=list)
    actionable_recommendations: List[str] = Field(default_factory=list)

from agent.eval_rules import EVALUATOR_MAP


def score_dispute_case(case: Union[DisputeCase, Dict[str, Any]]) -> ScoringResult:
    """Scores a single dispute case payload against its category rubric."""
    if isinstance(case, DisputeCase):
        data = case.model_dump()
        case_id = case.case_id
        cat_id_or_code = case.dispute_category or case.reason_code
    elif isinstance(case, dict):
        data = case
        case_id = case.get("case_id")
        cat_id_or_code = case.get("dispute_category") or case.get("reason_code") or "fraudulent_unauthorized"
    else:
        raise ValueError("Input must be DisputeCase or dict")

    cat = get_category_rubric(cat_id_or_code)
    if not cat:
        cat = get_category_rubric("fraudulent_unauthorized")

    # Evaluate each required evidence item
    item_scores: List[EvidenceItemScore] = []
    total_score = 0.0
    missing_crit: List[str] = []
    missing_imp: List[str] = []
    missing_sup: List[str] = []
    warnings: List[str] = []

    for item in cat.required_evidence:
        eval_fn = EVALUATOR_MAP.get(item.item_id)
        if eval_fn:
            ratio, f_pres, f_miss, strengths, weaknesses = eval_fn(data, item.weight)
        else:
            ratio, f_pres, f_miss, strengths, weaknesses = (0.5, [], [], ["Present in standard payload"], [])

        awarded = round(item.weight * ratio, 2)
        total_score += awarded
        present = ratio > 0.0

        if not present:
            if item.compelling_level == "critical":
                missing_crit.append(item.name)
            elif item.compelling_level == "important":
                missing_imp.append(item.name)
            else:
                missing_sup.append(item.name)

        if weaknesses:
            warnings.extend(weaknesses)

        item_scores.append(
            EvidenceItemScore(
                item_id=item.item_id,
                name=item.name,
                weight=item.weight,
                compelling_level=item.compelling_level,
                present=present,
                score_awarded=awarded,
                max_score=item.weight,
                score_percentage=round(ratio * 100, 1),
                fields_present=f_pres,
                fields_missing=f_miss,
                strengths=strengths,
                weaknesses=weaknesses,
            )
        )

    total_score = min(100.0, round(total_score, 2))

    # Check for hard abstention triggers
    abstention_reasons = check_abstention_triggers(cat.category_id, data)
    abstention_triggered = len(abstention_reasons) > 0

    # Determine recommendation, confidence, and win probability
    high_th = max(60.0, cat.win_probability_thresholds.high * 80.0)
    med_th = max(35.0, cat.win_probability_thresholds.medium * 75.0)

    actionable_recs = []
    if missing_crit:
        actionable_recs.append(f"Upload critical missing evidence: {', '.join(missing_crit)}")
    if missing_imp:
        actionable_recs.append(f"Attach supporting documentation: {', '.join(missing_imp)}")

    if abstention_triggered:
        recommendation = "ABSTAIN"
        confidence = "HIGH"
        win_prob = 0.10
        actionable_recs.append("Recommend dispute acceptance or manual human review due to hard network liability rules.")
    elif total_score >= high_th and not missing_crit:
        recommendation = "CONTEST"
        confidence = "HIGH" if total_score >= 75.0 else "MEDIUM"
        win_prob = round(0.70 + (total_score / 100.0) * 0.25, 2)
        actionable_recs.append("Submit full compelling evidence pack to card network / issuer.")
    elif total_score >= med_th:
        recommendation = "REVIEW"
        confidence = "MEDIUM"
        win_prob = round(0.40 + (total_score / 100.0) * 0.20, 2)
        actionable_recs.append("Review highlighted evidence gaps before contest submission.")
    else:
        recommendation = "ACCEPT"
        confidence = "HIGH" if total_score < 25.0 else "MEDIUM"
        win_prob = round((total_score / 100.0) * 0.35, 2)
        actionable_recs.append("Insufficient compelling evidence to overcome dispute burden of proof.")

    return ScoringResult(
        case_id=case_id,
        category_id=cat.category_id,
        category_title=cat.title,
        total_score=total_score,
        recommendation=recommendation,
        confidence=confidence,
        win_probability_estimate=min(0.99, max(0.01, win_prob)),
        item_scores=item_scores,
        missing_critical_items=missing_crit,
        missing_important_items=missing_imp,
        missing_supporting_items=missing_sup,
        abstention_triggered=abstention_triggered,
        abstention_reasons=abstention_reasons,
        quality_warnings=warnings,
        actionable_recommendations=actionable_recs,
    )


def batch_score_cases(cases: List[Union[DisputeCase, Dict[str, Any]]]) -> List[ScoringResult]:
    """Scores a batch of dispute cases."""
    return [score_dispute_case(c) for c in cases]

