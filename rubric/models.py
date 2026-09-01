"""Pydantic schemas and models for DisputeShield Evidence Rubric."""

from __future__ import annotations
from typing import List, Dict, Optional, Literal
from pydantic import BaseModel, Field


class EvidenceItem(BaseModel):
    item_id: str = Field(..., description="Unique identifier for evidence type")
    name: str = Field(..., description="Human readable evidence item name")
    weight: float = Field(..., ge=0.0, le=100.0, description="Evidence item weight in score computation")
    compelling_level: Literal["critical", "important", "supporting"] = Field(
        ..., description="Compelling level of the evidence"
    )
    required_fields: List[str] = Field(default_factory=list, description="Mandatory metadata fields")
    strong_evidence_indicators: List[str] = Field(
        default_factory=list, description="Conditions that award maximum confidence points"
    )
    weak_evidence_indicators: List[str] = Field(
        default_factory=list, description="Conditions that degrade score or invalidate evidence"
    )


class WinProbabilityThresholds(BaseModel):
    high: float = Field(default=0.75, ge=0.0, le=1.0)
    medium: float = Field(default=0.45, ge=0.0, le=1.0)


class DisputeCategoryRubric(BaseModel):
    category_id: str = Field(..., description="Unique category slug")
    title: str = Field(..., description="Category display title")
    description: str = Field(..., description="Category description and dispute context")
    reason_codes: List[str] = Field(..., description="List of card network & UPI reason codes")
    required_evidence: List[EvidenceItem] = Field(..., description="List of required evidence items")
    abstention_triggers: List[str] = Field(default_factory=list, description="Conditions triggering mandatory human review")
    win_probability_thresholds: WinProbabilityThresholds = Field(
        default_factory=WinProbabilityThresholds, description="Probability thresholds"
    )


class EvidenceRubric(BaseModel):
    version: str = "1.0.0"
    last_updated: str = "2026-09-01"
    description: str = "DisputeShield Evidence Evaluation Rubric"
    categories: Dict[str, DisputeCategoryRubric] = Field(..., description="Mapping of category_id to category rubric")
