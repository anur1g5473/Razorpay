# TODO

> What's left to build, in rough priority order.

## Phase 1 — Evidence Rubric
- [x] Write rubric for all 6 dispute categories
- [x] Cover Razorpay reason codes (UPI, Visa, Mastercard, Rupay, Amex, RZP)
- [x] Implement `rubric_loader.py` with query interface
- [x] Schema validation for rubric JSON
- [x] Tests: all reason codes load, strong/weak criteria present


## Phase 2 — Synthetic Dataset
- [ ] Generate 100 cases (40 win / 40 lose / 20 ambiguous)
- [ ] JSON schema for case validation
- [ ] Distribution verification
- [ ] Tests: all cases valid, distribution correct

## Phase 3 — Agent Pipeline
- [ ] Retriever tools (separate tool per data slice)
- [ ] Deterministic evidence scorer
- [ ] Abstention logic (missing/contradictory evidence)
- [ ] LLM response letter drafter
- [ ] Pipeline orchestrator
- [ ] Tests on 10 hand-picked cases

## Phase 4 — Evaluation Harness
- [ ] Run pipeline over all 100 cases
- [ ] Precision, recall, F1 computation
- [ ] False-positive cost analysis
- [ ] Results output (JSON + human-readable summary)

## Phase 5 — API Layer
- [ ] FastAPI routes for analyze, cases, eval, rubric
- [ ] Pydantic response schemas
- [ ] API tests

## Phase 6 — Web UI
- [ ] Next.js scaffold with Tailwind + shadcn/ui
- [ ] Dashboard page with metrics cards
- [ ] Analyze page with step-by-step results
- [ ] Evaluation page with confusion matrix
- [ ] Architecture page with pipeline diagram
- [ ] Custom 404 / 500 pages
- [ ] Info buttons on every section
- [ ] Dark mode, responsive, animations

## Phase 7 — Polish
- [ ] README hero section with real metrics
- [ ] ARCHITECTURE.md deep dive
- [ ] Fresh-clone test
- [ ] Demo video script
