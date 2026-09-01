"""POST /api/analyze/{case_id} — run the agent pipeline on dispute cases."""

from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Body
import copy

from data.generate_cases import load_case
from agent.pipeline import AgentPipeline, PipelineResult
from api.schemas import AnalyzeRequest, CustomDisputeInput

router = APIRouter(prefix="/api/analyze", tags=["analyze"])


def _enhance_result_dict(result_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Provide backward-compatible alias keys in the response."""
    result_dict["dispute_id"] = result_dict.get("case_id", "")
    result_dict["category"] = result_dict.get("dispute_category", "")
    result_dict["recommendation"] = result_dict.get("decision", "")
    result_dict["win_probability"] = result_dict.get("win_probability_estimate", 0.0)
    return result_dict


@router.post("/{case_id}")
async def analyze_case(
    case_id: str,
    request: Optional[AnalyzeRequest] = Body(default=None),
):
    try:
        case = load_case(case_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")

    case_copy = copy.deepcopy(case)

    # Apply optional evidence overrides if supplied
    if request and request.evidence_overrides:
        if "evidence_slices" not in case_copy:
            case_copy["evidence_slices"] = {}
        case_copy["evidence_slices"].update(request.evidence_overrides)

    model_name = request.model_name if request else None
    use_llm = request.use_llm if request else False

    pipeline = AgentPipeline(model_name=model_name, use_llm=use_llm)
    result: PipelineResult = pipeline.run(case_copy)
    return _enhance_result_dict(result.to_dict())


@router.post("/custom/run")
async def analyze_custom_dispute(dispute_input: CustomDisputeInput):
    case_dict = dispute_input.model_dump()
    if not case_dict.get("dispute_id"):
        case_dict["dispute_id"] = "disp_custom_adhoc"
    if not case_dict.get("case_id"):
        case_dict["case_id"] = case_dict["dispute_id"]

    pipeline = AgentPipeline(use_llm=False)
    result: PipelineResult = pipeline.run(case_dict)
    return _enhance_result_dict(result.to_dict())


