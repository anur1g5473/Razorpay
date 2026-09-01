"""System prompts and few-shot examples for the LLM drafter.

All prompts enforce the core safety constraint: the LLM must NEVER invent
evidence that is not present in the scored input.  It can only cite, quote,
and organise facts the deterministic scorer already validated.

Implemented in Phase 3.
"""

from __future__ import annotations
