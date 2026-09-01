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

---

## ADR-004: Abstention Gate Architecture (Hard Rules over Soft Thresholds)

**Context:** Naively relying on soft threshold cuts (e.g. score < 50) for abstention leaves merchants vulnerable when a case has a high total score from minor supporting points, but lacks a critical non-negotiable fact (e.g. 3DS log or courier proof) or has an explicit disqualifier (courier RTO).

**Decision:** The Abstention Gate combines category-specific disqualification triggers with threshold checks. If any hard trigger fires (e.g. RTO status, missing 3DS on high-ticket card transaction, merchant cancellation admission), the recommendation immediately drops to `ABSTAIN` or `FLAG_FOR_REVIEW`, regardless of other supporting evidence points.

**Consequences:**
- ✅ Prevents catastrophic representation fee penalties on disputes with glaring fatal flaws.
- ✅ Protects the merchant's chargeback win ratio with acquiring banks.

---

## ADR-005: Dual Output Paradigm (Continuous Probability + Discrete 3-Tier Categorical Decision)

**Context:** Merchants and risk analysts need both an intuitive action (`CONTEST`, `CONCEDE`/`ABSTAIN`, `HUMAN_REVIEW`) and a granular win probability (0.0% to 100.0%) for portfolio risk analytics.

**Decision:** The engine outputs both a discrete recommendation and a continuous win probability calculated from calibrated rubric thresholds.

---

## ADR-006: Asymmetric Financial Payoff Risk Modeling

**Context:** Standard machine learning optimizes symmetric loss (e.g. standard cross-entropy). In payment disputes, a False Contest (contesting an unwinnable chargeback) costs the disputed amount PLUS network arbitration penalty fees ($15-$50), whereas conceding an unwinnable dispute costs only the disputed amount.

**Decision:** Our evaluation metrics explicitly calculate asymmetric net financial recovery, penalizing false-positive contest recommendations by factoring in representment fines.


*More decisions will be documented as we build.*
