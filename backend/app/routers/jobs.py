from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/jobs", tags=["jobs"])

embedding_service = None
retrieval_service = None


def init_services(embedding, retrieval):
    global embedding_service, retrieval_service
    embedding_service = embedding
    retrieval_service = retrieval


class JobSearchRequest(BaseModel):
    query: str
    top_k: int = 10


@router.post("/search")
async def search_jobs(request: JobSearchRequest):
    """
    Semantic job search.
    Find jobs matching a text query.
    """
    if len(request.query) < 5:
        raise HTTPException(
            status_code=400,
            detail="Query too short"
        )

    # Encode query
    embedding = embedding_service.embed(request.query)

    # Search Qdrant
    jobs = retrieval_service.search(
        query_vector=embedding,
        top_k=request.top_k,
    )

    return {
        "status": "success",
        "query": request.query,
        "total_results": len(jobs),
        "jobs": jobs,
    }