"""GET /api/cases — list and retrieve synthetic dispute cases."""

from __future__ import annotations
from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Query

from data.generate_cases import load_all_cases, load_case_by_id
from data.schemas import DisputeCase
from api.schemas import CaseListResponse, CaseSummaryItem

router = APIRouter(prefix="/api/cases", tags=["cases"])


@router.get("", response_model=CaseListResponse)
async def list_cases(
    category: Optional[str] = Query(None, description="Filter by dispute category"),
    outcome: Optional[str] = Query(None, description="Filter by outcome (win, lose, ambiguous)"),
    expected_outcome: Optional[str] = Query(None, description="Alias for outcome"),
    search: Optional[str] = Query(None, description="Search keyword in ID, merchant, reason code"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    target_outcome = outcome or expected_outcome
    all_cases = load_all_cases()
    filtered = []

    # Compute category & outcome aggregates across all cases
    categories_count: Dict[str, int] = {}
    outcomes_count: Dict[str, int] = {}

    for c in all_cases:
        cat = c.dispute_category
        out = c.ground_truth
        categories_count[cat] = categories_count.get(cat, 0) + 1
        outcomes_count[out] = outcomes_count.get(out, 0) + 1

        # Apply filters
        if category and c.dispute_category != category:
            continue
        if target_outcome and c.ground_truth != target_outcome:
            continue
        if search:
            q = search.lower()
            m_name = c.merchant_name.lower()
            d_id = c.case_id.lower()
            rcode = c.reason_code.lower()
            cat_name = c.dispute_category.lower()
            if q not in m_name and q not in d_id and q not in rcode and q not in cat_name:
                continue

        item = CaseSummaryItem(
            case_id=c.case_id,
            dispute_category=c.dispute_category,
            reason_code=c.reason_code,
            ground_truth=c.ground_truth,
            dispute_amount=float(c.dispute_amount),
            currency=c.currency,
            merchant_name=c.merchant_name,
            merchant_category=c.merchant_category,
            payment_method=c.payment_method,
            card_network=c.card_network,
            filed_date=c.filed_date,
            due_date=c.due_date,
        )
        filtered.append(item)

    paginated = filtered[offset : offset + limit]
    return CaseListResponse(
        total_count=len(filtered),
        categories=categories_count,
        outcomes=outcomes_count,
        cases=paginated,
    )


@router.get("/{case_id}")
async def get_case_details(case_id: str):
    try:
        case = load_case_by_id(case_id)
        d = case.model_dump()
        d["dispute_id"] = d.get("case_id")
        d["category"] = d.get("dispute_category")
        return d
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Case with ID '{case_id}' not found.")



@router.post("")
async def create_custom_case(case_input: DisputeCase):
    from data.generate_cases import CASES_DIR
    import json

    case_file = CASES_DIR / f"{case_input.case_id}.json"
    with open(case_file, "w", encoding="utf-8") as f:
        json.dump(case_input.model_dump(), f, indent=2)

    return {
        "status": "created",
        "case_id": case_input.case_id,
        "case": case_input.model_dump(),
    }


