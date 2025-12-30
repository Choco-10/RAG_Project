from fastapi import APIRouter
from pydantic import BaseModel
from app.rag.pipeline import query_rag

router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    session_id: str
    top_k: int = 5

@router.post("/")
async def chat(request: QueryRequest):
    try:
        result = query_rag(
            question=request.query,
            session_id=request.session_id,
            top_k=request.top_k
        )
        return result
    except Exception as e:
        return {"error": str(e)}

