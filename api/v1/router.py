# api/v1/router.py

from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader

from api.v1.models import HackRxRequest, HackRxResponse
from services.rag_pipeline import RAGPipeline
from core.config import settings

# Define router and security scheme
router = APIRouter()
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)

async def verify_token(token: str = Security(api_key_header)):
    """Dependency to verify the bearer token."""
    expected_token = f"Bearer {settings.API_BEARER_TOKEN}"
    if not token or token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token"
        )

@router.post(
    "/hackrx/run",
    response_model=HackRxResponse,
    summary="Run Intelligent Query-Retrieval System",
    description="Processes a document from a URL and answers questions based on its content.",
    dependencies=[Depends(verify_token)]
)
async def run_submission(request: HackRxRequest) -> HackRxResponse:
    """
    This endpoint performs the entire RAG process:
    1. Downloads and processes the document from the provided URL.
    2. Creates a semantic index of the document content.
    3. Answers each question in the list using the indexed document.
    """
    try:
        # Initialize the RAG pipeline for this request
        pipeline = RAGPipeline()

        # Step 1: Load and index the document
        pipeline.setup_pipeline(str(request.documents))

        # Step 2: Run all questions against the indexed document concurrently
        answers = await pipeline.run_queries(request.questions)
        
        return HackRxResponse(answers=answers)

    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Catch-all for any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An internal server error occurred.")