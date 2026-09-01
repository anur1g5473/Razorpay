"""Retriever tool functions for the agent pipeline.

Each function simulates a distinct "tool call" the LLM would make to fetch
one slice of case data.  This keeps the design modular (no mega-prompt) and
mirrors how a real production agent would work against live APIs.

Implemented in Phase 3.
"""

from __future__ import annotations
