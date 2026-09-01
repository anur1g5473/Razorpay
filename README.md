# DisputeShield — Autonomous Chargeback Evidence Agent

<div align="center">

[![CI](https://github.com/anur1g5473/Razorpay/actions/workflows/ci.yml/badge.svg)](https://github.com/anur1g5473/Razorpay/actions)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-16.3-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tailwind CSS](https://img.shields.io/badge/TailwindCSS-v4.0-38B2AC?logo=tailwind-css)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**AI-powered chargeback evidence responder — evaluates dispute evidence, drafts bank-ready response letters, and honestly reports which fights are worth having.**

*Built for [Razorpay AI Buildathon 2026](https://razorpay.com/buildathon/) — Track 02: AI Risk Manager*

[Architecture Deep Dive](ARCHITECTURE.md) • [Live Dashboard UI](#web-dashboard) • [Benchmark Evaluation](#benchmark-metrics) • [Contributing](CONTRIBUTING.md)

</div>

---

## ⚡ The Problem

When a cardholder files a chargeback, the acquiring bank issues an ultimatum to the merchant:
> *"Prove this transaction was legitimate with compelling evidence, or we reverse the funds and charge a dispute penalty fee."*

Every year, merchants lose **billions of dollars** in winnable chargebacks because:
1. **Evidence Assembly is Slow & Manual:** Gathering 3DS authentication logs, delivery proof, IP coordinates, and customer communication takes hours per ticket.
2. **Blind Contesting Incurs Costly Penalties:** Naively contesting every dispute triggers card network representation fines ($15-$50 per failed dispute) on unwinnable claims.
3. **Generic Response Letters Fail Arbitrations:** Template responses omit the specific evidence indicators demanded by Visa, Mastercard, RuPay, Amex, and UPI dispute rules.

---

## 🛡️ What DisputeShield Does

DisputeShield turns chargeback defense into an automated, mathematically rigorous, and financially optimal pipeline:

1. **Evidence Retrieval:** Ingests transaction metadata, shipping telemetry, 3DS authentication data, customer support tickets, and terms acceptance.
2. **Deterministic Rubric Scoring:** Evaluates evidence against reason-code-specific schemas (covering Visa, Mastercard, RuPay, Amex, UPI, and Razorpay codes) without relying on non-deterministic LLM scoring.
3. **Honest Abstention Gate:** Identifies unwinnable or ambiguous cases (e.g. Courier RTO, promised refunds, missing 3DS) and flags them for human review or concession rather than burning representation fees.
4. **Fact-Grounded Response Drafter:** Uses dual-provider LLMs (Gemini / OpenAI / OmniRoute) to generate structured, compelling representation letters citing **only** validated facts.
5. **Real-Time Financial ROI Optimization:** Evaluates dispute value against representation risk to maximize merchant net recovery.

---

## 🏗️ Architecture

```
┌─────────────────┐       ┌────────────────────────┐       ┌─────────────────────────┐
│ Disputed Case   │ ───►  │ Evidence Retrieval     │ ───►  │ Deterministic Scorer    │
│ Payload (JSON)  │       │ Verification Engine    │       │ (Weight-based Rubric)   │
└─────────────────┘       └────────────────────────┘       └────────────┬────────────┘
                                                                        │
                 ┌──────────────────────────────────────────────────────┴─────────┐
                 ▼                                                                ▼
   ┌───────────────────────────┐                                    ┌───────────────────────────┐
   │ Recommendation Decision   │                                    │ Evidence Score & Breakdown│
   │ CONTEST | ACCEPT | ABSTAIN│                                    │ (0 - 100 Compelling Index)│
   └─────────────┬─────────────┘                                    └─────────────┬─────────────┘
                 │                                                                │
                 └──────────────────────────────┬─────────────────────────────────┘
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Fact-Grounded Response Drafter  │
                               │ (Gemini 2.5 / OmniRoute / LLM)  │
                               └────────────────┬────────────────┘
                                                ▼
                               ┌─────────────────────────────────┐
                               │ Bank-Ready Defense Package      │
                               │ (Letter, Citations, Audit Log)  │
                               └─────────────────────────────────┘
```

### Core Design Invariants

- **Zero Evidence Fabrication:** The LLM drafter receives strictly pre-filtered, verified evidence items from the deterministic scoring engine. It cannot hallucinate tracking numbers, IP logs, or delivery timestamps.
- **Mathematical Repeatability:** Identical dispute evidence always produces the exact same score and decision across runs.
- **Strictly Defense-Only:** System prompts and scoring rules operate exclusively to defend merchants against invalid claims.


## 📊 Benchmark Evaluation Metrics

Evaluated against a synthetic dataset of **100 diverse dispute scenarios** spanning 6 major card network and UPI reason-code categories:

| Metric | DisputeShield Benchmark | Target Threshold | Status |
|---|---|---|---|
| **Overall Recommendation Accuracy** | **90.0%** | > 85.0% | ✅ **PASS** |
| **Contest Recall** | **100.0%** | > 85.0% | ✅ **PASS** (Zero winnable chargebacks missed) |
| **Contest Precision** | **80.0%** | > 75.0% | ✅ **PASS** |
| **Macro F1 Score** | **0.8519** | > 0.8500 | ✅ **PASS** |
| **P95 Latency** | **0.11 ms** | < 250 ms | ✅ **PASS** |

### 💰 Financial Cost & ROI Analysis

```
Total Disputed Volume:              INR 1,130,765.93
Direct Recovered Volume:            INR   360,702.22  (100.0% winnable volume recovered)
Prevented Representation Penalties: INR    60,000.00  (40 unwinnable cases conceded)
Net Financial Gain:                 INR   413,202.22
Net Savings vs Blind Auto-Contest:  INR    52,500.00
```

### 📈 Category Breakdown

| Dispute Category | Total Cases | Accuracy | Macro F1 | Net Financial Gain |
|---|---|---|---|---|
| **Fraudulent / Unauthorized (10.4, 4837, UPI-01)** | 20 | 100.0% | 1.0000 | INR 107,057.33 |
| **Product Not Received (13.1, 4855, UPI-02)** | 20 | 80.0% | 0.6000 | INR 74,734.48 |
| **Product Defective / Not Described (13.3, 4853)** | 16 | 100.0% | 1.0000 | INR 88,750.00 |
| **Credit / Refund Not Processed (13.6, 4860)** | 16 | 75.0% | 0.5833 | INR 72,902.69 |
| **Duplicate / Incorrect Amount (12.6, 4834)** | 14 | 85.7% | 0.6190 | INR 46,263.72 |
| **Subscription / Recurring Cancelled (13.7, 4841)**| 14 | 100.0% | 1.0000 | INR 23,494.00 |

---

## 🚫 Graceful Failure & Honest Abstention

A key requirement of production AI risk systems is knowing **when not to act**. DisputeShield enforces deterministic abstention triggers when evidence is ambiguous or contradictory:

```json
{
  "case_id": "CASE_007",
  "category": "product_service_not_received",
  "disputed_amount": 8450.00,
  "recommendation": "flag_for_review",
  "score": 45.0,
  "abstention_triggered": true,
  "abstention_reason": "Courier tracking confirms package was returned to sender (RTO), but customer support logs indicate reshipment in transit.",
  "action": "Route to Human Risk Analyst — Do not submit automated representation."
}
```

*By abstaining on ambiguous disputes instead of blindly submitting ungrounded letters, DisputeShield protects merchants against costly dispute penalty fees.*

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Agent Core & Scorer** | Python 3.11+, Pydantic v2, Deterministic Rubric Engine |
| **LLM & AI Reasoning** | Google Gemini (`gemini-2.5-flash`) + OmniRoute / OpenAI API |
| **API & Backend** | FastAPI, Uvicorn, Python Dotenv |
| **Web Dashboard** | Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Lucide Icons |
| **Evaluation & Testing**| Pytest, Custom Evaluation Harness, GitHub Actions CI/CD |

---

## 🚀 Quick Start

### 1. Clone & Setup Python Environment

```bash
git clone https://github.com/anur1g5473/Razorpay.git
cd Razorpay

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys

```bash
cp .env.example .env
```

Edit `.env` and set your preferred LLM provider:
```ini
LLM_PROVIDER=gemini              # options: gemini | openai | mock
GEMINI_API_KEY=your_gemini_api_key_here
OMNIR_API_KEY=your_omniroute_api_key_here
OMNIR_BASE_URL=https://api.omniroute.ai/v1
```

### 3. CLI Commands

```bash
# Display CLI help
python -m agent --help

# Analyze a single dispute scenario
python -m agent analyze CASE_001

# Execute 100-case benchmark evaluation
python -m agent eval

# Regenerate benchmark synthetic cases
python -m agent generate-cases --count 100
```

### 4. Run API Server

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Interactive OpenAPI Swagger UI will be available at: `http://localhost:8000/docs`

### 5. Launch Web Dashboard

```bash
cd web
npm install
npm run dev
```

Visit the dashboard at: `http://localhost:3000`

---

## 🖥️ Web Dashboard

The DisputeShield web interface features four modules:

1. **⚡ Live Dispute Analyzer:** Real-time evidence score meter, category rubric compliance check, compelling indicator badges, and AI-drafted bank representation letter.
2. **📁 Case Repository:** Interactive filterable dataset of 100 synthetic disputes covering all reason codes.
3. **📊 Benchmark Evaluator:** Run full evaluation test suites, visualize confusion matrices, and review net financial gain calculations.
4. **📖 Rubric Explorer:** Inspect evidence weighting, critical indicators, and mandatory abstention triggers across all reason codes.

---

## 📡 REST API Reference

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/analyze` | Ingest dispute JSON, run deterministic score, draft response |
| `GET` | `/api/v1/cases` | List all synthetic cases with metadata & ground truth |
| `GET` | `/api/v1/cases/{case_id}` | Retrieve specific case payload and evidence history |
| `POST` | `/api/v1/eval` | Trigger evaluation run against benchmark dataset |
| `GET` | `/api/v1/rubric` | Retrieve the active evidence scoring rubric |
| `GET` | `/health` | Backend health & provider availability |

---

## 🧪 Testing

```bash
# Run test suite
pytest --tb=short -q
```

Our tests validate:
- Rubric schema validity & completeness across all 6 categories
- Deterministic scoring accuracy & weight normalization
- Pipeline execution & LLM drafter fallback behaviors
- FastAPI endpoints & JSON response contracts

---

## 🛡️ Responsible AI & Design Invariants

- **Zero Synthetic Hallucinations:** The drafting agent only cites verified facts validated by the deterministic scoring engine.
- **Strictly Defense-Only:** Designed solely to protect merchants against invalid claims and reduce illegitimate chargeback losses.
- **Auditable & Explainable:** Every score breakdown, indicator checklist, and decision factor is logged with full transparency.

---

## 👥 Authors & Acknowledgments

- **Author:** Anurag ([@anur1g5473](https://github.com/anur1g5473))
- **Event:** Razorpay AI Buildathon 2026 — Track 02: AI Risk Manager

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

