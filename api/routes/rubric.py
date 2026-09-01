"""GET /api/rubric — retrieve rubric criteria and reason code mappings."""

from __future__ import annotations
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query

from rubric.rubric_loader import RubricLoader

router = APIRouter(prefix="/api/rubric", tags=["rubric"])
_rubric_loader = RubricLoader()


@router.get("")
async def get_rubric():
    """Return the entire evidence evaluation rubric."""
    return _rubric_loader.rubric.model_dump()


@router.get("/categories")
async def list_categories():
    """Return all categories with metadata."""
    categories = _rubric_loader.list_categories()
    summary = []
    for cat_id in categories:
        cat_obj = _rubric_loader.get_category(cat_id)
        if cat_obj:
            summary.append({
                "category_id": cat_obj.category_id,
                "title": cat_obj.title,
                "description": cat_obj.description,
                "reason_codes": cat_obj.reason_codes,
                "evidence_count": len(cat_obj.required_evidence),
                "abstention_triggers_count": len(cat_obj.abstention_triggers),
            })
    return {"categories": summary}


@router.get("/{category_or_code}")
async def get_category_or_reason_code(category_or_code: str):
    """Retrieve category rubric by category_id or reason code."""
    # First check if direct category_id
    cat = _rubric_loader.get_category(category_or_code)
    if cat:
        return cat.model_dump()

    # Otherwise lookup by reason code
    cat = _rubric_loader.get_category_for_reason_code(category_or_code)
    if cat:
        return cat.model_dump()

    raise HTTPException(
        status_code=404,
        detail=f"No rubric category found matching '{category_or_code}'.",
    )

