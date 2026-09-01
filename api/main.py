"""FastAPI application for DisputeShield.

Exposes the agent pipeline over HTTP so the Next.js frontend can call it.
Run with:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="DisputeShield API",
    version="0.1.0",
    description="AI-powered chargeback evidence responder — REST API.",
)

# Allow the Next.js dev server and production origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "DisputeShield API",
        "version": "0.1.0",
        "status": "ok",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Route modules will be included here in Phase 5:
# from api.routes import analyze, cases, eval_routes, rubric
# app.include_router(analyze.router)
# app.include_router(cases.router)
# app.include_router(eval_routes.router)
# app.include_router(rubric.router)
