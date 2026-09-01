# Architecture

> System design deep-dive. For a quick overview, see the [README](README.md).

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         Web UI (Next.js)                         │
│  Dashboard · Analyze · Evaluation · Architecture · 404 / 500    │
└──────────────────────────┬───────────────────────────────────────┘
                           │ HTTP (REST)
┌──────────────────────────▼───────────────────────────────────────┐
│                       API Layer (FastAPI)                         │
│  /api/analyze · /api/cases · /api/eval · /api/rubric · /health  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ Python calls
┌──────────────────────────▼───────────────────────────────────────┐
│                     Agent Pipeline (agent/)                       │
│                                                                  │
│  ┌──────────┐  ┌─────────┐  ┌────────┐  ┌───────┐  ┌────────┐  │
│  │ Retrieve │→ │  Score  │→ │ Decide │→ │ Draft │→ │ Output │  │
│  │ (tools)  │  │(rubric) │  │        │  │ (LLM) │  │        │  │
│  └──────────┘  └─────────┘  └────────┘  └───────┘  └────────┘  │
│       ↑              ↑                       ↑                   │
│       │              │                       │                   │
│  ┌────┴────┐   ┌─────┴─────┐          ┌─────┴──────┐            │
│  │ Case    │   │ Evidence  │          │ Gemini /   │            │
│  │ Data    │   │ Rubric    │          │ OmniRoute  │            │
│  │ (JSON)  │   │ (JSON)    │          │ (LLM API)  │            │
│  └─────────┘   └───────────┘          └────────────┘            │
└──────────────────────────────────────────────────────────────────┘
```

## Pipeline Steps (Detail)

### Step 1: Retrieve

The agent calls discrete tool functions — one per data type — to fetch case information. This mirrors how a production agent would call real APIs (Razorpay Disputes API, shipping provider API, CRM) rather than receiving all data in a single prompt.

**Tools:**
- `get_dispute_info(case_id)` → dispute details (reason code, amount, phase)
- `get_order_details(case_id)` → order/transaction info
- `get_delivery_status(case_id)` → shipping/fulfillment evidence
- `get_customer_comms(case_id)` → communication log excerpts

### Step 2: Score (Deterministic — No LLM)

Each evidence field is scored against the rubric for the dispute's reason code. The rubric defines explicit criteria for what constitutes strong, moderate, or weak evidence.

**Key design choice:** This step is *purely deterministic*. Same input → same score, every time. No LLM involved. This makes scores:
- Reproducible
- Explainable (traceable to specific rubric rules)
- Auditable

**Output:** Per-field scores + weighted aggregate score (0.0 – 1.0).

### Step 3: Decide

Maps the aggregate score to a recommendation:
- **Contest** (score ≥ 0.60) → proceed to draft a response letter
- **Flag** (0.35 ≤ score < 0.60) → low confidence, recommend human review
- **Accept** (score < 0.35 OR any critical evidence missing) → don't contest

**Abstention logic:** If critical evidence for the dispute type is missing OR evidence is contradictory, the system abstains regardless of the score. This is the "honest about which fights are worth having" promise.

### Step 4: Draft (LLM)

Only invoked when the decision is Contest or Flag. The LLM receives:
- The scorer's structured output (validated evidence only)
- The rubric excerpt for this reason code
- A strict system prompt forbidding evidence invention

It produces a professional dispute-response letter citing only facts present in the data.

### Step 5: Output

Structured result combining:
- Recommendation: `contest` | `accept` | `flag`
- Confidence: probability (0.0–1.0) + tier label (strong/moderate/weak)
- Evidence breakdown: per-field scores and status
- Response letter (if applicable)
- Rationale: human-readable explanation referencing specific evidence

## Evidence Rubric

The rubric is the source of truth — a structured JSON file defining per-reason-code criteria. See [`rubric/evidence_rubric.json`](rubric/evidence_rubric.json).

Each reason code entry specifies:
- **Critical evidence** (must-have; if missing → abstain)
- **Supporting evidence** (strengthens the case)
- **Bonus evidence** (extra weight if present)
- **Strong/moderate/weak thresholds** for each evidence type
- **Scoring weights** per field

## Evaluation

The eval harness (`eval/harness.py`) runs the full pipeline over all 100 synthetic cases and computes:
- **Precision:** Of cases we said "contest," how many were actually should-win?
- **Recall:** Of should-win cases, how many did we correctly recommend contesting?
- **False-Positive Cost:** Cases where we said "contest" on a should-lose case (the expensive error)
- **Abstention Accuracy:** When we abstained, was it genuinely ambiguous or should-lose?

## Tech Stack

| Layer | Technology | Why |
|-------|-----------|-----|
| Agent Core | Python 3.11+ | The pipeline, scoring, and orchestration |
| LLM | Gemini / OmniRoute | Letter drafting (via OpenAI-compatible SDK) |
| API | FastAPI | REST layer for the web UI |
| Frontend | Next.js + Tailwind + shadcn/ui | Professional, responsive dashboard |
| Data | JSON files | Simple, portable, no database needed |
| Testing | pytest | Unit + integration tests |
| CI | GitHub Actions | Lint + test on every push |
