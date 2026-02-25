"""
Entrypoint de la API — Agenda Cultural GC v1.0.

Arrancar con:
    uvicorn api.main:app --reload --port 8000

Swagger UI:
    http://localhost:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes.eventos import router as eventos_router
from api.routes.feeds import router as feeds_router

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Agenda Cultural GC",
    description=(
        "API pública (read-only) de eventos culturales de Gran Canaria. "
        "Sirve datos del pipeline de scraping + IA al frontend Next.js."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# CORS — permisivo para desarrollo local
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",   # Next.js dev
        "http://localhost:3001",   # Static frontend dev
        "http://localhost:5173",   # Vite dev
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET"],         # API read-only
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(eventos_router)
app.include_router(feeds_router)

# ---------------------------------------------------------------------------
# Health-check
# ---------------------------------------------------------------------------


@app.get(
    "/",
    tags=["Health"],
    summary="Health check",
    description="Endpoint de verificación de que la API está viva.",
)
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
