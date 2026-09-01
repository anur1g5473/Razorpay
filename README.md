# DisputeShield

**AI-powered chargeback evidence responder — evaluates dispute evidence, drafts response letters, and honestly reports which fights are worth having.**

> Built for [Razorpay AI Buildathon 2026](https://razorpay.com/buildathon/) — Track 02: AI Risk Manager

---

## The Problem

When a customer disputes a payment, the bank asks the merchant: _"Prove this transaction was legitimate, or we're reversing the money."_ Merchants — especially small ones — respond badly, generically, or not at all, and **lose money they could have kept** had they assembled the right evidence in the right format.

## What DisputeShield Does

Feed it one disputed transaction, and it:

1. **Retrieves** the relevant evidence (delivery proof, billing, customer communications)
2. **Scores** each piece of evidence against a reason-code-specific rubric (deterministic — no LLM)
3. **Decides** whether to contest, flag for review, or accept the dispute
4. **Drafts** a professional response letter citing only verified facts (LLM-assisted)
5. **Honestly abstains** when evidence is missing or contradictory — instead of guessing

## Architecture

```
 Retrieve (tools) → Score (rubric) → Decide → Draft (LLM) → Output
      ↑                   ↑                        ↑
  Case Data          Evidence Rubric         Gemini / OmniRoute
   (JSON)              (JSON)                  (LLM API)
```

The scoring step is **purely deterministic** — no LLM involved. Same input always produces the same score. The LLM is used *only* for drafting the response letter, and it only receives evidence the scorer already validated. **It can never invent evidence.**

→ [Full architecture deep-dive](ARCHITECTURE.md)

## Metrics

> _To be populated after Phase 4 evaluation run._

| Metric | Value |
|--------|-------|
| Precision | _TBD_ |
| Recall | _TBD_ |
| F1 Score | _TBD_ |
| False Positive Rate | _TBD_ |
| Abstention Accuracy | _TBD_ |
| Dataset Size | 100 synthetic cases |

## Graceful Failure Example

> _To be populated after Phase 3 — a specific case where the system correctly abstains due to missing or contradictory evidence._

## Quick Start

```bash
# Clone
git clone https://github.com/anur1g5473/Razorpay.git
cd Razorpay

# Python setup
python -m venv venv
venv\Scripts\activate            # Windows
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your GEMINI_API_KEY to .env

# Run
python -m agent --help           # CLI
python -m agent analyze CASE_001 # Analyze one case
python -m agent eval             # Full evaluation

# API server
uvicorn api.main:app --port 8000

# Web UI
cd web && npm install && npm run dev
```

→ [Full setup guide](CONTRIBUTING.md)

## Project Structure

```
agent/    Core pipeline — retrieval, scoring, drafting, orchestration
api/      FastAPI REST layer
data/     100 synthetic dispute cases (JSON)
eval/     Evaluation harness — precision, recall, false-positive cost
rubric/   Evidence rubric per Razorpay dispute reason code
tests/    pytest test suite
web/      Next.js dashboard
```

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Core | Python, deterministic rubric-based scoring |
| LLM | Google Gemini + OmniRoute (OpenAI-compatible, dual provider) |
| API | FastAPI |
| Frontend | Next.js, Tailwind CSS, shadcn/ui |
| Testing | pytest, GitHub Actions CI |

## Constraints (by design)

- **No real customer data** — synthetic only.
- **Never fabricates evidence** — the LLM only cites facts validated by the deterministic scorer.
- **Strictly defense-only** — nothing in this codebase helps anyone commit chargeback fraud.
- **Honest metrics** — false-positive cost is reported, not hidden.

## License

MIT — see [LICENSE](LICENSE).
