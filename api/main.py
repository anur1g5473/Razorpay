"""FastAPI application for DisputeShield.

Exposes the agent pipeline over HTTP so the Next.js frontend can call it.
Run with:
    uvicorn api.main:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import analyze, cases, eval as eval_routes, rubric

app = FastAPI(
    title="DisputeShield API",
    version="1.0.0",
    description="AI-powered chargeback evidence responder and dynamic rubric evaluation engine.",
)

# Allow Next.js frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "service": "DisputeShield API",
        "version": "1.0.0",
        "status": "ok",
        "docs_url": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Register all routers
app.include_router(cases.router)
app.include_router(analyze.router)
app.include_router(rubric.router)
app.include_router(eval_routes.router)

