# TODO

> What's left to build, in rough priority order. All phases complete!

## Phase 0 — Project Skeleton
- [x] Repository scaffold and package configurations (`pyproject.toml`, `requirements.txt`)
- [x] Module stubs (`agent`, `api`, `eval`, `rubric`, `data`, `tests`)
- [x] CI/CD workflow (`.github/workflows/ci.yml`)

## Phase 1 — Evidence Rubric
- [x] Write rubric for all 6 dispute categories
- [x] Cover Razorpay reason codes (UPI, Visa, Mastercard, RuPay, Amex, RZP)
- [x] Implement `rubric_loader.py` with query interface
- [x] Schema validation for rubric JSON (`rubric/models.py`)
- [x] Tests: all reason codes load, strong/weak criteria present (12/12 passed)

## Phase 2 — Synthetic Dataset
- [x] Generate 100 cases (40 win / 40 lose / 20 ambiguous distribution)
- [x] JSON schema for case validation (`rubric/models.py` & `data/generate_cases.py`)
- [x] Distribution verification and synthetic metadata generators
- [x] Tests: all cases valid, distribution correct (8/8 passed)

## Phase 3 — Agent Pipeline
- [x] Retriever tools (separate tool per data slice: transaction, order, fulfillment, comms)
- [x] Deterministic evidence scorer (`agent/scorer.py`)
- [x] Abstention logic for missing/contradictory evidence (`rubric/rubric_loader.py` & `agent/scorer.py`)
- [x] LLM response letter drafter (`agent/drafter.py` + `agent/prompts.py`)
- [x] Pipeline orchestrator (`agent/pipeline.py`)
- [x] CLI interface with `analyze`, `eval`, `list`, `generate-cases` subcommands (`agent/__main__.py`)
- [x] Tests on hand-picked cases & pipeline integration (15/15 passed)

## Phase 4 — Evaluation Harness
- [x] Run pipeline over all 100 benchmark cases (`eval/harness.py`)
- [x] Precision, recall, F1 computation (`eval/metrics.py`)
- [x] Asymmetric false-positive cost & ROI analysis
- [x] Results output (`eval/results/eval_report.md` & JSON summaries)
- [x] Eval tests (5/5 passed)

## Phase 5 — API Layer
- [x] FastAPI routes for `/analyze`, `/cases`, `/eval`, `/rubric`
- [x] Pydantic request/response schemas (`api/schemas.py`)
- [x] CORS middleware and error handlers (`api/main.py`)
- [x] API tests with TestClient (16/16 passed)

## Phase 6 — Web UI
- [x] Next.js 16 (App Router) + React 19 + Tailwind CSS v4 scaffold in `web/`
- [x] Dashboard page with metrics cards & category distributions
- [x] Analyze page with live evidence breakdown & rebuttal letter viewer
- [x] Evaluation page with confusion matrix & ROI financial charts
- [x] Architecture page with interactive pipeline flow
- [x] Informational tooltips & explanations for every section
- [x] Dark mode, responsive design, and smooth animations
- [x] Next.js production build verified (`next build` / Turbopack)

## Phase 7 — Polish
- [x] README hero section with real, un-cherry-picked metrics & confusion matrix
- [x] ARCHITECTURE.md deep dive with complete system topology
- [x] 5-minute video demo pitch script (`video.md` and `form.md`)
- [x] Full test suite validation (56/56 pytest tests passing)
- [x] Submission form questionnaire documentation (`form.md`)

