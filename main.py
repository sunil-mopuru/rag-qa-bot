"""
FastAPI Application
REST API for Q&A Support Bot
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
from config import settings
from rag_pipeline import RAGPipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RAG Q&A Support Bot API",
    description="API for answering questions using Retrieval Augmented Generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
try:
    rag_pipeline = RAGPipeline(
        api_key=settings.openai_api_key,
        db_path=settings.chroma_db_path,
        collection_name=settings.collection_name,
        embedding_model=settings.embedding_model,
        llm_model=settings.llm_model,
        max_tokens=settings.max_tokens,
        temperature=settings.temperature,
        top_k=settings.top_k_results,
        use_ollama=settings.use_ollama,
        ollama_model=settings.ollama_model
    )
    logger.info("RAG pipeline initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
    rag_pipeline = None


# Request/Response Models
class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str
    top_k: Optional[int] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "How do I reset my password?",
                "top_k": 3
            }
        }


class Source(BaseModel):
    """Source document model"""
    title: str
    url: str
    snippet: str


class QuestionResponse(BaseModel):
    """Response model for questions"""
    answer: str
    sources: List[Source]
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To reset your password, go to the login page and click...",
                "sources": [
                    {
                        "title": "Password Reset Guide",
                        "url": "https://example.com/help/password-reset",
                        "snippet": "Step 1: Navigate to the login page..."
                    }
                ]
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    vector_db_count: int


# API Endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "RAG Q&A Support Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "ask": "/api/ask"
        }
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        count = rag_pipeline.vector_db.get_collection_count()
        return {
            "status": "healthy",
            "vector_db_count": count
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")


@app.post("/api/ask", response_model=QuestionResponse, tags=["Q&A"])
async def ask_question(request: QuestionRequest):
    """
    Ask a question and get an answer based on the crawled content
    
    Args:
        request: Question request with the question text
        
    Returns:
        Answer with source documents
    """
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    if not request.question or len(request.question.strip()) == 0:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        # Override top_k if provided
        if request.top_k:
            original_top_k = rag_pipeline.top_k
            rag_pipeline.top_k = request.top_k
        
        # Get answer
        result = rag_pipeline.answer_question(request.question)
        
        # Restore original top_k
        if request.top_k:
            rag_pipeline.top_k = original_top_k
        
        return QuestionResponse(
            answer=result['answer'],
            sources=[Source(**source) for source in result['sources']]
        )
        
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")


@app.get("/api/stats", tags=["Statistics"])
async def get_stats():
    """Get statistics about the vector database"""
    if rag_pipeline is None:
        raise HTTPException(status_code=503, detail="RAG pipeline not initialized")
    
    try:
        count = rag_pipeline.vector_db.get_collection_count()
        return {
            "total_documents": count,
            "collection_name": settings.collection_name,
            "embedding_model": settings.embedding_model,
            "llm_model": settings.llm_model
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True
    )
