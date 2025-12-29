from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.pipeline import query_rag

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/")
async def chat(request: QueryRequest):
    relevant_chunks = query_rag(request.query, top_k=request.top_k)
    return {
        "query": request.query,
        "relevant_chunks": relevant_chunks
    }
