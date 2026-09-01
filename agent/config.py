"""LLM provider configuration for DisputeShield.

Supports two providers:
 • gemini   — Google Gemini via the google-genai SDK.
 • omniroute — Any OpenAI-compatible endpoint (local OmniRoute at localhost:20128).

Set the active provider via the LLM_PROVIDER env-var or by calling
``get_llm_client()`` directly.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class LLMConfig:
    """Immutable configuration for a single LLM provider."""

    provider: str
    api_key: str
    base_url: str | None = None
    model: str | None = None


def _gemini_config() -> LLMConfig:
    return LLMConfig(
        provider="gemini",
        api_key=os.getenv("GEMINI_API_KEY", ""),
        model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
    )


def _omniroute_config() -> LLMConfig:
    return LLMConfig(
        provider="omniroute",
        api_key=os.getenv("OMNIROUTE_API_KEY", "not-needed"),
        base_url=os.getenv("OMNIROUTE_BASE_URL", "http://localhost:20128/v1"),
        model=os.getenv("OMNIROUTE_MODEL", "default"),
    )


def get_llm_config(provider: str | None = None) -> LLMConfig:
    """Return the LLM configuration for *provider* (defaults to env-var ``LLM_PROVIDER``)."""
    provider = provider or os.getenv("LLM_PROVIDER", "gemini")
    factories = {
        "gemini": _gemini_config,
        "omniroute": _omniroute_config,
    }
    if provider not in factories:
        raise ValueError(
            f"Unknown LLM provider '{provider}'. Choose from: {sorted(factories)}"
        )
    return factories[provider]()


def get_openai_client(config: LLMConfig | None = None):
    """Return an ``openai.OpenAI`` client pointed at the configured provider.

    Both Gemini (via its OpenAI-compatible endpoint) and OmniRoute expose
    the ``/v1/chat/completions`` interface, so a single client works for both.
    """
    from openai import OpenAI

    if config is None:
        config = get_llm_config()

    if config.provider == "gemini":
        return OpenAI(
            api_key=config.api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        )

    # omniroute / any OpenAI-compatible endpoint
    return OpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
    )
