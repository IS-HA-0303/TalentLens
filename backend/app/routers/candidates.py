import fitz  # PyMuPDF
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/candidates", tags=["candidates"])

# Services injected from main.py
ner_service = None
embedding_service = None
retrieval_service = None
ranking_service = None


def init_services(ner, embedding, retrieval, ranking):
    global ner_service, embedding_service, retrieval_service, ranking_service
    ner_service = ner
    embedding_service = embedding
    retrieval_service = retrieval
    ranking_service = ranking


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Could not read PDF: {str(e)}"
        )


class TextMatchRequest(BaseModel):
    text: str
    top_k: int = 10


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload a PDF resume.
    Returns extracted text and detected skills.
    """
    # Validate file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted"
        )

    # Read file
    file_bytes = await file.read()

    # Extract text
    text = extract_text_from_pdf(file_bytes)

    if len(text) < 50:
        raise HTTPException(
            status_code=400,
            detail="Could not extract enough text from PDF"
        )

    # Extract skills
    skills = ner_service.extract_skills(text)

    return {
        "status": "success",
        "filename": file.filename,
        "text_length": len(text),
        "text_preview": text[:500],
        "full_text": text, 
        "skills_extracted": skills,
        "skills_count": len(skills),
    }


@router.post("/match")
async def match_jobs(request: TextMatchRequest):
    """
    Full matching pipeline:
    1. Extract skills from candidate text
    2. Encode to embedding
    3. Retrieve top 100 from Qdrant
    4. Re-rank to top 10
    5. Return results
    """
    if len(request.text) < 20:
        raise HTTPException(
            status_code=400,
            detail="Text too short"
        )

    # Extract skills
    skills = ner_service.extract_skills(request.text)

    # Generate embedding
    embedding = embedding_service.embed(request.text)

    # Retrieve top 100 from Qdrant
    retrieved_jobs = retrieval_service.search(
        query_vector=embedding,
        top_k=100,
    )

    # Re-rank to top K
    ranked_jobs = ranking_service.rerank(
        query_text=request.text,
        jobs=retrieved_jobs,
        top_k=request.top_k,
    )

    return {
        "status": "success",
        "candidate_skills": skills,
        "total_retrieved": len(retrieved_jobs),
        "total_returned": len(ranked_jobs),
        "matches": ranked_jobs,
    }