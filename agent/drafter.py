"""LLM-powered response letter drafter.

Given scored evidence and the rubric excerpt, drafts a professional
dispute-response letter citing ONLY facts present in the case data.
The LLM is never given raw evidence — only the scorer's validated output.

Implemented in Phase 3.
"""

from __future__ import annotations
