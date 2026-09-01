"""Full agent pipeline orchestrator.

Coordinates the five-step flow:
  1. Retrieve — fetch case data via tool calls
  2. Score   — deterministic rubric-based evidence scoring
  3. Decide  — contest / accept / flag (abstain)
  4. Draft   — LLM-generated response letter (only if contesting)
  5. Output  — structured result with confidence + rationale

Implemented in Phase 3.
"""

from __future__ import annotations
