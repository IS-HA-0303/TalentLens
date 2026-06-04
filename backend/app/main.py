from fastapi import FastAPI
from contextlib import asynccontextmanager

from backend.app.services.ner_service import NERService
from backend.app.services.embedding_service import EmbeddingService
from backend.app.services.retrieval_service import RetrievalService
from backend.app.services.ranking_service import RankingService
from backend.app.routers import candidates, jobs

# ── Global services ────────────────────────────────────────
# Models are loaded ONCE when server starts and reused for every request
services = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Load all ML models at startup.
    This runs before the server accepts any requests.
    """
    print("\n" + "=" * 50)
    print("TalentLens API — Starting up")
    print("=" * 50)

    # Load all services
    services["ner"] = NERService()
    services["embedding"] = EmbeddingService()
    services["retrieval"] = RetrievalService()
    services["ranking"] = RankingService()

    # Inject services into routers
    candidates.init_services(
        ner=services["ner"],
        embedding=services["embedding"],
        retrieval=services["retrieval"],
        ranking=services["ranking"],
    )
    jobs.init_services(
        embedding=services["embedding"],
        retrieval=services["retrieval"],
    )

    print("\nAll services loaded successfully")
    print("API is ready to accept requests")
    print("=" * 50 + "\n")

    yield  # Server runs here

    # Cleanup on shutdown
    print("Shutting down TalentLens API...")


# ── Create FastAPI app ─────────────────────────────────────
app = FastAPI(
    title="TalentLens API",
    description="AI-powered job-candidate matching system",
    version="1.0.0",
    lifespan=lifespan,
)

# ── Include routers ────────────────────────────────────────
app.include_router(candidates.router)
app.include_router(jobs.router)


# ── Health check ───────────────────────────────────────────
@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "services": list(services.keys()),
        "version": "1.0.0",
    }


@app.get("/")
def root():
    return {
        "message": "TalentLens API",
        "docs": "/docs",
        "health": "/health",
    }