"""Metrics computation — precision, recall, F1, confusion matrix, and false-positive cost analysis."""

from __future__ import annotations
from typing import Dict, List, Any
from pydantic import BaseModel

ARBITRATION_PENALTY_FEE_INR = 1500.0


class ClassificationMetrics(BaseModel):
    total_cases: int
    accuracy: float
    precision_contest: float
    recall_contest: float
    f1_contest: float
    precision_accept: float
    recall_accept: float
    f1_accept: float
    precision_review: float
    recall_review: float
    f1_review: float
    macro_f1: float
    weighted_f1: float


class FinancialCostMetrics(BaseModel):
    total_disputed_amount_inr: float
    recovered_amount_inr: float
    prevented_penalty_fees_inr: float
    false_contest_penalty_inr: float
    missed_recovery_inr: float
    net_financial_gain_inr: float
    blind_contest_net_inr: float
    savings_vs_blind_contest_inr: float
    recovery_rate_pct: float


class CategoryPerformance(BaseModel):
    category_id: str
    category_title: str
    total_cases: int
    accuracy: float
    macro_f1: float
    win_cases: int
    lose_cases: int
    ambiguous_cases: int
    net_gain_inr: float


class EvaluationSummary(BaseModel):
    evaluation_id: str
    timestamp: str
    total_cases: int
    classification: ClassificationMetrics
    financial: FinancialCostMetrics
    confusion_matrix: Dict[str, Dict[str, int]]
    category_breakdown: Dict[str, CategoryPerformance]
    latency: Dict[str, float]

    def to_dict(self) -> Dict[str, Any]:
        return self.model_dump()


EvaluationReport = EvaluationSummary


def compute_classification_metrics(predictions: List[Dict[str, Any]]) -> ClassificationMetrics:
    total = len(predictions)
    if total == 0:
        return ClassificationMetrics(
            total_cases=0, accuracy=0.0,
            precision_contest=0.0, recall_contest=0.0, f1_contest=0.0,
            precision_accept=0.0, recall_accept=0.0, f1_accept=0.0,
            precision_review=0.0, recall_review=0.0, f1_review=0.0,
            macro_f1=0.0, weighted_f1=0.0
        )

    correct = 0
    tp = {"contest": 0, "accept": 0, "human_review": 0}
    fp = {"contest": 0, "accept": 0, "human_review": 0}
    fn = {"contest": 0, "accept": 0, "human_review": 0}
    actual_counts = {"contest": 0, "accept": 0, "human_review": 0}

    for p in predictions:
        expected = p.get("expected_outcome", "").upper()
        target = "contest" if expected == "WIN" else ("accept" if expected == "LOSE" else "human_review")
        actual_counts[target] += 1
        predicted = p.get("predicted_recommendation", "").lower()
        if predicted not in tp:
            predicted = "human_review"

        if predicted == target:
            correct += 1
            tp[target] += 1
        else:
            fp[predicted] += 1
            fn[target] += 1

    accuracy = correct / total if total > 0 else 0.0

    def calc_prf(cls: str):
        p = tp[cls] / (tp[cls] + fp[cls]) if (tp[cls] + fp[cls]) > 0 else 0.0
        r = tp[cls] / (tp[cls] + fn[cls]) if (tp[cls] + fn[cls]) > 0 else 0.0
        f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
        return p, r, f1

    p_c, r_c, f1_c = calc_prf("contest")
    p_a, r_a, f1_a = calc_prf("accept")
    p_r, r_r, f1_r = calc_prf("human_review")

    macro_f1 = (f1_c + f1_a + f1_r) / 3.0
    weighted_f1 = (
        (f1_c * actual_counts["contest"])
        + (f1_a * actual_counts["accept"])
        + (f1_r * actual_counts["human_review"])
    ) / total if total > 0 else 0.0

    return ClassificationMetrics(
        total_cases=total,
        accuracy=round(accuracy, 4),
        precision_contest=round(p_c, 4),
        recall_contest=round(r_c, 4),
        f1_contest=round(f1_c, 4),
        precision_accept=round(p_a, 4),
        recall_accept=round(r_a, 4),
        f1_accept=round(f1_a, 4),
        precision_review=round(p_r, 4),
        recall_review=round(r_r, 4),
        f1_review=round(f1_r, 4),
        macro_f1=round(macro_f1, 4),
        weighted_f1=round(weighted_f1, 4),
    )


def compute_confusion_matrix(predictions: List[Dict[str, Any]]) -> Dict[str, Dict[str, int]]:
    cm: Dict[str, Dict[str, int]] = {
        "WIN": {"contest": 0, "accept": 0, "human_review": 0},
        "LOSE": {"contest": 0, "accept": 0, "human_review": 0},
        "AMBIGUOUS": {"contest": 0, "accept": 0, "human_review": 0},
    }
    for p in predictions:
        exp = p.get("expected_outcome", "AMBIGUOUS").upper()
        if exp not in cm:
            exp = "AMBIGUOUS"
        pred = p.get("predicted_recommendation", "human_review").lower()
        if pred not in ["contest", "accept", "human_review"]:
            pred = "human_review"
        cm[exp][pred] += 1
    return cm


def compute_financial_metrics(predictions: List[Dict[str, Any]]) -> FinancialCostMetrics:
    total_amount = 0.0
    recovered_amount = 0.0
    prevented_penalty = 0.0
    false_contest_penalty = 0.0
    missed_recovery = 0.0

    blind_contest_recovery = 0.0
    blind_contest_penalty = 0.0

    for p in predictions:
        amt = float(p.get("dispute_amount", 0.0))
        total_amount += amt
        expected = p.get("expected_outcome", "").upper()
        predicted = p.get("predicted_recommendation", "").lower()

        if expected == "WIN":
            blind_contest_recovery += amt
        elif expected == "LOSE":
            blind_contest_penalty += ARBITRATION_PENALTY_FEE_INR

        if expected == "WIN":
            if predicted == "contest":
                recovered_amount += amt
            else:
                missed_recovery += amt
        elif expected == "LOSE":
            if predicted == "contest":
                false_contest_penalty += ARBITRATION_PENALTY_FEE_INR
            elif predicted == "accept":
                prevented_penalty += ARBITRATION_PENALTY_FEE_INR
        elif expected == "AMBIGUOUS":
            if predicted == "contest":
                false_contest_penalty += ARBITRATION_PENALTY_FEE_INR * 0.5

    net_gain = (recovered_amount + prevented_penalty) - (false_contest_penalty + missed_recovery)
    blind_net = blind_contest_recovery - blind_contest_penalty
    savings_vs_blind = (recovered_amount - false_contest_penalty) - blind_net

    total_winnable = sum(
        float(p.get("dispute_amount", 0.0)) for p in predictions if p.get("expected_outcome", "").upper() == "WIN"
    )
    recovery_rate = (recovered_amount / total_winnable * 100.0) if total_winnable > 0 else 0.0

    return FinancialCostMetrics(
        total_disputed_amount_inr=round(total_amount, 2),
        recovered_amount_inr=round(recovered_amount, 2),
        prevented_penalty_fees_inr=round(prevented_penalty, 2),
        false_contest_penalty_inr=round(false_contest_penalty, 2),
        missed_recovery_inr=round(missed_recovery, 2),
        net_financial_gain_inr=round(net_gain, 2),
        blind_contest_net_inr=round(blind_net, 2),
        savings_vs_blind_contest_inr=round(savings_vs_blind, 2),
        recovery_rate_pct=round(recovery_rate, 2),
    )


def compute_category_breakdown(predictions: List[Dict[str, Any]]) -> Dict[str, CategoryPerformance]:
    by_category: Dict[str, List[Dict[str, Any]]] = {}
    for p in predictions:
        cat = p.get("category_id", "unknown")
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(p)

    results: Dict[str, CategoryPerformance] = {}
    for cat_id, cat_preds in by_category.items():
        title = cat_preds[0].get("category_title", cat_id) if cat_preds else cat_id
        cls_metrics = compute_classification_metrics(cat_preds)
        fin_metrics = compute_financial_metrics(cat_preds)

        win_count = sum(1 for p in cat_preds if p.get("expected_outcome", "").upper() == "WIN")
        lose_count = sum(1 for p in cat_preds if p.get("expected_outcome", "").upper() == "LOSE")
        amb_count = sum(1 for p in cat_preds if p.get("expected_outcome", "").upper() == "AMBIGUOUS")

        results[cat_id] = CategoryPerformance(
            category_id=cat_id,
            category_title=title,
            total_cases=len(cat_preds),
            accuracy=cls_metrics.accuracy,
            macro_f1=cls_metrics.macro_f1,
            win_cases=win_count,
            lose_cases=lose_count,
            ambiguous_cases=amb_count,
            net_gain_inr=fin_metrics.net_financial_gain_inr,
        )

    return results

