"""Deterministic evidence scorer.

Scores each evidence field against the rubric for the given dispute reason
code.  No LLM involved — purely rule-based so results are reproducible and
explainable.

Implemented in Phase 3.
"""

from __future__ import annotations
