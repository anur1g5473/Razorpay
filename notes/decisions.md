# Architectural Decisions

> Key technical choices and why we made them. Updated as we build.

---

## ADR-001: Deterministic scoring, LLM only for drafting

**Context:** The agent needs to evaluate evidence and produce a confidence score. Using an LLM for scoring would make results non-reproducible and hard to explain to a bank or merchant.

**Decision:** Evidence scoring is purely deterministic (rubric-based rules). The LLM is used *only* for drafting the human-readable response letter — and it receives only the scorer's validated output, never raw case data.

**Consequences:**
- ✅ Scores are reproducible across runs — same input always gives same score.
- ✅ Every score can be traced back to specific rubric criteria — fully explainable.
- ✅ False positives are attributable to rubric design, not LLM hallucination.
- ⚠️ The rubric must be comprehensive enough to cover edge cases the LLM might catch intuitively.

---

## ADR-002: Dual LLM provider (Gemini + OmniRoute)

**Context:** We need an LLM for letter drafting. Gemini is the primary choice for quality; OmniRoute (localhost:20128) provides a local fallback for offline development and cost savings.

**Decision:** Both providers expose an OpenAI-compatible `/v1/chat/completions` endpoint. We use the `openai` Python SDK pointed at whichever endpoint is active. Switching is a single env-var change.

**Consequences:**
- ✅ No vendor lock-in — can switch models without code changes.
- ✅ Development works offline via OmniRoute.
- ⚠️ Must test with both providers to ensure prompt compatibility.

---

## ADR-003: Synthetic case design mirrors Razorpay's real dispute entity

**Context:** We can't use real transaction data. Our synthetic cases need to be realistic enough that the system's performance is meaningful.

**Decision:** Case JSON schema mirrors Razorpay's actual dispute API entity (reason codes, evidence fields like `shipping_proof`, `billing_proof`, `customer_communication`, etc.) enriched with order details.

**Consequences:**
- ✅ Demonstrates domain knowledge to judges/interviewers.
- ✅ System could conceptually work against real Razorpay disputes with minimal changes.
- ⚠️ Some real-world evidence types (scanned PDFs, photos) are represented as structured data, not actual documents.

---

*More decisions will be documented as we build.*
