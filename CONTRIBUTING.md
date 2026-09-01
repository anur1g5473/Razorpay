# Contributing to DisputeShield

Thanks for your interest. This section covers how to set up, run, and test the project locally.

## Prerequisites

- **Python 3.11+** (tested on 3.14)
- **Node.js 20+** (for the web UI)
- **Git**

## Quick Start

```bash
# 1. Clone
git clone https://github.com/anur1g5473/Razorpay.git
cd Razorpay

# 2. Python setup
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
pip install -r requirements.txt

# 3. Environment variables
cp .env.example .env
# Edit .env with your GEMINI_API_KEY (or use omniroute for local)

# 4. Verify everything works
python -m agent --help         # CLI
pytest --tb=short -q           # Tests
uvicorn api.main:app --port 8000  # API server

# 5. Web UI
cd web
npm install
npm run dev                    # → http://localhost:3000
```

## Project Layout

| Directory | Purpose |
|-----------|---------|
| `agent/`  | Core pipeline — retrieval, scoring, drafting, orchestration |
| `api/`    | FastAPI REST layer wrapping the agent |
| `data/`   | Synthetic dispute cases (JSON) + generator script |
| `eval/`   | Evaluation harness — precision, recall, false-positive cost |
| `rubric/` | Evidence rubric definitions per dispute reason code |
| `tests/`  | pytest test suite |
| `web/`    | Next.js frontend |
| `notes/`  | Working notes — decisions, TODOs |

## Running Tests

```bash
# All tests
pytest

# Specific module
pytest tests/test_rubric.py -v

# With coverage (if installed)
pytest --cov=agent --cov=eval
```

## Code Style

We use [Ruff](https://docs.astral.sh/ruff/) for linting and formatting:

```bash
ruff check .          # Lint
ruff format .         # Format
```

## Branch Workflow

Each feature is built on its own branch (`phase/N-name`) and merged to `main` only when fully tested:

```
main ← phase/0-skeleton ← phase/1-rubric ← phase/2-dataset ← ...
```
