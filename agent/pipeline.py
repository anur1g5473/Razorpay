"""Full agent pipeline orchestrator.

Coordinates the 5-step dispute defense lifecycle:
  1. Retrieve — fetch modular evidence slices via retriever tools
  2. Score    — deterministic rubric-based evidence scoring & quality checks
  3. Decide   — contest / review / abstain / accept decision engine
  4. Draft    — grounded rebuttal response letter (LLM or verified template)
  5. Output   — structured result with confidence, rationale, and metrics
"""

from __future__ import annotations
import time
from typing import Dict, Any, List, Optional, Union, Literal
from pydantic import BaseModel, Field

from agent.tools import retrieve_all_slices
from agent.scorer import score_dispute_case, ScoringResult
from agent.drafter import draft_rebuttal_letter
from data.schemas import DisputeCase


class PipelineResult(BaseModel):
    case_id: Optional[str] = None
    dispute_category: str
    category_title: str
    reason_code: str
    decision: Literal["CONTEST", "REVIEW", "ABSTAIN", "ACCEPT"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    total_score: float = Field(..., ge=0.0, le=100.0)
    win_probability_estimate: float = Field(..., ge=0.0, le=1.0)
    retrieved_slices: Dict[str, Any] = Field(default_factory=dict)
    scoring_result: ScoringResult
    rebuttal_letter: Optional[str] = None
    actionable_recommendations: List[str] = Field(default_factory=list)
    missing_critical_items: List[str] = Field(default_factory=list)
    ground_truth_label: Optional[str] = None
    predicted_outcome: str = Field(..., description="WIN, LOSE, or AMBIGUOUS / REVIEW")
    execution_time_ms: float = 0.0


def run_pipeline(
    case: Union[DisputeCase, Dict[str, Any]],
    use_llm: bool = True,
) -> PipelineResult:
    """Executes the full dispute defense pipeline on a single case."""
    start_time = time.perf_counter()

    if isinstance(case, DisputeCase):
        data = case.model_dump()
        case_id = case.case_id
        ground_truth = getattr(case, "ground_truth", None) or getattr(case, "expected_outcome", None)
        reason_code = case.reason_code
    elif isinstance(case, dict):
        data = case
        case_id = case.get("case_id")
        ground_truth = case.get("ground_truth") or case.get("expected_outcome")
        reason_code = case.get("reason_code", "N/A")
    else:
        raise ValueError("Input must be a DisputeCase instance or dictionary")

    # Step 1: Retrieve evidence slices
    slices = retrieve_all_slices(data)

    # Step 2: Deterministic Rubric Scoring
    scoring_result = score_dispute_case(data)

    # Step 3: Map Decision to predicted outcome
    if scoring_result.recommendation == "CONTEST":
        predicted_outcome = "win"
    elif scoring_result.recommendation in ("ABSTAIN", "ACCEPT"):
        predicted_outcome = "lose"
    else:
        predicted_outcome = "ambiguous"

    # Step 4: Draft Response Letter
    rebuttal_letter = None
    if scoring_result.recommendation in ("CONTEST", "REVIEW"):
        rebuttal_letter = draft_rebuttal_letter(data, scoring_result, use_llm=use_llm)

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    return PipelineResult(
        case_id=case_id,
        dispute_category=scoring_result.category_id,
        category_title=scoring_result.category_title,
        reason_code=reason_code,
        decision=scoring_result.recommendation,
        confidence=scoring_result.confidence,
        total_score=scoring_result.total_score,
        win_probability_estimate=scoring_result.win_probability_estimate,
        retrieved_slices=slices,
        scoring_result=scoring_result,
        rebuttal_letter=rebuttal_letter,
        actionable_recommendations=scoring_result.actionable_recommendations,
        missing_critical_items=scoring_result.missing_critical_items,
        ground_truth_label=ground_truth,
        predicted_outcome=predicted_outcome,
        execution_time_ms=elapsed_ms,
    )


def run_pipeline_batch(
    cases: List[Union[DisputeCase, Dict[str, Any]]],
    use_llm: bool = False,
) -> List[PipelineResult]:
    """Executes the pipeline over a batch of cases."""
    return [run_pipeline(c, use_llm=use_llm) for c in cases]

